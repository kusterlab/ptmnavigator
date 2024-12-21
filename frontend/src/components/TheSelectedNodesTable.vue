<template>
  <div>
    <DxDataGrid
      :ref="dataGridRefName"
      :data-source="dataIn"
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
      <DxHeaderFilter
        :visible="true"
        :allow-search="true"
        :width="300"
      />
      <DxColumn
        v-for="colname in columnNames"
        :key="colname"
        :caption="colname"
        :calculate-cell-value="getValue(colname)"
        alignment="left"
        :allow-sorting="true"
        :allow-filtering="true"
        :cell-template="getTemplate(colname)"
      />
      <template #regulationTemplate="{ data }">
        <v-icon
          v-if="data.value === 'up'"
          color="#ea0000"
        >
          mdi-arrow-up-bold
        </v-icon>
        <v-icon
          v-else-if="data.value === 'down'"
          color="#252bff"
        >
          mdi-arrow-down-bold
        </v-icon>
        <v-icon
          v-else-if="data.value === '-' || data.value === 'not'"
          color="#000000"
        >
          mdi-minus
        </v-icon>
        <v-icon
          v-else-if="data.value === 'both'"
          color="#8100c2"
        >
          mdi-arrow-up-down-bold
        </v-icon>
      </template>

      <template #multilineHTMLTemplate="{ data }">
        <div v-if="!!data.value">
          <div
            v-for="link in new Set(data.value.split(','))"
            :key="link"
            v-html="link"
          />
        </div>
      </template>

      <DxPaging :page-size="10" />
      <DxPager
        :show-page-size-selector="true"
        :allowed-page-sizes="[5, 10, 25]"
      />

      <DxPaging :page-size="10" />
      <DxPager
        :show-page-size-selector="true"
        :allowed-page-sizes="[5, 10, 25]"
      />
    </DxDataGrid>
  </div>
</template>

<script>
import {
  DxDataGrid,
  DxColumn,
  DxPaging,
  DxPager,
  DxFilterRow,
  DxHeaderFilter
} from 'devextreme-vue/data-grid'
import downloadUtils from "@/utils/downloadUtils";

export default {
  name: 'TheSelectedNodesTable',
  components: {
    DxDataGrid,
    DxColumn,
    DxPaging,
    DxPager,
    DxFilterRow,
    DxHeaderFilter
  },
  props: {
    dataGridRefName: {
      type: String,
      default: 'selectednodestable'
    },
    dataIn: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    columnBlacklist: [
      'Uniprot_Accession_Number',
      'Site'

    ]
  }),
  computed: {
    columnNames () {
      const allColumnNames = new Set()
      this.dataIn.forEach(obj => {
        Object.keys(obj).forEach(key => {
          if (!this.columnBlacklist.includes(key) && !!obj[key] && String(obj[key]).trim() !== '' && obj[key]) { allColumnNames.add(key) }
        })
      })

      // For Full Proteome data, sort the #Up,#Down, #Not columns to the end, if present
      const columnNamesInOrder = [...allColumnNames].filter(item => !['#Up', '#Down', '#Not'].includes(item));
      ['#Up', '#Down', '#Not'].forEach(col => {
        if (allColumnNames.has(col)) { columnNamesInOrder.push(col) }
      })
      return columnNamesInOrder
    }
  },
  methods: {
    getValue: function (key) {
      return rowData => rowData[key]
    },
    getTemplate: function (colname) {
      const templateDictionary = {
        Regulation: 'regulationTemplate',
        Uniprot: 'multilineHTMLTemplate',
        'Site(s)': 'multilineHTMLTemplate',
        'Gene Name(s)': 'multilineHTMLTemplate',
        'Functional Score*': 'multilineHTMLTemplate'
      }
      return templateDictionary[colname]
    },
    saveGridInstance: function (e) {
      this.dataGridInstance = e.component
      // The isLoading watcher is triggered before we arrive here, but the loading indicator cannot be shown
      // before this function has been run. So we need to check again whether we are in a loading state
      if (this.isLoading) {
        this.dataGridInstance.beginCustomLoading()
      }
    },
    onExporting: function (nodetype) {
      downloadUtils.downloadDxDataGridCSV(
        `Selected_${nodetype}.csv`,
        this.$refs[this.dataGridRefName]
      )
    }
  }
}
</script>

<style scoped>

</style>
