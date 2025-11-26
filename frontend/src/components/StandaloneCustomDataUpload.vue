<template>
  <v-container
      class="grey lighten-3 pa-4"
      fluid
      style="max-width: 1500px"

  >
    <v-row>
      <v-spacer/>
      <v-col cols="1"
             align-self="end"
             class="text-right">
        <v-tooltip
            bottom
            color="#4d4b4d"
        >
          <template #activator="{ on, attrs }">
            <v-btn
                color="primary"
                fab
                v-bind="attrs"
                v-on="on"
                @click="goToPTMNavigator"
            >
              <v-icon large>
                mdi mdi-replay
              </v-icon>
            </v-btn>
          </template>
          <span>Go back to PTMNavigator</span>
        </v-tooltip>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-card elevation="0">
          <v-card-title><h3>Data Upload</h3></v-card-title>
          <v-tabs
              v-model="activeTab"
              fixed-tabs
              dark
              background-color="primary"
          >
            <v-tab key="ptmTab">
              PTM Data
            </v-tab>
            <v-tab key="proteinTab">
              Protein Data
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="activeTab">
            <v-tab-item key="ptmTabItem">
              <v-card elevation="0">
                <v-card-title>PTM Data Upload</v-card-title>
                <v-card-text>
                  <v-form
                      ref="peptideDataForm"
                      v-model="peptideDatasetFormValid"
                      lazy-validation
                  >
                    <!-- dataset related stuff -->
                    <v-text-field
                        v-model="datasetName"
                        :counter="50"
                        :rules="datasetNameRules"
                        label="Name your dataset"
                        outlined
                        required
                    />

                    <v-select
                        v-model="selectedOrganism"
                        :items="organismList"
                        item-text="text"
                        label="Select Organism"
                        outlined
                        required
                        return-object
                    />

                    <v-select
                        v-model="currentDatasetType"
                        :items="datasetTypes"
                        item-text="text"
                        :rules="datasetTypeRules"
                        label="Select your Dataset type"
                        outlined
                        required
                        return-object
                    />

                    <!--                    PTM Type (we only distinguish phospho vs. non-phospho because this makes a difference for the enrichment)-->
                    <v-radio-group
                        v-model="isPhospho"
                        row
                        mandatory
                        class="mt-n6"
                    >
                      <v-radio :value="true">
                        <template #label>
                          <span style="font-size: 14px">Phosphoproteomics</span>
                        </template>
                      </v-radio>
                      <v-radio :value="false">
                        <template #label>
                          <span style="font-size: 14px">Other PTM</span>
                        </template>
                      </v-radio>
                    </v-radio-group>

                    <!-- File related stuff -->
                    <v-file-input
                        v-model="inputCsvFile"
                        class="ma-2"
                        accept="text/csv,.txt,.tsv"
                        label="Select .csv/.txt file (containing fold changes or curve data)"
                        outlined
                        :rules="fileUploadRules"
                    />
                    <v-file-input
                        v-if="currentDatasetType.type === 'Curve'"
                        v-model="tomlFile"
                        class="ma-2"
                        accept=".toml"
                        label="Select .toml file"
                        outlined
                        :rules="fileUploadRules"
                    />
                  </v-form>
                </v-card-text>

                <v-row justify="end">
                  <v-col
                      cols="12"
                      align-self="end"
                  >
                    <v-card elevation="0">
                      <v-card-title>Enrichment Options</v-card-title>
                      <v-card-subtitle>
                        The enrichment server will run several enrichment algorithms over your data.<br>
                        The results of the enrichments will be displayed in PTMNavigator.
                      </v-card-subtitle>
                      <v-card-text>
                        <h4>Some of the enrichment algorithms can either be run on the full dataset or only on regulated
                          entries.</h4>
                        <v-checkbox
                            v-model="enrichmentFilterRegulated"
                            dense
                        >
                          <template #label>
                            <span style="font-size: 14px">Filter for regulated entries before enrichment</span>
                          </template>
                        </v-checkbox>
                        <div
                        >
                          <h4>Does your data have raw or log-transformed fold changes?</h4>
                          <p>
                            If they are raw, ProteomicsDB will log-transform them for you.
                            If you select "Raw Fold Changes", the values will be log-transformed even if your column is
                            named 'Log Fold Change'.
                          </p>
                          <v-radio-group
                              v-model="foldChangeDataFoldChangeScale"
                              dense
                              row
                              mandatory
                              class="mt-n3"
                          >
                            <v-radio value="log">
                              <template #label>
                                <span style="font-size: 14px">Log Fold Changes</span>
                              </template>
                            </v-radio>
                            <v-radio value="raw">
                              <template #label>
                                <span style="font-size: 14px">Raw Fold Changes</span>
                              </template>
                            </v-radio>
                            <v-radio value="none">
                              <template #label>
                                <span style="font-size: 14px">No Fold Changes</span>
                              </template>
                            </v-radio>
                          </v-radio-group>
                        </div>
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer/>
                        <v-btn
                            :disabled="
                            !peptideDatasetFormValid
                          "
                            color="success"
                            class="mr-4"
                            :loading="isUploading"
                            @click="submit('peptideData')"
                        >
                          Upload File(s)
                        </v-btn>
                        <v-btn
                            fab
                            class="mr-6"
                            elevation="2"
                            color="#e9f1f5"
                            @click="showUploadHelpDialog = !showUploadHelpDialog"
                        >
                          <v-icon>mdi-help</v-icon>
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>
                <v-dialog
                    v-model="showUploadHelpDialog"
                    max-width="500px"
                >
                  <v-card>
                    <v-card-actions>
                      <v-alert
                          class="pa-4 mt-3"
                          color="blue-grey"
                          text
                          icon="mdi-help"
                          prominent
                      >
                        <v-row align="center">
                          <v-col class="grow">
                            Don't know what the input should look like?
                          </v-col>
                          <v-col class="shrink">
                            <v-btn>
                              TODO: Provide Examples or delete
                            </v-btn>
                            <!--                            <v-btn :href="$store.state.host + '/proteomicsdb/logic/customUserData/examples/examples.zip'">-->
                            <!--                              Download Examples-->
                            <!--                            </v-btn>-->
                          </v-col>
                        </v-row>
                      </v-alert>
                    </v-card-actions>
                  </v-card>
                </v-dialog>

              </v-card>
            </v-tab-item>
            <v-tab-item key="proteinTabItem">
              <v-card elevation="0">
                <v-card-title>Protein Data Upload</v-card-title>

                <v-card-text>
                  <v-form
                      ref="proteinDataForm"
                      v-model="proteinDatasetFormValid"
                      lazy-validation
                  >
                    <!-- dataset related stuff -->
                    <v-text-field
                        v-model="datasetName"
                        :counter="50"
                        :rules="datasetNameRules"
                        label="Name your dataset"
                        outlined
                        required
                    />
                    <v-select
                        v-model="selectedOrganism"
                        :items="organismList"
                        item-text="text"
                        label="Select Organism"
                        outlined
                        required
                        return-object
                    />

                    <v-select
                        v-model="currentDatasetType"
                        :items="datasetTypes"
                        item-text="text"
                        :rules="datasetTypeRules"
                        label="Select your Dataset type"
                        outlined
                        required
                        return-object
                    />

                    <!-- File related stuff -->
                    <v-file-input
                        v-model="inputCsvFile"
                        class="ma-2"
                        accept="text/csv,.txt,.tsv"
                        label="Select .csv/.txt file (containing fold changes or curve data)"
                        outlined
                        :rules="fileUploadRules"
                    />
                    <v-file-input
                        v-if="currentDatasetType.type === 'Curve'"
                        v-model="tomlFile"
                        accept=".toml"
                        label="Select .toml file"
                        outlined
                        :rules="fileUploadRules"
                    />
                  </v-form>
                </v-card-text>

                <v-row justify="end">
                  <v-col
                      cols="12"
                      align-self="end"
                  >
                    <v-card elevation="0">
                      <v-card-title>Enrichment Options</v-card-title>
                      <v-card-subtitle>
                        The enrichment server will run several enrichment algorithms over your data.<br>
                        The results of the enrichments will be displayed in PTMNavigator.
                      </v-card-subtitle>
                      <v-card-text>
                        <h4>Some of the enrichment algorithms can either be run on the full dataset or only on regulated
                          entries.</h4>
                        <v-checkbox
                            v-model="enrichmentFilterRegulated"
                            dense
                        >
                          <template #label>
                            <span style="font-size: 14px">Filter for regulated entries before enrichment</span>
                          </template>
                        </v-checkbox>
                        <div
                        >
                          <h4>Does your data have raw or log-transformed fold changes?</h4>
                          <p>
                            If they are raw, ProteomicsDB will log-transform them for you.
                            If you select 'Raw Fold Changes', the values will be log-transformed even if your column is
                            named 'Log Fold Change'.
                          </p>
                          <v-radio-group
                              v-model="foldChangeDataFoldChangeScale"
                              dense
                              row
                              mandatory
                              class="mt-n3"
                          >
                            <v-radio value="raw">
                              <template #label>
                                <span style="font-size: 14px">Raw Fold Changes</span>
                              </template>
                            </v-radio>
                            <v-radio value="log">
                              <template #label>
                                <span style="font-size: 14px">Log Fold Changes</span>
                              </template>
                            </v-radio>

                            <v-radio value="none">
                              <template #label>
                                <span style="font-size: 14px">No Fold Changes</span>
                              </template>
                            </v-radio>
                          </v-radio-group>
                        </div>
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer/>
                        <v-btn
                            :disabled="
                            !proteinDatasetFormValid
                          "
                            color="success"
                            class="mr-4"
                            :loading="isUploading"
                            @click="submit('proteinData')"
                        >
                          Upload File(s)
                        </v-btn>
                        <v-btn
                            fab
                            class="mr-6"
                            elevation="2"
                            color="#e9f1f5"
                            @click="showUploadHelpDialog = !showUploadHelpDialog"
                        >
                          <v-icon>mdi-help</v-icon>
                        </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-col>
                </v-row>


              </v-card>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-card elevation="0">
          <v-card-title>Current Session Information</v-card-title>
          <v-card-text>
            <v-text-field
                v-model="uuid"
                label="Session ID"
                :counter="32"
                :rules="uuidRules"
            />
          </v-card-text>
          <v-card-text>
            <v-select
                v-model="selectedDataset"
                return-object
                outlined
                :items="userDatasets"
                item-text="datasetName"
                item-value="datasetId"
                label="Uploaded Datasets"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer/>
            <v-btn
                :disabled="!uuid || !selectedDataset.datasetName"
                color="primary"
                @click="deletionDialog = true"
            >
              <v-icon left>
                mdi-delete
              </v-icon>
              Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-dialog
        v-model="deletionDialog"
        width="600"
    >
      <v-card>
        <v-card-title>Warning - This will delete data.</v-card-title>
        <v-card-text>
          Selected dataset: <b>{{ selectedDataset.datasetName }}</b> <br>
          Are you sure you want to continue?
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn
              color="primary"
              text
              @click="
              deletionDialog = false;
              deleteDataset();
            "
          >
            Continue
          </v-btn>
          <v-btn
              color="primary"
              text
              @click="deletionDialog = false"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
        v-model="loadingSnackbar"
        :timeout="snackbarTimeout"
        color="primary"
        width="500"
    >
      Please wait. Your data is being uploaded...
      <template #action="{ attrs }">
        <v-btn
            color="white"
            text
            v-bind="attrs"
            @click="loadingSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
        v-model="uploadSnackbar"
        :timeout="snackbarTimeout"
        color="primary"
        width="500"
    >
      {{ uploadedDatasetMessage }}
      <template #action="{ attrs }">
        <v-btn
            color="white"
            text
            v-bind="attrs"
            @click="uploadSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
        v-model="uploadErrorSnackbar"
        color="red accent-2"
    >
      {{ uploadErrorMessage }}
      <template #action="{ attrs }">
        <v-btn
            color="white"
            text
            v-bind="attrs"
            @click="uploadErrorSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar
        v-model="deletedDatasetSnackbar"
        :timeout="snackbarTimeout"
        color="primary"
    >
      {{ deletedDatasetMessage }}
      <template #action="{ attrs }">
        <v-btn
            color="white"
            text
            v-bind="attrs"
            @click="deletedDatasetSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script>
import {apiValidator} from "@/types/backendApiInterface";

export default {
  name: 'DataUpload',
  metaInfo() {
    return {
      title: 'Upload',
      titleTemplate: '%s',
      meta: [
        {charset: 'utf-8'},
        {name: 'description', content: 'Upload your data to PTMNavigator.'}
      ]
    }
  },
  props: {
    /** @type {BackendApiInterface} */
    backendApi: {
      type: Object,
      required: true,
      validator: apiValidator
    },
  },
  data() {
    return {
      activeTab: 0,

      //Peptide Tab
      peptideDatasetFormValid: true,
      isPhospho: true,

      //Protein Tab
      proteinDatasetFormValid: true,

      //Common variables for both tabs
      datasetName: '',
      datasetNameRules: [
        (v) => !!v || 'Name is required.',
        (v) => (v && v.length >= 5) || 'Name must be longer than 5 characters.',
        (v) =>
            (v && !!v.match(/^[a-zA-Z0-9_-]+$/i)) ||
            'Name can only contain the following characters: a-z, A-Z, 0-9, - , _ .'
      ],
      datasetTypes: [
        {
          id: 1,
          text: "Quantitative Proteomics ('Fold Change Data')",
          type: 'FoldChange'
        }, {
          id: 2,
          text: 'decryptM / CurveCurator',
          type: 'Curve'
        }],
      datasetTypeRules: [(t) => (!!t && t !== -1) || 'Dataset type is required.'],
      currentDatasetType: -1,
      organismList: undefined,
      selectedOrganism: undefined,
      defaultTaxcode: 9606, //Homo sapiens as default organism
      inputCsvFile: null,
      fileUploadRules: [
        (value) => typeof value !== 'undefined' || 'Please choose a file.',
        (value) =>
            (value && value.size < 1000000000) ||
            'File size should be less than 1 GB!'
      ],
      tomlFile: null,
      enrichmentFilterRegulated: false,
      foldChangeDataFoldChangeScale: null,
      isUploading: false,


      //SessionID & Datasets Section
      uuid: '',
      uuidRules: [
        (uuid) =>
            !!uuid.match(/^[A-F0-9]{32}$/i) ||
            'Session ID must have a length of 32 characters and only contain "0-9, A-F".'
      ],
      userDatasets: [],
      selectedDataset: {},


      //Dialogs
      deletionDialog: false,
      showUploadHelpDialog: false,

      //Snackbars
      snackbarTimeout: 4000,
      loadingSnackbar: false,
      uploadSnackbar: false,
      uploadErrorSnackbar: false,
      deletedDatasetSnackbar: false,
      uploadedDatasetMessage: '',
      uploadErrorMessage: '',
      deletedDatasetMessage: '',

    }
  },
  computed: {
  },
  watch: {
    uuid: {
      immediate: true,
      async handler(newUUID, oldUUID) {
        // Validate the UUID
        if (newUUID !== oldUUID && newUUID.length === 32) {
          const sessionIdResponse = (await this.backendApi.refreshSessionId(newUUID)).session_id
          if (sessionIdResponse !== newUUID) {
            this.uuid = sessionIdResponse
            return
          }
          const userDatasetListResponse = await this.backendApi.getUserDatasetList(newUUID)

          const d = new Date()
          d.setTime(d.getTime() + 14 * 24 * 60 * 60 * 1000)
          this.$cookie.set('analyticsUploadSessionID', newUUID, {expires: d})
          this.userDatasets = userDatasetListResponse
        }
      }
    }
  },
  methods: {

    async submit(uploadType) {
      //Validate
      if (!this.$refs[uploadType + 'Form'].validate()) {
        console.error(`Validation failed for: ${uploadType}`)
      }

      //Refresh UUID, automatically create a new one if the user does not have one yet
      this.uuid = (await this.backendApi.refreshSessionId(this.uuid)).session_id


      //Create form for request
      const formData = new FormData()
      formData.append('tomlFile', this.tomlFile)
      formData.append('csvFile', this.inputCsvFile)
      const params = {
        uuid: this.uuid,
        uploadType: uploadType,
        datasetName: this.datasetName,
        datasetType: this.currentDatasetType.type,
        omics: (uploadType === 'proteinData') ? 'Protein' : (this.isPhospho ? 'Phosphorylation' : 'Other'),
        foldChangeDataFoldChangeScale: this.currentDatasetType.needsToml ? null : this.foldChangeDataFoldChangeScale,
        taxcode: this.selectedOrganism.value
      }


      //Send the request
      //TODO: Check if request/cancel tokens are a thing for your server
      //TODO: Check if these two flags always correlate, if yes eliminate one
      this.loadingSnackbar = true
      this.isUploading = true
      try {
        const response = await this.backendApi.uploadDataset(formData, params)
        if (response.data.datasetId) {
          await this.backendApi.performUserDatasetEnrichment(
              {
                datasetId: response.data.datasetId,
                uuid: this.uuid,
                datasetName: this.datasetName,
                onlyRegulated: this.enrichmentFilterRegulated,
                taxcode: this.selectedOrganism.value
              })
        }
        this.loadingSnackbar = false
        this.isUploading = false
        this.uploadedDatasetMessage = response.data.message
        this.uploadSnackbar = true
      } catch (error) {
        console.log(error)
        this.isUploading = false
        this.uploadErrorMessage = error.response ? error.response.data : error
        this.uploadSnackbar = false
        this.uploadErrorSnackbar = true
      }
    },

    goToPTMNavigator() {
      this.$router.push({name: 'PTMNavigator', props: {backendApi: this.backendApi, ptmNavigatorRouter: this.$router}})
    },
    async loadOrganisms() {
      const organismResponse = await this.backendApi.getOrganisms()
      this.organismList = organismResponse.map(datum => {
        return {text: datum.name, value: datum.taxcode}
      })
      this.selectedOrganism = this.organismList.filter(org => org.value === this.defaultTaxcode)[0]
    },
    async deleteDataset() {
      const deletionResponse =  await this.backendApi.deleteDataset(this.uuid, this.selectedDataset.datasetId)
      this.deletedDatasetSnackbar = true
      this.deletedDatasetMessage = deletionResponse.data.message
    }
  },
  mounted() {
    this.loadOrganisms()
    this.uuid = this.$cookie.get('analyticsUploadSessionID') || ''
  }

}
</script>

<style scoped>

</style>