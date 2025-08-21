import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import userPtmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import userFpInputList from  './mock_data/mockUserDatasetFPInput.json'

import userdecryptMInputList from  './mock_data/mockUserDatasetDecryptMInput.json'
// import userFpInputList from  './mock_data/mockUserDatasetFPInput.json'

import InternalDatabasePTMInputList from './mock_data/mockInternalDatabaseDatasetPTMInput.json'
import InternalDatabaseFPInputList from './mock_data/mockInternalDatabaseDatasetFPInput.json'
//TODO: Motif and KEA3 not available, haven't checked InternalDatabase datasets yet
import mockUserEnrichmentResults from './mock_data/mockUserEnrichmentResults.json'
import mockInternalDatabaseEnrichmentResults from './mock_data/mockInternalDatabaseEnrichmentResults.json'


const mockApi = {
    getDefaultSessionId() {
        return '0'.repeat(32)
    },

    getBackendName() {
        return 'Internal Database'
    },

    refreshSessionId(uuid) {
        if (!uuid) {
            uuid = '0'.repeat(32)
        }
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }else {
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
                {datasetName: "MockPTMDataset", datasetId: "mockPtm", omicsType: "FoldChange"},
                {datasetName: "MockFPDataset", datasetId: "mockFp", omicsType: "FoldChange"},
                {datasetName: "MockDecryptMDataset", datasetId: "mockDecryptM", omicsType: "decryptM"},
                // {datasetName: "MockDecryptEDataset", datasetId: "mockDecryptE", omicsType: "decryptE"} //TODO: decryptE probably not recognized by PTMNav
            ]
        }
    },

    async getOrganisms() {
        return [{taxcode: 9606, name: "Homo sapiens"}]

    },

    async getProjects() {
        return [{projectId: 1234, projectName: "MockInternalDatabaseProject"}]

    },

    async getExperimentDesigns(projectId) {
        if (projectId !== 1234) {
            console.log("Mock Backend only has Project 'MockInternalDatabaseProject'")
        }
        return [{
            datasetName: "Mock InternalDatabase Experiment Design",
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

        if(userDatasets.map(d => d.datasetId).includes('mockDecryptM')){
            userDatasetTypes["mockDecryptM"] = "decryptM" //TODO Not sure if this is the same as omics type... maybe need to put phospho instead
            ptmInputList = userdecryptMInputList
        }

        // if(userDatasets.map(d => d.datasetId).includes('mockDecryptE')){
        //     userDatasetTypes["mockDecryptM"] = "decryptE" //TODO This type is not recognized by PTMNav yet
        //     fpInputList = userdecryptEInputList
        // }


        return {
            ptmInputList,
            fpInputList,
            userDatasetTypes,
            organismOfFirstDataset : 9606
        }
    },

    async getInternalDatabaseData(selectedExperimentDesigns) {
        if (selectedExperimentDesigns !== 42) {
            console.log('Mock backend only has experiment 42!')
        }

        return { ptmInputList:InternalDatabasePTMInputList, fpInputList:InternalDatabaseFPInputList }

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
    async getInternalDatabaseEnrichmentResults(experimentDesignIds) {
        if (experimentDesignIds !== '42') {
            console.log('Mock backend only has experiment 42!')
        }
        return mockInternalDatabaseEnrichmentResults

    },
    async renewSession(uuid) {
        console.log(`Pretending to extend the following UUID: ${uuid}`)

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
