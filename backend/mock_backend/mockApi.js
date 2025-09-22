import customPathwayList from './mock_data/customPathwayList.json'
import WP422 from './mock_data/WP422.json'
import userPtmInputList from  './mock_data/mockUserDatasetPTMInput.json'
import userProteinInputList from './mock_data/mockUserDatasetProteinInput.json'

import userdecryptMInputList from  './mock_data/mockUserDatasetDecryptMInput.json'
import userdecryptEInputList from './mock_data/mockUserDatasetDecryptEInput.json'

import InternalDatasetPTMInputList from './mock_data/mockInternalDatasetPTMInput.json'
import InternalDatasetProteinInputList from './mock_data/mockInternalDatasetProteinInput.json'
//TODO: Motif and KEA3 not available, haven't checked InternalDatabase datasets yet
import mockUserEnrichmentResults1 from './mock_data/mockUserEnrichmentResults1.json'
import mockUserEnrichmentResults2 from './mock_data/mockUserEnrichmentResults2.json'
import mockUserEnrichmentResults3 from './mock_data/mockUserEnrichmentResults3.json'
import mockUserEnrichmentResults4 from './mock_data/mockUserEnrichmentResults4.json'
import mockInternalDatasetEnrichmentResults from './mock_data/mockInternalDatasetEnrichmentResults.json'
import enrichmentTypeHTMLs from './mock_data/enrichmentTypeHTMLs.json'

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

    async refreshSessionId(uuid) {
        /**
         * In the mock backend, this function will only change any uuid to all 0s.
         * In a proper backend, it could also reset its expiry date and create a new one if no existing uuid is supplied
         */
        if (uuid !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
            uuid = '0'.repeat(32)
        }
        return uuid
    },

    async getUserDatasetList(uuid) {
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
                enrichmentClass: 'Pathway',
                tooltipHtml: enrichmentTypeHTMLs.ptmsea.tooltip,
                parametersHtml: enrichmentTypeHTMLs.ptmsea.parameters,
                stringColumns: ['Signature ID', 'Gene'],
                sortColumn: 'Score',
                sortDesc: true,
            },
            {
                name: 'GC-PEA',
                short: 'gc',
                enrichmentTypeId: 2,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway',
                tooltipHtml: enrichmentTypeHTMLs.gc.tooltip,
                parametersHtml: enrichmentTypeHTMLs.gc.parameters,
                stringColumns: ['Signature ID', 'Gene'],
                sortColumn: 'Score',
                sortDesc: true,
            },
            {
                name: 'GCR-PEA',
                short: 'gcr',
                enrichmentTypeId: 3,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway',
                tooltipHtml: enrichmentTypeHTMLs.gcr.tooltip,
                parametersHtml: enrichmentTypeHTMLs.gcr.parameters,
                stringColumns: ['Signature ID', 'Gene'],
                sortColumn: 'Score',
                sortDesc: true,
            },
            {
                name: 'KSEA',
                short: 'ksea',
                enrichmentTypeId: 4,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.ksea.tooltip,
                parametersHtml: enrichmentTypeHTMLs.ksea.parameters,
                stringColumns: ['Signature ID', 'Gene'],
                sortColumn: 'Score',
                sortDesc: true,
                kaiDetails: {
                    kinaseColname: 'Gene',
                    scoreColnamePrefix: 'Score',
                    significanceColnamePrefix: 'adj p-val',
                    higherScoreIsStrongerEnrichment: true,
                    hasDirection: true,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: false,
                }
            },
            {
                name: 'RoKAI+KSEA',
                short: 'ksea_rokai',
                enrichmentTypeId: 5,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.ksea_rokai.tooltip,
                parametersHtml: enrichmentTypeHTMLs.ksea_rokai.parameters,
                stringColumns: ['Signature ID', 'Gene'],
                sortColumn: 'Score',
                sortDesc: true,
                kaiDetails: {
                    kinaseColname: 'Gene',
                    scoreColnamePrefix: 'Score',
                    significanceColnamePrefix: 'adj p-val',
                    higherScoreIsStrongerEnrichment: true,
                    hasDirection: true,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: false,
                }
            },
            {
                name: 'MOTIF',
                short: 'motif',
                enrichmentTypeId: 6,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.motif.tooltip,
                parametersHtml: enrichmentTypeHTMLs.motif.parameters,
                stringColumns: ['Kinase'],
                sortColumn: '-Log10 p_value adjusted',
                sortDesc: true,
                kaiDetails: {
                    kinaseColname: 'Kinase',
                    scoreColnamePrefix: 'Log2 Enrichment',
                    significanceColnamePrefix: '-Log10 p_value adjusted',
                    higherScoreIsStrongerEnrichment: true,
                    hasDirection: true,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: true,
                }
            },
            {
                name: 'KEA3',
                short: 'kea3',
                enrichmentTypeId: 7,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: undefined, //Only KEA3's two subtypes have an enrichment Class
            },
            {
                name: 'KEA3 - Mean Rank',
                short: 'kea3_mean',
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.kea3.tooltip,
                parametersHtml: enrichmentTypeHTMLs.kea3.parameters,
                stringColumns: ['TF', 'Library', 'Overlapping_Genes'],
                sortColumn: 'Rank',
                sortDesc: false,
                kaiDetails: {
                    kinaseColname: 'TF',
                    scoreColnamePrefix: 'Score',
                    significanceColnamePrefix: undefined,
                    higherScoreIsStrongerEnrichment: false,
                    hasDirection: false,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: true,
                }
            },
            {
                name: 'KEA3 - Top Rank',
                short: 'kea3_top',
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.kea3.tooltip,
                parametersHtml: enrichmentTypeHTMLs.kea3.parameters,
                stringColumns: ['TF', 'Library', 'Overlapping_Genes'],
                sortColumn: 'Rank',
                sortDesc: false,
                kaiDetails: {
                    kinaseColname: 'TF',
                    scoreColnamePrefix: 'Score',
                    significanceColnamePrefix: undefined,
                    higherScoreIsStrongerEnrichment: false,
                    hasDirection: false,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: true,
                }
            },
            {
                name: 'KSTAR',
                short: 'kstar',
                enrichmentTypeId: 8,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.kstar.tooltip,
                parametersHtml: enrichmentTypeHTMLs.kstar.parameters,
                stringColumns: ['Kinase'],
                sortColumn: 'Kinase',
                sortDesc: false,
                kaiDetails: {
                    kinaseColname: 'Kinase',
                    scoreColnamePrefix: undefined,
                    significanceColnamePrefix: '',
                    higherScoreIsStrongerEnrichment: true,
                    hasDirection: true,
                    directionFromSignificance: true,
                    isAlreadyLogTransformed: true,
                }
            },
            {
                name: 'RoKAI',
                short: 'rokai',
                enrichmentTypeId: 9,
                applicableOmics: ['Phosphorylation'],
                enrichmentClass: 'KinaseActivity',
                tooltipHtml: enrichmentTypeHTMLs.rokai.tooltip,
                parametersHtml: enrichmentTypeHTMLs.rokai.parameters,
                stringColumns: ['Gene'],
                sortColumn: 'ZScore',
                sortDesc: true,
                kaiDetails: {
                    kinaseColname: 'Gene',
                    scoreColnamePrefix: 'ZScore',
                    significanceColnamePrefix: 'FDR',
                    higherScoreIsStrongerEnrichment: true,
                    hasDirection: true,
                    directionFromSignificance: false,
                    isAlreadyLogTransformed: false,
                }
            },
            {
                name: 'GO',
                short: 'go',
                enrichmentTypeId: 10,
                applicableOmics: ['Phosphorylation', 'Protein', 'Other'],
                enrichmentClass: 'Pathway',
                tooltipHtml: enrichmentTypeHTMLs.go.tooltip,
                parametersHtml: enrichmentTypeHTMLs.go.parameters,
                stringColumns: ['GO_ID', 'Name', 'Intersection'],
                sortColumn: '',
                sortDesc: true,
            },
        ]
    },

    async loadUserEnrichmentResults(sessionId, userDatasetIds, enrichmentTypeId) {
        if (sessionId !== '0'.repeat(32)) {
            console.log(`Mock Backend only has UUID ${'0'.repeat(32)}!`)
            return null
        }
        else if(userDatasetIds[0] === 1){
            return mockUserEnrichmentResults1[enrichmentTypeId]
        }
        else if(userDatasetIds[0] === 2){
            return mockUserEnrichmentResults2[enrichmentTypeId]
        }
        else if(userDatasetIds[0] === 3){
            return mockUserEnrichmentResults3[enrichmentTypeId]
        } else if (userDatasetIds[0] === 4) {
            return mockUserEnrichmentResults4[enrichmentTypeId]
        } else {
            console.log(`Mock Backend only has enrichment for the Mock PTM Dataset with IDs 1,3`)
            return null
        }

    },
    //TODO: Currently the format of the mock dataset here is different then from user dataset enrichment results
    //We could align that, it creates confusion
    async loadInternalDatabaseEnrichmentResults(projectId, experimentDesignIds) {
        if (experimentDesignIds !== '42') {
            console.log('Mock backend only has experiment 42!')
        }
        return mockInternalDatasetEnrichmentResults

    },

    async loadCurveData(curveIDs, isUserDataMode) {
        if (!curveIDs || curveIDs.length === 0) {
            return [];
        }
        if (!isUserDataMode) {
            console.log('Mock backend currently only has curves for user data')
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
