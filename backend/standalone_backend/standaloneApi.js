import axios from 'axios'

const host = 'http://localhost:3000' //TODO: Get from somewhere

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
        //TODO: ProteomicsDB returns the uuid here, I find that weird but maybe I have to for compatibility
        await axios.get(`${host}/api/refresh_session`,
            {params: {uuid}})
    },

    async getUserDatasetList(uuid) {
        return (await axios.get(
                `${host}/api/get_user_dataset_list`,
                {params: {uuid}})
        ).data
    },

    async loadUserDatasets(sessionId, userDatasets) {
        //TODO LATER
    },

    async getInternalProjects() {
        //TODO LATER
        return [];

    },

    async getInternalDatasetsForProject(projectId) {
//TODO LATER
    },

    async loadInternalDatasets(selectedDatasets) {
//TODO LATER
    },

    async getCanonicalPathwayList(taxcode) {
        return (await axios.get(
                `${host}/api/get_canonical_pathway_list`,
                {params: {taxcode}})
        ).data

    },

    async getCustomPathwayList(uuid) {
//TODO LATER
    },

    // async getPathwaySkeleton(taxcode, canonicalPathwayLink) {
    async getPathwaySkeleton(canonicalPathwayId) {
        //TODO: Change PTMNavigator so it sends an ID instead of a link
        // then the PrDB Backend needs to have a mapping from id to link or so.
        // Or rather send an additional query that converts the ID into a link
        // But it shouldn't be too hard to make PrDB send an ID as well and then construct the link
        return (await axios.get(
                `${host}/api/get_pathway_skeleton`,
                {params: {pathwayId: canonicalPathwayId}})
        ).data

    },

    async storeCustomPathway(skeleton, uuid, customPathwayName, currentlyEditedPathwayId) {

    },

    async getFilteredPathwayIds(searchStrings, taxcode) {
        return (await axios.get(
                `${host}/api/get_filtered_pathway_names`,
                {params: {searchStrings, taxcode}})
        ).data
    },

    async getEnrichmentTypes() {
    },

    async loadUserEnrichmentResults(sessionId, userDatasetIds, enrichmentTypeId) {
    },

    async loadInternalDatabaseEnrichmentResults(projectId, experimentDesignIds) {

    },

    async loadCurveData(curveIDs, isUserDataMode) {
    },

    getCustomDataUploadComponent() {
        return 'DataUpload';

    },

    async uploadDataset(formData, params) {
        const response = await axios.put(`${host}/api/upload_dataset`,
            formData,
            {params})

        console.log(response)
        //TODO: Return value must look like this:
        //          {
        //             data: {
        //                 datasetId: 1,
        //                 message: 'Success!'
        //             }
        //         }
        return response;
    },

    async performUserDatasetEnrichment(params) {
    },

    async deleteDataset(uuid, datasetId) {
    },

}

export default standaloneApi