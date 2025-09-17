<template>
  <div>
    <h4>Dataset: {{ selectedDataset.datasetName }}</h4>
    <v-select
        v-model="selectedKaiMethod"
        :disabled="!selectedDataset"
        :items="kinaseActivityMethodsFiltered"
        return-object
        item-text="name"
        item-value="short"
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
      <v-container v-if="selectedKaiMethod.kaiDetails.scoreColnamePrefix">
        <v-slider
            v-model="scoreThreshold"
            :max="maxScore"
            min="0"
            thumb-label="always"
            thumb-size="35"
            step="0.1"
            :label="'|Score| ' + (selectedKaiMethod.kaiDetails.higherScoreIsStrongerEnrichment ? '>=' : '<=')"
            style="font-style: italic"
            @change="filterKinases"
        />
      </v-container>

      <v-container v-if="selectedKaiMethod.kaiDetails.significanceColnamePrefix">
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
          v-if="!selectedKaiMethod.kaiDetails.higherScoreIsStrongerEnrichment"
          color="blue-grey"
          text
          icon="mdi-exclamation"
          class="mt-4 mr-4 pa-4"
          prominent
      >
        Caveat: Lower scores mean stronger enrichment!
      </v-alert>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'TheKinaseActivityThresholder',
  props: {
    enrichmentResponse: {
      type: Object,
      default: () => {
      }
    },
    allKinaseActivityMethods: {
      type: Array,
      default: () => []
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
    kinaseActivityMethodsFiltered() {
      if (this.selectedDataset) {
        return this.allKinaseActivityMethods.map(method => {
          return {
            ...method,
            disabled: !this.enrichmentResponse[method.short] || this.enrichmentResponse[method.short].length === 0
          }
        })
      } else {
        return []
      }
    },
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
        const colnames = Object.keys(this.enrichmentResponse[this.selectedKaiMethod.short][0])
        const kinaseColname = this.selectedKaiMethod.kaiDetails.kinaseColname
        const scoreColname = this.selectedKaiMethod.kaiDetails.scoreColnamePrefix
            ? colnames.filter(name => name.startsWith(this.selectedKaiMethod.kaiDetails.scoreColnamePrefix))[0]
            : undefined
        const significanceColname = this.selectedKaiMethod.kaiDetails.significanceColnamePrefix
            ? colnames.filter(name => name.startsWith(this.selectedKaiMethod.kaiDetails.significanceColnamePrefix))[0]
            : undefined


        this.selectedKaiResults = this.enrichmentResponse[this.selectedKaiMethod.short].map(datum => {
          const res = {}
          res.Kinase = datum[kinaseColname]
          if (scoreColname) {
            res.Score = datum[scoreColname]
          }
          if (significanceColname) {
            // Log transform those who aren't
            if (this.selectedKaiMethod.kaiDetails.isAlreadyLogTransformed) {
              res.Significance = datum[significanceColname]
            } else {
              res.Significance = datum[significanceColname] !== 0 ? -Math.log10(datum[significanceColname]) : -Math.log10(Number.MIN_VALUE)
            }
          }
          return res
        })

        this.maxScore = Math.max(...this.selectedKaiResults.map(datum => Math.abs(datum.Score || 0)))
        this.maxSignificance = Math.max(...this.selectedKaiResults.map(datum => datum.Significance || 0))

      }
    },

    filterKinases () {
      // Apply the thresholds from the sliders
      const perturbedNodes = { up: [], down: [], undirected: [] }
      if (!!this.selectedDataset && !!this.selectedKaiMethod) {
        this.selectedKaiResults
          .filter(kinaseActivityObject => {
            if (!this.selectedKaiMethod.kaiDetails.higherScoreIsStrongerEnrichment) {
              return kinaseActivityObject.Score <= this.scoreThreshold
            } else {
              // For all others: either the method doesn't return a Score/Signifiance column, or the value needs to be above the threshold
              return (!Object.hasOwn(kinaseActivityObject, 'Score') || Math.abs(kinaseActivityObject.Score) >= this.scoreThreshold) &&
                  (!Object.hasOwn(kinaseActivityObject, 'Significance') || Math.abs(kinaseActivityObject.Significance) >= this.significanceThreshold)
            }
          }).forEach(filteredKinaseActivityObject => {
            // Sort into up, down, and undirected
          if (this.selectedKaiMethod.kaiDetails.hasDirection) {
            perturbedNodes.undirected.push(filteredKinaseActivityObject.Kinase)
          } else if (this.selectedKaiMethod.kaiDetails.directionFromSignificance) {
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
