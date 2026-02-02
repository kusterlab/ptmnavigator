/* eslint-disable */
/* Needed to do this bc there are some non-implemented endpoints which have to be there to pass the API validation,
but since they are empty eslint would complain about unused parameters
 */

import axios from 'axios'

const backendPort = process.env.VUE_APP_BACKEND_PORT || 4040 //Default in gunicorn.sh if not running via docker
const host = `http://localhost:${backendPort}`

const standaloneApi = {

    getBackendName() {
        return 'Internal Database (SQLite)'
    },

    async getOrganisms() {
        return (await axios.get(
                `${host}/api/get_organisms`)
        ).data
    },


    getDefaultSessionId() {
        return '0123456789ABCDEF0123456789ABCDEF'
    },

    async refreshSessionId(uuid) {
        //TODO: When I manually input a valid id it gets overwritten, maybe bc it does not exist? No, also if it does!
        return (await axios.get(`${host}/api/refresh_session`,
            {params: {uuid}})).data
    },

    async getUserDatasetList(uuid) {
        return (await axios.get(
                `${host}/api/get_user_dataset_list`,
                {params: {uuid}})
        ).data
    },

    async loadUserDatasets(sessionId, userDatasets) {
        const datasetIds = userDatasets.map(dataset => dataset.datasetId).join(';')
        return (await axios.get(
                `${host}/api/get_user_datasets`,
                {params: {sessionId, datasetIds}})
        ).data

    },

    async getInternalProjects() {
        //No internal datasets right now
        return [];

    },

    async getInternalDatasetsForProject(projectId) {
        //No internal datasets right now
    },

    async loadInternalDatasets(selectedDatasets) {
        //No internal datasets right now
    },

    async getCanonicalPathwayList(taxcode) {
        return (await axios.get(
                `${host}/api/get_canonical_pathway_list`,
                {params: {taxcode}})
        ).data

    },

    async getCustomPathwayList(uuid) {
        return (await axios.get(
                `${host}/api/get_custom_pathway_list`,
                {params: {uuid}})
        ).data
    },

    async getPathwaySkeleton(canonicalPathwayName) {
        return (await axios.get(
                `${host}/api/get_pathway_skeleton`,
                {params: {pathwayName: canonicalPathwayName}})
        ).data

    },

    async storeCustomPathway(skeleton, uuid, customPathwayName, customPathwayId) {
        console.log(`Storing with ${uuid}`)
        await axios.put(`${host}/api/store_custom_pathway`,
            {data: skeleton},
            {params: {uuid, customPathwayName, customPathwayId}})
    },

    async getFilteredPathwayIds(searchStrings, taxcode) {
        return (await axios.get(
                `${host}/api/get_filtered_pathway_names`,
                {params: {searchStrings, taxcode}})
        ).data
    },

    async getEnrichmentTypes() {
        const enrichmentTypes = (await axios.get(
            `${host}/api/get_enrichment_types`)).data
        //Add individual enrichment types for KEA3 Mean and Top Rank
        //They do not get an enrichment type id because their results are not individually stored
        const kea3Index = enrichmentTypes.findIndex(et => et.name === 'KEA3')
        enrichmentTypes.push(
            {
                ...enrichmentTypes[kea3Index],
                "name": "KEA3 - Mean Rank",
                "short": "kea3_mean",
                'enrichmentTypeId': undefined
            },
            {
                ...enrichmentTypes[kea3Index],
                "name": "KEA3 - Top Rank",
                "short": "kea3_top",
                'enrichmentTypeId': undefined
            })
        //Remove original KEA3
        // enrichmentTypes.splice(kea3Index, 1)
        return enrichmentTypes
    },

    async loadUserEnrichmentResults(sessionId, userDatasetIdList, enrichmentTypeId) {
        //userDatasetIdList always has only one element
        const userDatasetId = userDatasetIdList[0]

        return (await axios.get(
                `${host}/api/get_user_enrichment_results`,
                {params: {sessionId, userDatasetId, enrichmentTypeId}})
        ).data
    },

    async loadInternalDatabaseEnrichmentResults(projectId, experimentDesignIds) {
        //Only user data for now

    },

    async loadCurveData(curveIDs, isUserDataMode) {
        //Backend expects the curveIDs as a ;-separated list
        curveIDs = curveIDs.join(';')
        return (await axios.get(
                `${host}/api/get_curve_data`,
                {params: {curveIDs, isUserDataMode}}) //isUserDataMode is always true right now I think
        ).data
    },

    getCustomDataUploadComponent() {
        return 'DataUpload';

    },

    async uploadDataset(formData, params) {
        const response = await axios.put(`${host}/api/upload_dataset`,
            formData,
            {params})

        return response;
    },

    async deleteDataset(uuid, datasetId) {
    },

    async performUserDatasetEnrichment(params) {
        const userProteomicsData = await this.loadUserDatasets(params.uuid, [{datasetId: params.datasetId}])
        //We only called loadUserDatasets with one datasetId, so we can assume that userProteomicsData also only contains one dataset
        const datasetInfo = userProteomicsData.datasetInfo[0]
        const isPhospho = datasetInfo['OMICS'] === 'Phosphorylation';
        const isPeptide = userProteomicsData['ptmInputList'].filter(datum => datum.details["Modified Sequence"]?.length > 0).length > 0


        //All Uniprot and Gene Name entries are singleton lists, for compatibility reasons
        //Extract those lists here to make the processing easier
        userProteomicsData.ptmInputList = userProteomicsData.ptmInputList.map(datum => {
            return {
                ...datum,
                geneNames: datum['geneNames']?.length > 0 ? datum['geneNames'][0] : null,
                uniprotAccs: datum['uniprotAccs']?.length > 0 ? datum['uniprotAccs'][0] : null,
            }
        })

        userProteomicsData.proteinInputList = userProteomicsData.proteinInputList.map(datum => {
            return {
                ...datum,
                geneNames: datum['geneNames']?.length > 0 ? datum['geneNames'][0] : null,
                uniprotAccs: datum['uniprotAccs']?.length > 0 ? datum['uniprotAccs'][0] : null,
            }
        })

        // Generate a queue of promised requests, then resolve them all
        const requestQueue = []
        if (isPhospho) {

            const preformattedRequestInput = isPeptide
                ? this.preformatEnrichmentInputPhosphoPeptide(userProteomicsData.ptmInputList)
                : this.preformatEnrichmentInputPhosphoSite(userProteomicsData.ptmInputList)

            const goEnrichmentRequestInput = this.formatEnrichmentInputForGO(preformattedRequestInput)
            requestQueue.push([goEnrichmentRequestInput, 'GO'])
            const gseaEnrichmentRequestInput = this.formatEnrichmentInputForGSEA(preformattedRequestInput, params.onlyRegulated)
            requestQueue.push([gseaEnrichmentRequestInput, 'GC-PEA'])
            requestQueue.push([gseaEnrichmentRequestInput, 'GCR-PEA'])
            const ptmseaEnrichmentRequestInput = this.formatEnrichmentInputForPTMSEA(preformattedRequestInput, params.onlyRegulated)
            requestQueue.push([ptmseaEnrichmentRequestInput, 'PTM-SEA'])
            const kseaEnrichmentRequestInput = this.formatEnrichmentInputForKSEA(preformattedRequestInput)
            requestQueue.push([kseaEnrichmentRequestInput, 'KSEA'])
            requestQueue.push([kseaEnrichmentRequestInput, 'RoKAI'])
            // PHONEMES needs the RoKAI-KSEA output, so we need to chain those two requests
            // This needs to happen in the backend though, because if we wait for it here the request is aborted in case
            // the user leaves the page before RoKAI-KSEA runs through.
            const phonemesRequestInput = this.formatEnrichmentInputForPHONEMeS(preformattedRequestInput)
            requestQueue.push([{
                rokai: kseaEnrichmentRequestInput,
                phonemes: phonemesRequestInput
            }, 'RoKAI-KSEA+PHONEMeS'])

            // Motif Enrichment, KEA3, and KSTAR only work for H. sapiens
            if (params.taxcode === 9606) {
                const motifEnrichmentInput = this.formatEnrichmentInputForMotifEnrichment(preformattedRequestInput)
                requestQueue.push([motifEnrichmentInput, 'MOTIF'])
                const kea3Input = this.formatEnrichmentInputForKEA3(preformattedRequestInput)
                requestQueue.push([kea3Input, 'KEA3'])

                // K-STAR does not work for site-level data, because it needs sequences
                if (isPeptide) {
                    const kstarInput = this.formatEnrichmentInputForKSTAR(preformattedRequestInput)
                    requestQueue.push([kstarInput, 'KSTAR'])
                }
            }


        } else if (userProteomicsData.ptmInputList.length > 0) {
            const nonPhosphoGseaEnrichmentInput = this.preformatEnrichmentInputNonPhosphoForGSEA(userProteomicsData.ptmInputList, params.onlyRegulated)
            requestQueue.push([nonPhosphoGseaEnrichmentInput, 'GC-PEA'])
            requestQueue.push([nonPhosphoGseaEnrichmentInput, 'GCR-PEA'])
            const nonPhosphoGOEnrichmentInput = this.preformatEnrichmentInputNonPhosphoForGO(userProteomicsData.ptmInputList)
            requestQueue.push([nonPhosphoGOEnrichmentInput, 'GO'])
        } else if (userProteomicsData.proteinInputList.length > 0) {
            // Full Proteome Data can be processed same as non-Phospho PTMs: Only GC, GCR, and GO can be performed.
            const fullProtGseaEnrichmentInput = this.preformatEnrichmentInputNonPhosphoForGSEA(userProteomicsData.proteinInputList, params.onlyRegulated)
            requestQueue.push([fullProtGseaEnrichmentInput, 'GC-PEA'])
            requestQueue.push([fullProtGseaEnrichmentInput, 'GCR-PEA'])
            const fullProtGOEnrichmentInput = this.preformatEnrichmentInputNonPhosphoForGO(userProteomicsData.proteinInputList)
            requestQueue.push([fullProtGOEnrichmentInput, 'GO'])
        }

        requestQueue.map(requestTuple => this.runAndStoreEnrichment(
            {
                sessionId: params.uuid,
                datasetName: params.datasetName,
                datasetId: params.datasetId,
                taxcode: params.taxcode,
                enrichmentInput: requestTuple[0],
                enrichmentType: requestTuple[1]
            }))

    },

    async runAndStoreEnrichment({sessionId, datasetName, datasetId, taxcode, enrichmentInput, enrichmentType}) {

        const taxcodeToOrganism = {
            9606: 'hsa',
            10090: 'mmu'
        }

        const enrichmentTypeToEndpoint = {
            'GC-PEA': 'ssgsea/gc',
            'GCR-PEA': 'ssgsea/gcr',
            'PTM-SEA': 'ssgsea/ssc/uniprot',
            KSEA: 'ksea',
            KEA3: 'kea3',
            KSTAR: 'kstar',
            'RoKAI+KSEA': 'ksea/rokai',
            MOTIF: 'motif_enrichment',
            PHONEMeS: 'phonemes',
            RoKAI: 'rokai',
            GO: 'go_enrichment'
        };

        if (!taxcode in taxcodeToOrganism) {
            throw `Enrichment not implemented for taxcode ${taxcode}!`
        }
        const organism = taxcodeToOrganism[taxcode];

        //Send request to enrichment server and store the results
        if (enrichmentType !== 'RoKAI-KSEA+PHONEMeS') {
            const endpoint = enrichmentTypeToEndpoint[enrichmentType];
            const enrichmentResponseJSON = await this.sendEnrichmentServerRequest(sessionId, datasetName, enrichmentInput, endpoint, organism);
            await this.storeUserEnrichmentResult(datasetId, enrichmentType, enrichmentResponseJSON);
        } else {
            // 'RoKAI-KSEA+PHONEMeS' is handled differently, because PHONEMeS needs the output of RoKAI,
            // but we don't want to send to separate requests - that would cause problems if the user leaves the frontend page
            // before RoKAI is finished.
            const rokaiEndpoint = enrichmentTypeToEndpoint['RoKAI+KSEA'];
            const rokaiResponseJSON = await this.sendEnrichmentServerRequest(sessionId, datasetName, enrichmentInput.rokai, rokaiEndpoint, organism);
            await this.storeUserEnrichmentResult(datasetId, 'RoKAI+KSEA', rokaiResponseJSON);
            // PHONEMeS only works for homo sapiens for now
            if (organism === 'hsa') {
                const phonemesInput = this.formatPHONEMeSInput(
                    enrichmentInput.phonemes.sites,
                    enrichmentInput.phonemes.experiments,
                    rokaiResponseJSON);
                const phonemesResponseJSON = await this.sendEnrichmentServerRequest(sessionId, datasetName, phonemesInput, enrichmentTypeToEndpoint.PHONEMeS, organism);
                await this.storePHONEMeSResults(sessionId, datasetName, phonemesResponseJSON);
            }
        }
    },

    //TODO: All of these are helper functions to preprocess the enrichment input. Could be outsourced into a separate file
    async sendEnrichmentServerRequest(sessionId, datasetName, enrichmentInput, endpoint, organism) {
        const enrichmentServerUrl = process.env.VUE_APP_ENRICHMENT_SERVER_URL || 'https://enrichment.kusterlab.org/main_enrichment-server/'
        const formData = new FormData()
        formData.append('data', JSON.stringify(enrichmentInput))
        const response = await axios.post(`${enrichmentServerUrl}${endpoint}`,
            formData,
            {
                params: {
                    // data: JSON.stringify(enrichmentInput),
                    session_id: sessionId,
                    dataset_name: datasetName,
                    organism: organism
                }
            }
        )
        return response.data //Maybe need to stringify

    },

    async storeUserEnrichmentResult(datasetId, enrichmentType, enrichmentResponseJSON) {
        return axios.put(`${host}/api/store_user_enrichment_result`,
            {data: enrichmentResponseJSON},
            {params: {datasetId, enrichmentType}});
    },

    storePHONEMeSResults(sessionId, datasetName, phonemesResponseJSON) {
        try {
            // TODO: Investigate double parse and eliminate it
            let pathway_skeletons_list = JSON.parse(JSON.parse(phonemesResponseJSON));

            // Since version 0.1.1, the enrichment server returns the output wrapped in 'Result' in order to also send metadata
            // For legacy reasons we still support the old format
            if (pathway_skeletons_list.Result) {
                pathway_skeletons_list = pathway_skeletons_list.Result;
            }

            pathway_skeletons_list.forEach(skeleton => {
                const experimentName = skeleton.pathway.name;
                this.storeCustomPathway(
                    JSON.stringify(skeleton),
                    sessionId,
                    `PHONEMeS-Pathway-${datasetName}-${experimentName}`,
                    undefined)
            });
        } catch (err) {
            throw `Exception occurred: ${err}. Probably the PHONEMeS result was empty. Raw PHONEMeS Response: ${phonemesResponseJSON}`
        }
    },

    formatPHONEMeSInput(sites, experiments, kseaResponse) {
        // Try to get the top 3 kinases of each experiment by summed absolute score
        const targetsInput = {};
        try {


            // Since version 0.1.1, the enrichment server returns the output wrapped in 'Result' in order to also send metadata
            // For legacy reasons we still support the old format
            if (kseaResponse.Result) {
                kseaResponse = kseaResponse.Result;
            }

            experiments.forEach(experiment => {
                targetsInput[experiment] = {up: [], down: []};
                const kseaScoresExperiment = kseaResponse.map(entry => {
                    return {
                        Gene: entry.Gene,
                        Score: entry[`Score (${experiment})`]
                    };
                });
                kseaScoresExperiment.sort((a, b) => Math.abs(b.Score) - Math.abs(a.Score));
                kseaScoresExperiment.slice(0, 3).forEach(
                    entry => entry.Score > 0 ? targetsInput[experiment].up.push(entry.Gene) : targetsInput[experiment].down.push(entry.Gene)
                );
            });
        } catch (err) {
            console.error(err)
            return null;
        }

        return {
            targets: targetsInput,
            sites: sites
        };
    },

    preformatEnrichmentInputPhosphoPeptide(peptideData) {
        /**
         * This function transforms the peptideData into the following format:
         * [
         *    {"Experiment":"E1","Expression":-1.61,"siteKSEA":"Q9NS69_S44","sitePTMSEA":"Q9NS69;S44-p","id":"TOM22", "Regulation": 'down', 'Modified sequence': "RSD(ph)ASYR"},
         *    {"Experiment":"E2","Expression":7.79,"siteKSEA":"Q9NS69_S44","sitePTMSEA":"Q9NS69;S44-p","id":"TOM22", "Regulation": 'up', 'Modified sequence': "RSD(ph)ASYR"},
         *    {"Experiment":"E1","Expression":7.79,"siteKSEA":"P47755_S1529","sitePTMSEA":"P47755;S1529-p","id":"CAPZA2", "Regulation": 'not', 'Modified sequence': "RSD(ph)ASYR"}
         * ]
         */


        return peptideData
            .filter(datum => {
                // Throw out rows without valid values
                if (!(datum.details["Modified Sequence"]?.length > 0) || !datum.details["Modified Site(s)"]) {
                    return false
                }

                // Everything regulated always passes
                if (datum.regulation === 'up' || datum.regulation === 'down') {
                    return true
                }

                // For not regulated, is passes if its R2 is large enough (or if it is non-decryptM, in that case it has no R2 and also passes)
                return !datum.details.R2 || datum.details.R2 > 0.7
            })
            .map(datum => {
                return datum.details["Modified Site(s)"].map(siteIdentifier => {
                    return {
                        Experiment: datum.details['Experiment Name'],
                        Expression: Number(datum.details['Log Fold Change']),
                        siteKSEA: siteIdentifier,
                        sitePTMSEA: siteIdentifier.replace('_', ';') + '-p',
                        sitePHONEMeS: datum['geneNames'] + '_' + siteIdentifier.split('_')[1],
                        Regulation: datum.regulation,
                        ModSequence: datum.details['Modified Sequence'],
                        id: datum['geneNames'],
                        Uniprot: datum['uniprotAccs']
                    }
                })

            }).flat()
    },

    preformatEnrichmentInputPhosphoSite(siteData) {
        // Same as previous function, but for site-level data (therefore, no modified sequence)
        return siteData
            .filter(datum => {
                // Throw out rows without valid values
                if (!datum.details["Modified Site(s)"]) {
                    return false
                }

                // Everything regulated always passes
                if (datum.regulation !== '-') {
                    return true
                }

                // For not regulated, is passes if its R2 is large enough (or if it is non-decryptM, in that case it has no R2 and also passes)
                return !datum.details.R2 || datum.details.R2 > 0.7
            }).map(datum => {
                return datum.details["Modified Site(s)"].map(siteIdentifier => {
                    return {
                        Experiment: datum.details['Experiment Name'],
                        Expression: Number(datum.details['Log Fold Change']),
                        siteKSEA: siteIdentifier,
                        sitePTMSEA: siteIdentifier.replace('_', ';') + '-p',
                        sitePHONEMeS: datum['geneNames'] + '_' + siteIdentifier.split('_')[1],
                        Regulation: datum.regulation,
                        id: datum['geneNames'],
                        Uniprot: datum['uniprotAccs']

                    }
                })

            }).flat()
    },

    preformatEnrichmentInputNonPhosphoForGSEA(data, onlyRegulated) {
        /**
         * This function transforms the peptideData or fullProteomeData returned by a getUserProteomicsData into the following format:
         * [{"id":"EGFR","E1":-1.61},{"id":"MAPK1","E2":7.79},{"id":"EGFR","E1":7.79}]
         */
        return data
            .filter(datum => !!datum && (!onlyRegulated || datum.regulation === 'up' || datum.regulation === 'down'))
            .filter(datum => datum.geneNames && datum.geneNames.length > 0)
            .map(datum => {
                return {
                    id: datum.geneNames,
                    [datum.details["Experiment Name"]]: Number(datum.details["Log Fold Change"])
                }
            })
    },

    preformatEnrichmentInputNonPhosphoForGO(data) {
        /**
         * Transforms non-phospho PTM data or fullproteome data into the following format:
         * {"Experiment01": ["SMAD9","FOXM1"],"Experiment02": ["LALA"], "Background": ["SMAD9", "FOXM1", "XOXO", "TMPO", "LALA"]}
         */
        const result = {Background: new Set()}

        data
            .forEach(datum => {
                const id = datum.geneNames
                const experiment = datum.details["Experiment Name"]
                if (id) {
                    if (['up', 'down'].indexOf(datum.regulation) !== -1) {
                        if (!result[experiment]) {
                            result[experiment] = new Set()
                        }
                        result[experiment].add(id)
                    }
                    result.Background.add(id)
                }
            })

        Object.keys(result).forEach(experimentOrBackground => {
            result[experimentOrBackground] = [...result[experimentOrBackground]]
        })
        return result
    },

    formatEnrichmentInputForGO(unformattedInput) {
        /**
         * This function reshapes a list of objects in the following way:
         * [{"Experiment":"E1",'id':"SMAD9", "Regulation": 'up'},
         {"Experiment":"E1",'id':"FOXM1", "Regulation": 'down'},
         {"Experiment":"E1",'id':"XOXO", "Regulation": '-'},
         {"Experiment":"E2",'id':"TMPO", "Regulation": '-'},
         {"Experiment":"E2",'id':"LALA", "Regulation": 'down'},
         * ...
         * ]
         * ==>
         * {"Experiment01": ["SMAD9","FOXM1"],"Experiment02": ["LALA"], "Background": ["SMAD9", "FOXM1", "XOXO", "TMPO", "LALA"]}
         *
         * So, everything that is 'up' or 'down' gets placed in the respective experiment's data.
         * And everything overall gets placed in 'Background'
         */

        const result = {Background: new Set()}

        unformattedInput.forEach(item => {
            const {Experiment, id, Regulation} = item
            if (['up', 'down'].indexOf(Regulation) !== -1) {
                if (!result[Experiment]) {
                    result[Experiment] = new Set()
                }
                if (id) {
                    result[Experiment].add(id)
                }
            }
            if (id) {
                result.Background.add(id)
            }
        })

        Object.keys(result).forEach(experimentOrBackground => {
            result[experimentOrBackground] = [...result[experimentOrBackground]]
        })
        return result
    },

    formatEnrichmentInputForGSEA(unformattedInput, onlyRegulated) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1","Expression":-1.61,"id":"EGFR"},
         *    {"Experiment":"E2","Expression":7.79,"id":"MAPK1"},
         *    {"Experiment":"E1","Expression":7.79,"id":"EGFR"}
         * ]
         * ==>
         * [{"id":"EGFR","E1":-1.61},{"id":"MAPK1","E2":7.79},{"id":"EGFR","E1":7.79}]
         *
         * Note the difference to the KSEA formatting method: Duplicates are allowed, and
         * there is only one experiment per object
         *
         * In a GSEA, we do not have to include all peptides, so we filter for regulated
         */
        return unformattedInput
            .filter(datum => !!datum && (!onlyRegulated || datum.Regulation === 'up' || datum.Regulation === 'down'))
            .map(item => {
                const {Experiment, id, Expression} = item
                if (id) {
                    const res = {}
                    res.id = id
                    res[Experiment] = Expression
                    return res
                }
                return null
            }).filter(datum => !!datum)
    },

    formatEnrichmentInputForPTMSEA(unformattedInput, onlyRegulated) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1","Expression":-1.61,"Site":"Q9NS69_S44"},
         *    {"Experiment":"E2","Expression":7.79,"Site":"Q9NS69_S44"},
         *    {"Experiment":"E1","Expression":7.79,"Site":"P07902;S1529-p"}
         * ]
         * ==>
         * [{"Site":"Q9NS69_S44","E1":-1.61},{"Site":"Q9NS69_S44","E2":7.79},{"Site":"P07902;S1529-p","E1":7.79}]
         *
         * In a PTM-SEA, we do not have to include all peptides, so we filter for regulated
         */
        return unformattedInput
            .filter(datum => !!datum && (!onlyRegulated || datum.Regulation === 'up' || datum.Regulation === 'down'))
            .map(item => {
                const {Experiment, sitePTMSEA, Expression} = item

                const Site = sitePTMSEA

                if (Site) {
                    const res = {}
                    res.Site = Site
                    res[Experiment] = Expression
                    return res
                }
                return null
            }).filter(datum => !!datum)
    },

    formatEnrichmentInputForKSEA(unformattedInput) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1","Expression":-1.61,"Site":"Q9NS69_S44"},
         *    {"Experiment":"E2","Expression":7.79,"Site":"Q9NS69_S44"},
         *    {"Experiment":"E1","Expression":7.79,"Site":"P07902;S1529-p"}
         * ]
         * ==>
         * [{"Site":"Q9NS69_S44","E1":-1.61},{"Site":"Q9NS69_S44","E2":7.79},{"Site":"P07902;S1529-p","E1":7.79}]
         *
         * In a KSEA, we have to include all peptides, regulated and unregulated, so there is no filtering
         */
        return unformattedInput.map(item => {
            const {Experiment, siteKSEA, Expression} = item

            const Site = siteKSEA

            if (Site) {
                const res = {}
                res.Site = Site
                res[Experiment] = Expression
                return res
            }
            return null
        }).filter(datum => !!datum)
    },

    formatEnrichmentInputForKSTAR(unformattedInput) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1",'ModSequence':"RSD(ph)ASYR", 'Expression':0.987, "Uniprot":"E9PCX8;Q68CZ2;Q68CZ2-2"},
         * ...
         * ]
         * ==>
         * [{"Modified sequence":"RSD(ph)ASYR","E1":0.987, "Proteins":"E9PCX8;Q68CZ2;Q68CZ2-2"},...]
         *
         * In KSTAR we filter for up/down
         */

        return unformattedInput
            .filter(item => item.ModSequence !== '' && ['up', 'down'].indexOf(item.Regulation) !== -1)
            .map(item => {
                const {Experiment, ModSequence, Uniprot, Expression} = item
                const res = {}
                res['Modified sequence'] = ModSequence
                res[Experiment] = Expression
                res.Proteins = Uniprot
                return res
            })
    },

    formatEnrichmentInputForKEA3(unformattedInput) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1",'id':"SMAD9"},{"Experiment":"E1",'id':"FOXM1"},{"Experiment":"E2",'id':"TMPO"},
         * ...
         * ]
         * ==>
         * {"Experiment01": ["FOXM1","SMAD9"],"Experiment02": ["TMPO"]}
         *
         * We filter for up/down, since we only hand over gene names
         */

        const result = {}

        unformattedInput.forEach(item => {
            const {Experiment, id, Regulation} = item
            if (['up', 'down'].indexOf(Regulation) !== -1) {
                if (!result[Experiment]) {
                    result[Experiment] = new Set()
                }
                if (id) {
                    result[Experiment].add(id)
                }
            }
        })

        Object.keys(result).forEach(experiment => {
            result[experiment] = [...result[experiment]]
        })

        return result
    },

    formatEnrichmentInputForMotifEnrichment(unformattedInput) {
        /**
         * This function reshapes a list of objects in the following way:
         * [  {"Experiment":"E1",'ModSequence':"RSD(ph)ASYR", 'Regulation':'down', "Uniprot":"E9PCX8;Q68CZ2;Q68CZ2-2"},
         * ...
         * ]
         * ==>
         * [{"Modified sequence":"RSD(ph)ASYR","E1":'down', "Proteins":"E9PCX8;Q68CZ2;Q68CZ2-2"},...]
         *
         * In a Motif Enrichment, we filter for up/down/not
         */

        return unformattedInput
            .filter(item => item.ModSequence !== '' && ['up', 'down', 'not'].indexOf(item.Regulation) !== -1)
            .map(item => {
                const {Experiment, ModSequence, siteKSEA, Uniprot, Regulation} = item
                const res = {}
                // For Peptide-Level Data
                if (ModSequence) {
                    res['Modified sequence'] = ModSequence
                }
                // For Site-Level Data
                if (siteKSEA) {
                    res['Site positions'] = siteKSEA
                }
                res[Experiment] = Regulation
                res.Proteins = Uniprot
                return res
            })
    },

    formatEnrichmentInputForPHONEMeS(unformattedInput) {
        const allExperiments = []
        const sitesInput = unformattedInput.map(item => {
            const {Experiment, sitePHONEMeS, Expression, Regulation} = item
            allExperiments.push(Experiment)
            const Site = sitePHONEMeS

            if (Site && (Regulation === 'up' || Regulation === 'down')) {
                const res = {}
                res.Site = Site
                res[Experiment] = Expression
                return res
            }
            return null
        }).filter(datum => !!datum)
        return {experiments: [...new Set(allExperiments)], sites: sitesInput}
    },

}

export default standaloneApi