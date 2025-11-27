<template>
  <div>
    <v-row
      align="start"
      style="background-color: #ffffff"
      class="mx-0"
    >
      <v-col cols="6">
        <v-select
          v-model="selectedDataset"
          class="px-4"
          :items="datasets"
          item-text="datasetName"
          return-object
          label="Show Enrichment Results for Dataset:"
          clearable
        />
      </v-col>
      <v-col
        v-if="!!enrichmentStatuses && enrichmentStatuses.length>0"
        cols="6"
        class="ma-0"
      >
        <h4>Status of Enrichment Analyses:</h4>
        <v-row
          class="mb-5 mx-0 mt-2"
          style="background-color: #e8e8e8; border-radius: 20pt"
        >
          <v-col
            v-for="(item, index) in enrichmentStatuses"
            :key="index"
            cols="12"
            sm="6"
            md="3"
            class="text-center py-4"
          >
            <div>{{ item.name }}</div>
            <div class="d-flex justify-center mt-0">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <v-icon
                    v-bind="attrs"
                    :color="getEnrichmentStatusIndicator(item.status).color"
                    size="14"
                    class="led-icon"
                    v-on="on"
                  >
                    mdi-circle
                  </v-icon>
                </template>
                <span>{{ getEnrichmentStatusIndicator(item.status).tooltip }}</span>
              </v-tooltip>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <div v-if="selectedDataset">
      <v-tabs

        v-model="peaVsKaiTab"
        height="70"
        background-color="primary"
        dark
        fixed-tabs
      >
        <v-tab
          key="pea"
          class="enrichment-tab"
          href="#pea"
          style="font-size: 12pt"
        >
          Pathway Enrichment
        </v-tab>
        <v-tab
          key="kai"
          class="enrichment-tab"
          href="#kai"
          style="font-size: 12pt"
        >
          Kinase Activity Inference
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="peaVsKaiTab">
        <v-tab-item value="pea">
          <v-tabs
            v-model="pathwayEnrichmentTab"
            fixed-tabs
            dark
          >
            <v-tooltip
                v-for="pathwayEnrichmentType in enrichmentTypes.filter(et => et.enrichmentClass === 'Pathway')"
                :key="pathwayEnrichmentType.short + '-tooltip'"
                top
                color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                    v-bind="attrs"
                    :key="pathwayEnrichmentType.short"
                    class="enrichment-tab"
                    :href="'#' + pathwayEnrichmentType.short"
                    v-on="on"
                >
                  {{ pathwayEnrichmentType.name }}
                </v-tab>
              </template>
              <span v-html="pathwayEnrichmentType.tooltipHtml"></span>
            </v-tooltip>
          </v-tabs>
          <v-tabs-items
              v-model="pathwayEnrichmentTab"
              class="pt-5"
          >
            <v-tab-item
                v-for="pathwayEnrichmentType in enrichmentTypes.filter(et => et.enrichmentClass === 'Pathway')"
                :key="pathwayEnrichmentType.short + '-tabitem'"
                :value="pathwayEnrichmentType.short"
            >
              <v-dialog
                  width="600"
              >
                <template #activator="{ on, attrs }">
                  <v-btn
                      class="ml-2 mb-3"
                      v-bind="attrs"
                      v-on="on"
                  >
                    Show Parameters File
                  </v-btn>
                </template>
                <v-card style="overflow-x: scroll;">
                  <v-card-title class="text-h5 grey lighten-2">
                    {{ pathwayEnrichmentType.name }} Parameters
                  </v-card-title>
                  <v-card-text class="mt-5">
                    <pre>{{pathwayEnrichmentType.parametersHtml}}</pre>
                  </v-card-text>
                </v-card>
              </v-dialog>

              <DxDataGrid
                  v-if="!!selectedDataset && !!enrichmentResponse && !!enrichmentResponse[pathwayEnrichmentType.short] && enrichmentResponse[pathwayEnrichmentType.short].length > 0"
                  :ref="dataGridRefName + '-' + pathwayEnrichmentType.short"
                  :data-source="enrichmentResponse[pathwayEnrichmentType.short]"
                  :show-borders="true"
                  :repaint-changes-only="false"
                  :column-auto-width="true"
                  :allow-column-resizing="true"
                  column-resizing-mode="widget"
                  :allow-column-reordering="true"
                  :scrolling="{ useNative: true }"
                  @initialized="saveGridInstance"
                  @exporting="onExporting"
              >
                <DxFilterRow :visible="true" />
                <DxColumn
                    v-for="key in Object.keys(enrichmentResponse[pathwayEnrichmentType.short][0])"
                    :key="key + '_column'"
                    :width="250"
                    :caption="key"
                    :calculate-cell-value="getValue(key)"
                    :calculate-sort-value="getValueAbsolute(key)"
                    alignment="left"
                    :data-type="pathwayEnrichmentType.stringColumns.some(c => key.startsWith(c)) ? 'string' : 'number' "
                    :sort-order="key.startsWith(pathwayEnrichmentType.sortColumn) ? (pathwayEnrichmentType.sortDesc ? 'desc' : 'asc') : null"
                    :allow-sorting="true"
                    :allow-filtering="true"
                    :format="{formatter: val => key.startsWith('Percent Overlap') ? val + '%' : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                    :show-page-size-selector="true"
                    :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>
          </v-tabs-items>
        </v-tab-item>
        <v-tab-item value="kai">
          <v-tabs
            v-model="kinaseActivityTab"
            dark
          >
            <v-tooltip
                v-for="pathwayEnrichmentType in enrichmentTypes.filter(et => et.enrichmentClass === 'KinaseActivity')"
                :key="pathwayEnrichmentType.short + '-tooltip'"
                top
                color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                    v-bind="attrs"
                    :key="pathwayEnrichmentType.short"
                    class="enrichment-tab"
                    :href="'#' + pathwayEnrichmentType.short"
                    v-on="on"
                >
                  {{ pathwayEnrichmentType.name }}
                </v-tab>
              </template>
              <span v-html="pathwayEnrichmentType.tooltipHtml"></span>
            </v-tooltip>
          </v-tabs>
          <v-tabs-items
            v-model="kinaseActivityTab"
            class="pt-5"
          >
            <v-tab-item
                v-for="pathwayEnrichmentType in enrichmentTypes.filter(et => et.enrichmentClass === 'KinaseActivity')"
                :key="pathwayEnrichmentType.short + '-tabitem'"
                :value="pathwayEnrichmentType.short"
            >
              <v-dialog
                  width="600"
              >
                <template #activator="{ on, attrs }">
                  <v-btn
                      class="ml-2 mb-3"
                      v-bind="attrs"
                      v-on="on"
                  >
                    Show Parameters File
                  </v-btn>
                </template>
                <v-card style="overflow-x: scroll;">
                  <v-card-title class="text-h5 grey lighten-2">
                    {{ pathwayEnrichmentType.name }} Parameters
                  </v-card-title>
                  <v-card-text class="mt-5">
                    <pre>{{pathwayEnrichmentType.parametersHtml}}</pre>
                  </v-card-text>
                </v-card>
              </v-dialog>

              <DxDataGrid
                  v-if="!!selectedDataset && !!enrichmentResponse && !!enrichmentResponse[pathwayEnrichmentType.short] && enrichmentResponse[pathwayEnrichmentType.short].length > 0"
                  :ref="dataGridRefName + '-' + pathwayEnrichmentType.short"
                  :data-source="enrichmentResponse[pathwayEnrichmentType.short]"
                  :show-borders="true"
                  :repaint-changes-only="false"
                  :column-auto-width="true"
                  :allow-column-resizing="true"
                  column-resizing-mode="widget"
                  :allow-column-reordering="true"
                  :scrolling="{ useNative: true }"
                  @initialized="saveGridInstance"
                  @exporting="onExporting"
              >
                <DxFilterRow :visible="true" />
                <DxColumn
                    v-for="key in Object.keys(enrichmentResponse[pathwayEnrichmentType.short][0])"
                    :key="key + '_column'"
                    :width="250"
                    :caption="key"
                    :calculate-cell-value="getValue(key)"
                    :calculate-sort-value="getValueAbsolute(key)"
                    alignment="left"
                    :data-type="pathwayEnrichmentType.stringColumns.some(c => key.startsWith(c)) ? 'string' : 'number' "
                    :sort-order="key.startsWith(pathwayEnrichmentType.sortColumn) ? (pathwayEnrichmentType.sortDesc ? 'desc' : 'asc') : null"
                    :allow-sorting="true"
                    :allow-filtering="true"
                    :format="{formatter: val => key.startsWith('Percent Overlap') ? val + '%' : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                    :show-page-size-selector="true"
                    :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>
          </v-tabs-items>
        </v-tab-item>
      </v-tabs-items>
    </div>
  </div>
</template>

<script>
import {
  DxDataGrid,
  DxColumn,
  DxPaging,
  DxPager,
  DxFilterRow
} from 'devextreme-vue/data-grid'
import TheEnrichmentTablePlaceholder from './TheEnrichmentTablePlaceholder'
import downloadUtils from "@/utils/downloadUtils";

export default {
  components: {
    TheEnrichmentTablePlaceholder,
    DxDataGrid,
    DxColumn,
    DxPaging,
    DxPager,
    DxFilterRow
  },
  props: {
    dataGridRefName: {
      type: String,
      default: 'assayGrid'
    },
    datasets: {
      type: Array,
      default: () => []
    },
    enrichmentResponse: {
      type: Object,
      default: () => {
      }
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    enrichmentTypes: {
      type: Array,
      default: () => []
    },
    enrichmentStatuses: {
      type: Array,
      default: () => []
    }
  },
  data: () => ({
    peaVsKaiTab: 'pea',
    pathwayEnrichmentTab: '',
    kinaseActivityTab: '',
    selectedDataset: undefined
  }),
  watch: {
    datasets: {
      immediate: true,
      handler () {
        if (this.datasets.length > 0) { this.selectedDataset = this.datasets[0] }
      }
    },
    selectedDataset: {
      immediate: true,
      handler () {
        if (this.selectedDataset) { this.$emit('enrichment-selected-dataset-changed', this.selectedDataset) }
      }
    }
  },
  methods: {
    getEnrichmentStatusIndicator (status) {
      const statusMapping = {
        completed: { color: 'green', tooltip: 'Completed' },
        'in progress': { color: 'yellow', tooltip: 'In Progress' },
        failed: { color: 'red', tooltip: 'Failed' },
        'not applicable': { color: 'grey', tooltip: 'Not Applicable' }
      }

      return statusMapping[status] || { color: 'grey', tooltip: 'Unknown Status' }
    },
    getValue: function (key) {
      return rowData => rowData[key]
    },
    getValueAbsolute: function (key) {
      return rowData => Math.abs(rowData[key]) || rowData[key]
    },
    saveGridInstance: function (e) {
      this.dataGridInstance = e.component
      // The isLoading watcher is triggered before we arrive here, but the loading indicator cannot be shown
      // before this function has been run. So we need to check again whether we are in a loading state
      if (this.isLoading) {
        this.dataGridInstance.beginCustomLoading()
      }
    },
    onExporting: function () {
      const tabName = (this.peaVsKaiTab === 'pea') ? this.pathwayEnrichmentTab : this.kinaseActivityTab
      downloadUtils.downloadDxDataGridCSV(
          `Enrichment-${tabName}.csv`,
          this.$refs[`${this.dataGridRefName}-${tabName}`]
      )
    }
  }
}

</script>

<style>
@import './ThePathwayEnrichmentTables.css.prdb';
</style>
