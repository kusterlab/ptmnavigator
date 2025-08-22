import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import userPtmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import userFpInputList from  './mock_data/mockUserDatasetFPInput.json'

import userdecryptMInputList from  './mock_data/mockUserDatasetDecryptMInput.json'
import userdecryptEInputList from './mock_data/mockUserDatasetDecryptEInput.json'

import InternalDatabasePTMInputList from './mock_data/mockInternalDatabaseDatasetPTMInput.json'
import InternalDatabaseFPInputList from './mock_data/mockInternalDatabaseDatasetFPInput.json'
//TODO: Motif and KEA3 not available, haven't checked InternalDatabase datasets yet
import mockUserEnrichmentResults from './mock_data/mockUserEnrichmentResults.json'
import mockInternalDatabaseEnrichmentResults from './mock_data/mockInternalDatabaseEnrichmentResults.json'


const mockApi = {

    getBackendName() {
        return 'Internal Database'
    },

    async getOrganisms() {
        return [{taxcode: 9606, name: "Homo sapiens"}]
    },

    getDefaultSessionId() {
        return '0'.repeat(32)
    },

    async renewSession(uuid) {
        console.log(`Pretending to extend the following UUID: ${uuid}`)

    },

    refreshSessionId(uuid) {
        if (!uuid) {
            uuid = '0'.repeat(32)
        }
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        } else {
            //A proper backend could also refresh the expiry date of the uuid
            return {
                cookieStatus: 0,
                uuid,
            }
        }
    },

    getUserDatasetList(uuid) {
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
            return []
        } else {
            return [
                {datasetName: "MockPTMDataset", datasetId: 1, omicsType: "FoldChange"},
                {datasetName: "MockFPDataset", datasetId: 2, omicsType: "FoldChange"},
                {datasetName: "MockDecryptMDataset", datasetId: 3, omicsType: "decryptM"},
                {datasetName: "MockDecryptEDataset", datasetId: 4, omicsType: "decryptE"}
            ]
        }
    },

    /**
     * Session ID is added as additional parameter for security reasons - otherwise, a third party could access a user dataset by guessing the ID
     * The 32-Digit Session ID is much harder to guess
     * @param sessionId
     * @param userDatasets
     * @returns {Promise<{fpInputList: *[], organismOfFirstDataset: number, ptmInputList: *[], userDatasetTypes: {}}>}
     */
    async loadUserDatasets(sessionId, userDatasets) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        const userDatasetTypes = {}
        let ptmInputList = [];
        let fpInputList = []


        if (userDatasets.map(d => d.datasetId).includes(1)) {
            userDatasetTypes[1] = "phospho"
            ptmInputList = ptmInputList.concat(userPtmInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(2)) {
            userDatasetTypes[2] = "fullprot"
            fpInputList = fpInputList.concat(userFpInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(3)) {
            userDatasetTypes[3] = "phospho"
            ptmInputList = ptmInputList.concat(userdecryptMInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(4)) {
            userDatasetTypes[4] = "fullprot" //TODO: Replace fullprot by protein - or maybe just distinguish phospho and nonphospho, that is all this field is used for at the moment
            fpInputList = fpInputList.concat(userdecryptEInputList)
        }

        return {
            ptmInputList,
            fpInputList,
            userDatasetTypes,
            //TODO: Awkwaaaard
            organismOfFirstDataset: 9606
        }
    },

    async getInternalProjects() {
        return [{projectId: 1234, projectName: "MockInternalDatabaseProject"}]
    },

    async getInternalDatasetsForProject(projectId) {
        if (projectId !== 1234) {
            console.log("Mock Backend only has Project 'MockInternalDatabaseProject'")
        }
        return [{
            datasetName: "MockInternalPTMDataset",
            datasetId: 42,
            omicsType: 'FoldChange'
        },
            {
                datasetName: "MockInternalFPDataset",
                datasetId: 43,
                omicsType: 'FoldChange'
            }
        ]
    },

    async loadInternalDatasets(selectedDatasets) {
        let ptmInputList = [];
        let fpInputList = []

        if (selectedDatasets.map(d => d.datasetId).includes(42)) {
            ptmInputList = ptmInputList = ptmInputList.concat(InternalDatabasePTMInputList)
        }

        if (selectedDatasets.map(d => d.datasetId).includes(43)) {
            fpInputList = fpInputList.concat(InternalDatabaseFPInputList)
        }

        return {
            ptmInputList,
            fpInputList,
            organismOfFirstDataset: 9606
        }

    },


    async getCanonicalPathwayList(taxcode) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
        }
        return [{
            name: "WP422",
            title: "MAPK cascade",
            link: "WP422.json"
        }]

    },

    async getCustomPathwayList(uuid) {
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        return customPathwayList;
    },

    async getPathwaySkeleton(taxcode, canonicalPathwayLink) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
        }
        if (canonicalPathwayLink !== "WP422.json") {
            console.log('Mock Backend only has WP422 (MAPK cascade)')
        }
        return WP422;

    },

    async storeCustomPathway(skeleton, uuid, customPathwayName, currentlyEditedPathwayId) {
        console.log("Pretending to send the following request to the backend:")
        console.log(`uuid: ${uuid}, pathwayName: ${customPathwayName}, customPathwayId: ${currentlyEditedPathwayId}`)
        console.log('Skeleton:')
        console.log(skeleton)


    },

    async getFilteredPathwayIds(searchStrings, taxcode) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
        }
        console.log(`Ignoring search string because I am a mock backend... (${searchStrings})`)
        return ['WP422']


    },

    async getUserEnrichmentResults(sessionId, userDatasetIds, enrichmentTypeId) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        if (userDatasetIds[0] !== 1) {
            console.log(`Mock Backend only has enrichment for the Mock PTM Dataset with ID 1`)
            return null
        }
        return mockUserEnrichmentResults[enrichmentTypeId]

    },
    async getInternalDatabaseEnrichmentResults(experimentDesignIds) {
        if (experimentDesignIds !== '42') {
            console.log('Mock backend only has experiment 42!')
        }
        return mockInternalDatabaseEnrichmentResults

    },

    async getCurveData(curveIDs){
        if(!curveIDs || curveIDs.length === 0){
            return [];
        }
        return await Promise.all(curveIDs.map(async curveId => {
            const jsonfile = await import(`./mock_data/curve_data/${curveId}.json`);
            return jsonfile.default;
        }))
    },

    getCustomDataUploadComponent() {
        console.log('No Custom Data Upload Component Implemented (yet)!')
        return null;

    }
}

export default mockApi
