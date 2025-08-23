import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import userPtmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import userProteinInputList from './mock_data/mockUserDatasetProteinInput.json'

import userdecryptMInputList from  './mock_data/mockUserDatasetDecryptMInput.json'
import userdecryptEInputList from './mock_data/mockUserDatasetDecryptEInput.json'

import InternalDatasetPTMInputList from './mock_data/mockInternalDatasetPTMInput.json'
import InternalDatasetProteinInputList from './mock_data/mockInternalDatasetProteinInput.json'
//TODO: Motif and KEA3 not available, haven't checked InternalDatabase datasets yet
import mockUserEnrichmentResults from './mock_data/mockUserEnrichmentResults.json'
import mockInternalDatasetEnrichmentResults from './mock_data/mockInternalDatasetEnrichmentResults.json'


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
                {
                    datasetName: "MockPTMDataset",
                    datasetId: 1,
                    datasetType: "FoldChange",
                    omics: 'Phosphorylation',
                    taxcode: 9606
                },
                {
                    datasetName: "MockProteinDataset",
                    datasetId: 2,
                    datasetType: "FoldChange",
                    omics: 'Protein',
                    taxcode: 9606
                },
                {
                    datasetName: "MockDecryptMDataset",
                    datasetId: 3,
                    datasetType: "Curve",
                    omics: 'Phosphorylation',
                    taxcode: 9606
                },
                {
                    datasetName: "MockDecryptEDataset",
                    datasetId: 4,
                    datasetType: "Curve",
                    omics: 'Protein',
                    taxcode: 9606
                }
            ]
        }
    },

    /**
     * Session ID is added as additional parameter for security reasons - otherwise, a third party could access a user dataset by guessing the ID
     * The 32-Digit Session ID is much harder to guess
     * @param sessionId
     * @param userDatasets
     * @returns {Promise<{proteinInputList: *[], ptmInputList: *[]}>}
     */
    async loadUserDatasets(sessionId, userDatasets) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
        }
        let ptmInputList = [];
        let proteinInputList = []


        if (userDatasets.map(d => d.datasetId).includes(1)) {
            ptmInputList = ptmInputList.concat(userPtmInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(2)) {
            proteinInputList = proteinInputList.concat(userProteinInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(3)) {
            ptmInputList = ptmInputList.concat(userdecryptMInputList)
        }

        if (userDatasets.map(d => d.datasetId).includes(4)) {
            proteinInputList = proteinInputList.concat(userdecryptEInputList)
        }

        return {
            ptmInputList,
            proteinInputList
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
            datasetType: 'FoldChange',
            omics: 'Phosphorylation',
            taxcode: 9606
        },
            {
                datasetName: "MockInternalProteinDataset",
                datasetId: 43,
                datasetType: 'FoldChange',
                omics: 'Protein',
                taxcode: 9606
            }
        ]
    },

    async loadInternalDatasets(selectedDatasets) {
        let ptmInputList = [];
        let proteinInputList = []

        if (selectedDatasets.map(d => d.datasetId).includes(42)) {
            ptmInputList = ptmInputList = ptmInputList.concat(InternalDatasetPTMInputList)
        }

        if (selectedDatasets.map(d => d.datasetId).includes(43)) {
            proteinInputList = proteinInputList.concat(InternalDatasetProteinInputList)
        }

        return {
            ptmInputList,
            proteinInputList
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

    async getEnrichmentTypes() {
        return [
            {
                name: 'PTM-SEA',
                short: 'ptmsea',
                enrichmentTypeId: 1,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'Pathway'
            },
            {
                name: 'GC-PEA',
                short: 'gc',
                enrichmentTypeId: 2,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway'
            },
            {
                name: 'GCR-PEA',
                short: 'gcr',
                enrichmentTypeId: 3,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway'
            },
            {
                name: 'GO',
                short: 'go',
                enrichmentTypeId: 10,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway'
            },
            {
                name: 'KSEA',
                short: 'ksea',
                enrichmentTypeId: 4,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            },
            {
                name: 'RoKAI+KSEA',
                short: 'ksea_rokai',
                enrichmentTypeId: 5,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            },
            {
                name: 'MOTIF',
                short: 'motif',
                enrichmentTypeId: 6,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            },
            {
                name: 'KEA3',
                short: 'kea3',
                enrichmentTypeId: 7,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            },
            {
                name: 'KSTAR',
                short: 'kstar',
                enrichmentTypeId: 8,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            },
            {
                name: 'RoKAI',
                short: 'rokai',
                enrichmentTypeId: 9,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity'
            }
        ]
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
        return mockInternalDatasetEnrichmentResults

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
