<template>
  <div>
    <h4>Dataset: {{ selectedDataset.datasetName }}</h4>
    <v-select
      v-model="selectedKaiMethod"
      :disabled="!selectedDataset"
      :items="kinaseActivityMethods"
      label="Kinase Activity Inference Method"
      clearable
      @change="onKaiMethodChange();filterKinases()"
    />
    <v-card
      v-if="!!selectedKaiMethod"
      :disabled="!selectedDataset"
      class="pa-2"
      outlined
    >
      <h3 class="text-h7 mb-6">
        Set thresholds:
      </h3>
      <v-container v-if="['ksea', 'ksea_rokai', 'motif', 'kea3_mean', 'kea3_top'].includes(selectedKaiMethod)">
        <v-slider
          v-model="scoreThreshold"
          :max="maxScore"
          min="0"
          thumb-label="always"
          thumb-size="35"
          step="0.1"
          :label="'|Score| ' + (selectedKaiMethod.startsWith('kea3') ? '<=' : '>=')"
          style="font-style: italic"
          @change="filterKinases"
        />
      </v-container>

      <v-container v-if="['ksea', 'ksea_rokai', 'motif', 'kstar'].includes(selectedKaiMethod)">
        <v-slider
          v-model="significanceThreshold"
          :max="maxSignificance"
          min="0"
          thumb-label="always"
          thumb-size="35"
          step="0.1"
          label="-log10(pval) >="
          style="font-style: italic"
          @change="filterKinases"
        />
      </v-container>
      <v-alert
        v-if="selectedKaiMethod.startsWith('kea3')"
        color="blue-grey"
        text
        icon="mdi-exclamation"
        class="mt-4 mr-4 pa-4"
        prominent
      >
        Caveat: For KEA3, lower scores mean stronger enrichment!
      </v-alert>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'TheKinaseActivityThresholder',
  props: {
    dataIn: {
      type: Object,
      default: () => {
      }
    },
    selectedDataset: {
      type: Object,
      default: () => {
      }
    }
  },
  data: () => ({
    selectedKaiMethod: undefined,
    selectedKaiResults: [],
    scoreThreshold: 0,
    significanceThreshold: 0,
    maxScore: 10,
    maxSignificance: 10
  }),
  computed: {
    kinaseActivityMethods () {
      const methodList = [
        { text: 'KSEA', value: 'ksea' },
        { text: 'RoKAI+KSEA', value: 'ksea_rokai' },
        { text: 'Motif Enrichment', value: 'motif' },
        { text: 'KEA3 - Mean Rank', value: 'kea3_mean' },
        { text: 'KEA3 - Top Rank', value: 'kea3_top' },
        { text: 'KSTAR', value: 'kstar' }
      ]
      if (this.selectedDataset) {
        return methodList
          .map(method => {
            return {
              ...method,
              disabled: !this.dataIn[method.value] || this.dataIn[method.value].length === 0
            }
          })
      } else {
        return []
      }
    }
  },
  watch: {
    selectedDataset: {
      immediate: true,
      handler () {
        this.onKaiMethodChange()
        this.filterKinases()
      }
    }
  },
  methods: {
    onKaiMethodChange () {
      if (!!this.selectedDataset && !!this.selectedKaiMethod) {
        // Convert results of selected method into generic format
        const colnames = Object.keys(this.dataIn[this.selectedKaiMethod][0])
        let kinaseColname
        let scoreColname
        let pvalColname
        switch (this.selectedKaiMethod) {
          case 'ksea':
          case 'ksea_rokai':
            kinaseColname = 'Gene'
            scoreColname = colnames.filter(name => name.startsWith('Score'))[0]
            pvalColname = colnames.filter(name => name.startsWith('adj p-val'))[0]
            break
          case 'motif':
            kinaseColname = 'Kinase'
            scoreColname = colnames.filter(name => name.startsWith('Log2 Enrichment'))[0]
            pvalColname = colnames.filter(name => name.startsWith('-Log10 p_value adjusted'))[0]
            break
          case 'kea3_mean':
          case 'kea3_top':
            kinaseColname = 'TF'
            scoreColname = 'Score'
            break
          case 'kstar':
            kinaseColname = 'Kinase'
            pvalColname = colnames[1]
        }

        this.selectedKaiResults = this.dataIn[this.selectedKaiMethod].map(datum => {
          const res = {}
          res.Kinase = datum[kinaseColname]
          if (scoreColname) {
            res.Score = datum[scoreColname]
          }
          if (pvalColname) {
            // Log transform those who aren't
            if (['ksea', 'ksea_rokai'].includes(this.selectedKaiMethod)) {
              res.Significance = datum[pvalColname] !== 0 ? -Math.log10(datum[pvalColname]) : -Math.log10(Number.MIN_VALUE)
            } else {
              res.Significance = datum[pvalColname]
            }
          }
          return res
        })

        this.maxScore = Math.max(...this.selectedKaiResults.map(datum => Math.abs(datum.Score || 0)))
        this.maxSignificance = Math.max(...this.selectedKaiResults.map(datum => datum.Significance || 0))

        // Hack for KSTAR: For some reason, many (all?) entries in KSTAR results are duplicated, so each kinase gets two scores.
        // Here we reduce this to only retain the absolute maximum value.
        // Props to ChatGPT for this beautiful use case for reduce <3
        if (this.selectedKaiMethod === 'kstar') {
          this.selectedKaiResults = Object.values(
            this.selectedKaiResults.reduce((acc, item) => {
              const { Kinase, Significance } = item
              // Check if this Kinase is already in the accumulator and compare Significance
              if (!acc[Kinase] || Math.abs(Significance) > Math.abs(acc[Kinase].Significance)) {
                acc[Kinase] = item
              }
              return acc
            }, {})
          )
        }
      }
    },

    filterKinases () {
      // Apply the thresholds from the sliders
      const perturbedNodes = { up: [], down: [], undirected: [] }
      if (!!this.selectedDataset && !!this.selectedKaiMethod) {
        this.selectedKaiResults
          .filter(kinaseActivityObject => {
            // KEA3 is a special case, since here lower scores mean stronger enrichment
            if (this.selectedKaiMethod.startsWith('kea3')) {
              return kinaseActivityObject.Score <= this.scoreThreshold
            } else {
              // For all others: either the method doesn't return a Score/Signifiance column, or the value needs to be above the threshold
              return (!Object.hasOwn(kinaseActivityObject, 'Score') || Math.abs(kinaseActivityObject.Score) >= this.scoreThreshold) &&
                                (!Object.hasOwn(kinaseActivityObject, 'Significance') || Math.abs(kinaseActivityObject.Significance) >= this.significanceThreshold)
            }
          }).forEach(filteredKinaseActivityObject => {
            // Sort into up, down, and - since KEA3 does not support directions - undirected
            if (['kea3_mean', 'kea3_top'].includes(this.selectedKaiMethod)) {
              perturbedNodes.undirected.push(filteredKinaseActivityObject.Kinase)
            } else if (this.selectedKaiMethod === 'kstar') {
              filteredKinaseActivityObject.Significance < 0
                ? perturbedNodes.down.push(filteredKinaseActivityObject.Kinase)
                : perturbedNodes.up.push(filteredKinaseActivityObject.Kinase)
            } else {
              filteredKinaseActivityObject.Score > 0
                ? perturbedNodes.up.push(filteredKinaseActivityObject.Kinase)
                : perturbedNodes.down.push(filteredKinaseActivityObject.Kinase)
            }
          })
      }
      // Send to PTMNavigator, so it can forward it to biowc-pathwaygraph
      this.$emit('kinase-activities-filtered', perturbedNodes)
    }
  }
}
</script>

<style scoped>

</style>
