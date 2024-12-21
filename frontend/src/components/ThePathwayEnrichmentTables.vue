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
          key="kea"
          class="enrichment-tab"
          href="#kea"
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
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="ptmsea"
                  class="enrichment-tab"
                  href="#ptmsea"
                  v-on="on"
                >
                  PTM-SEA
                </v-tab>
              </template>
              <span>PTM-Centric Enrichment Analysis using the PTM Signature Database (PTMSigDB).<br>
                Basically a GSEA that is Single-Site-Centric (ssc).</span>
            </v-tooltip>
            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="gc"
                  class="enrichment-tab"
                  href="#gc"
                  v-on="on"
                >
                  PEA Gene-Centric
                </v-tab>
              </template>
              <span>Gene-Centric Enrichment Analysis using the Molecular Signatures Database (MSigDB).<br>
                PTM data is collapsed to gene level.<br>
                We use the KEGG and WikiPathways signature sets.</span>
            </v-tooltip>
            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="gcr"
                  class="enrichment-tab"
                  href="#gcr"
                  v-on="on"
                >
                  PEA Gene-Centric Redundant
                </v-tab>
              </template>
              <span>Gene-Centric-Redundant Enrichment Analysis using the Molecular Signatures Database (MSigDB).<br>
                PTM data is collapsed to gene level.<br>
                We use the KEGG and WikiPathways signature sets.</span>
            </v-tooltip>
          </v-tabs>
          <v-tabs-items
            v-model="pathwayEnrichmentTab"
            class="pt-5"
          >
            <v-tab-item
              value="ptmsea"
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
                    PTM-SEA Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
    gene.set.database:   ptm.sig.db.all.uniprot.human.v2.0.0.gmt
    sample.norm.type:    rank
    weight:              0.75
    statistic:           area.under.RES
    output.score.type    NES
    nperm:               1000
    global.fdr:          FALSE
    min.overlap:         10
    correl.type:         z.score
    export.signat.gct:   FALSE
    run.parallel:        TRUE
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !!enrichmentResponse.ptmsea && enrichmentResponse.ptmsea.length > 0"
                :ref="dataGridRefName + '-' + pathwayEnrichmentTab"
                :data-source="enrichmentResponse.ptmsea"
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
                  v-for="key in Object.keys(enrichmentResponse.ptmsea[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Signature ID' || key === 'Gene') ? 'string' : 'number'"
                  :sort-order="key.startsWith('Score') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Signature ID' || key === 'Gene')"
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
            <v-tab-item
              value="gc"
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
                    Gene-Centric ssGSEA Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
    gene.set.database:  c2.cp.kegg+wp.v2023.2.Hs.symbols.gmt
    sample.norm.type:   rank
    weight:             0.75
    statistic:          area.under.RES
    output.score.type   NES
    nperm:              1000
    global.fdr:         FALSE
    min.overlap:        10
    correl.type:        z.score
    export.signat.gct:  FALSE
    run.parallel:       TRUE
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.gc&& enrichmentResponse.gc.length > 0"
                :ref="dataGridRefName + '-' + pathwayEnrichmentTab"
                :data-source="enrichmentResponse.gc"
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
                  v-for="key in Object.keys(enrichmentResponse.gc[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Signature ID' || key === 'Gene') ? 'string' : 'number'"
                  :sort-order="key.startsWith('Score') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Signature ID' || key === 'Gene')"
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
            <v-tab-item
              value="gcr"
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
                    Gene-Centric Redundant ssGSEA Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
    gene.set.database:  c2.cp.kegg+wp.v2023.2.Hs.symbols.gmt
    sample.norm.type:   rank
    weight:             0.75
    statistic:          area.under.RES
    output.score.type   NES
    nperm:              1000
    global.fdr:         FALSE
    min.overlap:        10
    correl.type:        z.score
    export.signat.gct:  FALSE
    run.parallel:       TRUE
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.gcr&& enrichmentResponse.gcr.length > 0"
                :ref="dataGridRefName + '-' + pathwayEnrichmentTab"
                :data-source="enrichmentResponse.gcr"
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
                  v-for="key in Object.keys(enrichmentResponse.gcr[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Signature ID' || key === 'Gene') ? 'string' : 'number'"
                  :sort-order="key.startsWith('Score') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Signature ID' || key === 'Gene')"
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
        <v-tab-item value="kea">
          <v-tabs
            v-model="kinaseActivityTab"
            dark
          >
            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="ksea"
                  class="enrichment-tab"
                  href="#ksea"
                  v-on="on"
                >
                  KSEA
                </v-tab>
              </template>
              <span>Kinase Activity Inference using phosphoproteomic data and prior knowledge on kinase-substrate relationships.<br>
                In KSEA, the mean fold change among the set of substrates of each kinase is compared to an expected value.<br></span>
            </v-tooltip>
            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="ksea_rokai"
                  class="enrichment-tab"
                  href="#ksea_rokai"
                  v-on="on"
                >
                  KSEA with RoKAI
                </v-tab>
              </template>
              <span>RoKAI refines phosphorylation profiles using prior knowledge functional networks.<br>
                KSEA is run on the refined profiles afterwards.<br>
                In general, this produces more robust results compared to only running KSEA.</span>
            </v-tooltip>

            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="motif"
                  class="enrichment-tab"
                  href="#motif"
                  v-on="on"
                >
                  Motif Enrichment
                </v-tab>
              </template>
              <span>Performs a Kinase Motif Enrichment by utilizing the Kinase Library.<br>
                Position-specific scoring matrices are used to score the motif of each kinase against a phosphoproteomics dataset.</span>
            </v-tooltip>

            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="kea3_mean"
                  class="enrichment-tab"
                  href="#kea3_mean"
                  v-on="on"
                >
                  KEA3 MeanRank
                </v-tab>
              </template>
              <span>Kinase enrichment analysis using the KEA3 algorithm.<br>
                KEA3 infers upstream kinases whose putative substrates are <br>
                overrepresented in a user-inputted list of proteins or differentially phosphorylated proteins.</span>
            </v-tooltip>

            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="kea3_top"
                  class="enrichment-tab"
                  href="#kea3_top"
                  v-on="on"
                >
                  KEA3 TopRank
                </v-tab>
              </template>
              <span>Kinase enrichment analysis using the KEA3 algorithm.<br>
                KEA3 infers upstream kinases whose putative substrates are <br>
                overrepresented in a user-inputted list of proteins or differentially phosphorylated proteins.</span>
            </v-tooltip>

            <v-tooltip
              top
              color="#4d4b4d"
            >
              <template #activator="{ on, attrs }">
                <v-tab
                  v-bind="attrs"
                  key="kstar"
                  class="enrichment-tab"
                  href="#kstar"
                  v-on="on"
                >
                  KSTAR
                </v-tab>
              </template>
              <span>Kinase Activity Prediction using the KSTAR algorithm.</span>
            </v-tooltip>
          </v-tabs>
          <v-tabs-items
            v-model="kinaseActivityTab"
            class="pt-5"
          >
            <v-tab-item
              value="ksea"
            >
              <v-dialog
                width="1000"
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
                    KSEA Parameters (kinact)
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
   interactions:   "Kinase-Substrate Interactions from PhosphoSitePlus"
                   See also here:
                    github.com/kusterlab/enrichment-server/blob/publication/db/scripts/update_ksea_es_db.py
   mP:             "Experiment-Wise Fold Change Mean"
   delta:          "Experiment-Wise Fold Change Standard Deviation"
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.ksea&& enrichmentResponse.ksea.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.ksea"
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
                  v-for="key in Object.keys(enrichmentResponse.ksea[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Signature ID' || key === 'Gene') ? 'string' : 'number'"
                  :sort-order="key.startsWith('Score') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Signature ID' || key === 'Gene')"
                  :format="{formatter: val => key.startsWith('Overlap') ? val + '%' : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                  :show-page-size-selector="true"
                  :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>
            <v-tab-item
              value="ksea_rokai"
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
                    RoKAI Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
    network_file:   rokai_network_data_uniprotkb_human.rds (v2.2.0)
    datanorm:       Normalized
    ksNetwork:      PhosphoSitePlus (includeSignor = F)
    rokaiNetwork:   KS+PPI+SD+CoEv
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.ksea_rokai&& enrichmentResponse.ksea_rokai.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.ksea_rokai"
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
                  v-for="key in Object.keys(enrichmentResponse.ksea_rokai[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Signature ID' || key === 'Gene') ? 'string' : 'number'"
                  :sort-order="key.startsWith('Score') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Signature ID' || key === 'Gene')"
                  :format="{formatter: val => key.startsWith('Overlap') ? val + '%' : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                  :show-page-size-selector="true"
                  :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>

            <v-tab-item
              value="motif"
            >
              <v-dialog
                width="1000"
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
                <v-card
                  style="overflow-x: scroll;"
                >
                  <v-card-title class="text-h5 grey lighten-2">
                    Motif Enrichment Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
  This is an inhouse re-implementation of the Kinase Library tool: https://kinase-library.phosphosite.org
  For implementation details see here:
  github.com/kusterlab/enrichment-server/blob/publication/flask_server/modules/motif_enrichment/motif_enrichment.py
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>

              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.motif&& enrichmentResponse.motif.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.motif"
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
                  v-for="key in Object.keys(enrichmentResponse.motif[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Kinase') ? 'string' : 'number'"
                  :sort-order="key.startsWith('-Log10 p_value adjusted') ? 'desc' : null"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Kinase')"
                  :format="{formatter: val => val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                  :show-page-size-selector="true"
                  :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>

            <v-tab-item
              value="kea3_mean"
            >
              <v-dialog
                width="800"
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
                    KEA3 Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
   We use the KEA3 API endpoint: https://amp.pharm.mssm.edu/kea3/api/enrich/
   This table shows the 'Integrated--meanRank' part of the results.
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.kea3_mean&& enrichmentResponse.kea3_mean.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.kea3_mean"
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
                  v-for="key in Object.keys(enrichmentResponse.kea3_mean[0]).filter(col => col !== 'Query Name')"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="[ 'TF', 'Library', 'Overlapping_Genes'].includes(key) ? 'string' : 'number'"
                  :sort-order="key === 'Rank' ? 'asc' : null"
                  :allow-sorting="true"
                  :allow-filtering="['TF', 'Library', 'Overlapping_Genes', 'Experiment'].includes(key)"
                  :format="{formatter: val => key=== 'Rank' ? val : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                  :show-page-size-selector="true"
                  :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>

            <v-tab-item
              value="kea3_top"
            >
              <v-dialog
                width="800"
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
                    KEA3 Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
   We use the KEA3 API endpoint: https://amp.pharm.mssm.edu/kea3/api/enrich/
   This table shows the 'Integrated--topRank' part of the results.
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>
              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.kea3_top&& enrichmentResponse.kea3_top.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.kea3_top"
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
                  v-for="key in Object.keys(enrichmentResponse.kea3_top[0]).filter(col => col !== 'Query Name')"
                  :key="key + '_column'"
                  :width="250"
                  :caption="key"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="[ 'TF', 'Library', 'Overlapping_Genes'].includes(key) ? 'string' : 'number'"
                  :sort-order="key === 'Rank' ? 'asc' : null"
                  :allow-sorting="true"
                  :allow-filtering="['TF', 'Library', 'Overlapping_Genes', 'Experiment'].includes(key)"
                  :format="{formatter: val => key=== 'Rank' ? val : val.toFixed(2)}"
                />
                <DxPaging :page-size="10" />
                <DxPager
                  :show-page-size-selector="true"
                  :allowed-page-sizes="[5, 10, 25]"
                />
              </DxDataGrid>
              <TheEnrichmentTablePlaceholder v-else />
            </v-tab-item>

            <v-tab-item
              value="kstar"
            >
              <v-dialog
                width="1050"
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
                    K-STAR Parameters
                  </v-card-title>

                  <v-card-text class="mt-5">
                    <pre>
  We use the functions calculate.KinaseActivity() and calculate.enrichment_analysis() from the kstar Python package.
  Because of time and memory constraints, we do not perform the randomized analysis and Mann Whitney U-test,
  instead we directly return the p-values from the hypergeometric tests.
  For implementation details see here:
  github.com/kusterlab/enrichment-server/blob/publication/flask_server/modules/k_star/k_star.py
                            </pre>
                  </v-card-text>
                </v-card>
              </v-dialog>

              <DxDataGrid
                v-if="!!selectedDataset && !!enrichmentResponse && !! enrichmentResponse.kstar&& enrichmentResponse.kstar && enrichmentResponse.kstar.length > 0"
                :ref="dataGridRefName + '-' + kinaseActivityTab"
                :data-source="enrichmentResponse.kstar"
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
                  v-for="key in Object.keys(enrichmentResponse.kstar[0])"
                  :key="key + '_column'"
                  :width="250"
                  :caption="(key === 'Kinase') ? key : 'p-value ('+key+')'"
                  :calculate-cell-value="getValue(key)"
                  :calculate-sort-value="getValueAbsolute(key)"
                  alignment="left"
                  :data-type="(key === 'Kinase') ? 'string' : 'number'"
                  :sort-order="key === 'Kinase' ? null : 'asc'"
                  :allow-sorting="true"
                  :allow-filtering="(key === 'Kinase')"
                  :format="{formatter: val => val.toFixed(2)}"
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
      default: () => {}
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    enrichmentStatuses: {
      type: Array,
      default: () => []
    }
  },
  data: () => ({
    peaVsKaiTab: 'pea',
    pathwayEnrichmentTab: 'ptmsea',
    kinaseActivityTab: 'ksea',
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
      // Hotfix 2024-11-08: Disable K-STAR for new datasets
      if (status === 'disabled_kstar') {
        return { color: 'grey', tooltip: 'Unfortunately, KSTAR is currently disabled for new datasets.' }
      }

      return statusMapping[status] || { color: 'grey', tooltip: 'Unknown Status' }
    },
    getValue: function (key) {
      return rowData => rowData[key]
    },
    getValueAbsolute: function (key) {
      return rowData => Math.abs(rowData[key])
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
