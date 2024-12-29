import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import userPtmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import userFpInputList from  './mock_data/mockUserDatasetFPInput.json'
import PrdbPTMInputList from './mock_data/mockPrdbDatasetPTMInput.json'
import PrdbFPInputList from './mock_data/mockPrdbDatasetFPInput.json'
//TODO: Motif and KEA3 not available, haven't checked PrDB datasets yet
import mockUserEnrichmentResults from './mock_data/mockUserEnrichmentResults.json'
import mockPrDBEnrichmentResults from './mock_data/mockPrDBEnrichmentResults.json'


const mockApi = {
    getDefaultSessionId(){
        return '0'.repeat(32)
    },

    getBackendName() {
        return 'Mock API'
    },

    async checkSessionId(uuid) {
        if(!uuid){
            uuid = '0'.repeat(32)
        }
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        } else {
            return {
                cookieStatus: 0,
                uuid,
                datasets: [
                    {datasetName: "MockPTMDataset", datasetId: "mockPtm", omicsType: "FoldChange"},
                    {datasetName: "MockFPDataset", datasetId: "mockFp", omicsType: "FoldChange"}
                ]
            }
        }
    },

    async getOrganisms() {
        return [{taxcode: 9606, name: "Homo sapiens"}]

    },

    async getProjects() {
        return [{projectId: 1234, projectName: "MockPrdbProject"}]

    },

    async getExperimentDesigns(projectId) {
        if (projectId !== 1234) {
            console.log("Mock Backend only has Project 'MockPrdbProject'")
        }
        return [{
            datasetName: "Mock Prdb Experiment Design",
            datasetId: 42,
        }]

    },

    async getCustomPathwayList(uuid) {
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        return customPathwayList;
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

    async getPathwaySkeleton(taxcode, canonicalPathwayLink) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
        }
        if (canonicalPathwayLink !== "WP422.json") {
            console.log('Mock Backend only has WP422 (MAPK cascade)')
        }
        return WP422;

    },

    async getUserProteomicsData(sessionId, userDatasets) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        const userDatasetTypes = {}
        let ptmInputList = [];
        let fpInputList = []

        if(userDatasets.map(d => d.datasetId).includes('mockPtm')){
            userDatasetTypes["mockPtm"] = "phospho"
            ptmInputList = userPtmInputList
        }

        if(userDatasets.map(d => d.datasetId).includes('mockFp')){
            userDatasetTypes["mockFp"] = "fullprot"
            fpInputList = userFpInputList
        }

        return {
            ptmInputList,
            fpInputList,
            userDatasetTypes,
            organismOfFirstDataset : 9606
        }
    },

    async getPrdbData(selectedExperimentDesigns) {
        if (selectedExperimentDesigns !== 42) {
            console.log('Mock backend only has experiment 42!')
        }

        return { ptmInputList:PrdbPTMInputList, fpInputList:PrdbFPInputList }

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
        if (userDatasetIds[0] !== 'mockPtm') {
            console.log(`Mock Backend only has enrichment for the Mock PTM Dataset with ID 'mockPtm'`)
            return null
        }
        return mockUserEnrichmentResults[enrichmentTypeId]

    },
    async getPrdbEnrichmentResults(experimentDesignIds) {
        if (experimentDesignIds !== '42') {
            console.log('Mock backend only has experiment 42!')
        }
        return mockPrDBEnrichmentResults

    },
    async renewSession(uuid) {
        console.log(`Pretending to extend the following UUID: ${uuid}`)

    },
    getCustomDataUploadComponent() {
        console.log('No Custom Data Upload Component Implemented (yet)!')
        return null;

    }
}

export default mockApi
