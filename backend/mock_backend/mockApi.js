import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import ptmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import fpInputList from  './mock_data/mockUserDatasetFPInput.json'
import PrdbPTMInputList from './mock_data/mockPrdbDatasetPTMInput.json'
import PrdbFPInputList from './mock_data/mockPrdbDatasetFPInput.json'
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
                datasets: [{
                    datasetName: "MockDataset", datasetId: "mock", omicsType: "FoldChange"
                }]
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
            console.log('Mock Backend only has Project 1234')
        } else {
            return [{
                datasetName: "Mock Experiment Design",
                datasetId: 42,
            }]
        }

    },

    async getCustomPathwayList(uuid) {
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        } else {
            return customPathwayList;
        }
    },

    async getCanonicalPathwayList(taxcode) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
        } else {
            return [{
                name: "WP422",
                title: "MAPK cascade",
                link: "WP422.json"
            }]
        }

    },

    async getPathwaySkeleton(taxcode, canonicalPathwayLink) {
        if (taxcode !== 9606) {
            console.log('Mock Backend only has Taxcode 9606 (Homo sapiens)')
            return null;
        }
        if (canonicalPathwayLink !== "WP422.json") {
            console.log('Mock Backend only has WP422 (MAPK cascade)')
            return null;
        }
        return WP422;

    },

    async getUserProteomicsData(sessionId, userDatasets) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
            return null
        }
        if (userDatasets[0].datasetId !== 'mock') {
            console.log(`Mock Backend only has the dataset with the ID 'mock'`)
            return null
        }
        const userDatasetTypes = {
            "Mock_User_PTM_Dataset": "phospho",
            "Mock_User_FP_Dataset": "fullprot", //TODO: Not sure if this name is preserved, if not, check what name PTMNav expects
        }
        const organismOfFirstDataset = 9606;

        return {
            ptmInputList,
            fpInputList,
            userDatasetTypes,
            organismOfFirstDataset
        }
    },

    async getPrdbData(selectedExperimentDesigns) {
        if (selectedExperimentDesigns !== 42) {
            console.log('Mock backend only has experiment 42!')
        } else {

            return { ptmInputList:PrdbPTMInputList, fpInputList:PrdbFPInputList }
        }
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
        } else {
            console.log(`Ignoring search string because I am a mock backend... (${searchStrings})`)
            return ['WP422']
        }

    },

    async getUserEnrichmentResults(sessionId, userDatasetIds, enrichmentTypeId) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
            return null
        }
        if (userDatasetIds[0] !== 'mock') {
            console.log(`Mock Backend only has the dataset with the ID 'mock'`)
            console.log(`You attempted: ${userDatasetIds[0]}`)
            return null
        }
        return mockUserEnrichmentResults[enrichmentTypeId]

    },
    async getPrdbEnrichmentResults(experimentDesignIds) {
        if (experimentDesignIds !== '42') {
            console.log('Mock backend only has experiment 42!')
        } else {
            return mockPrDBEnrichmentResults
        }
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
