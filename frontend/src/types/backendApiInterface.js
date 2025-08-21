//Readme: If you add a new method to this interface, also add it to 'requiredMethods' in the validator below!
/**
 * @typedef {Object} BackendApiInterface
 * @property {() => String} getDefaultSessionId
 * @property {() => String} getBackendName
 * @property {(uuid: string||undefined) => RefreshSessionIdResult} refreshSessionId
 * @property {(uuid: string||undefined) => UserDataset[]} getUserDatasetList
 * @property {(uuid: string) => void} renewSession
 * @property {() => Organism[]} getOrganisms
 * @property {() => Project} getProjects
 * @property {(projectId: string) => ExperimentDesign[]} getExperimentDesigns
 * @property {(uuid: string) => CustomPathwayList[]} getCustomPathwayList
 * @property {(taxcode: string) => CanonicalPathwayList[]} getCanonicalPathwayList
 * @property {(taxcode: string, canonicalPathwayLink: string) => RawPathwaySkeleton} getPathwaySkeleton
 * @property {(uuid: string, userDatasets: Array) => UserProteomicsData} getUserProteomicsData
 * @property {(selectedExperimentDesigns: ExperimentDesign[]) => InternalDatabaseData} getInternalDatabaseData
 * @property {(skeleton: String, uuid: String, customPathwayName: string, currentlyEditedPathwayId: string|undefined) => number} storeCustomPathway
 * @property {(searchStrings: String[], taxcode: String) => Array} getFilteredPathwayIds
 * @property {() => String} getCustomDataUploadComponent
 * @property {(sessionId: String, userDatasetIds: String, enrichmentTypeId: String) => Object} getUserEnrichmentResults
 * @property {(experimentDesignIds: String) => Object} getInternalDatabaseEnrichmentResults
 * @property {(curveIds: Array) => Array} getCurveData
 */


/**
 * @typedef RefreshSessionIdResult
 * @property {number} cookieStatus
 * @property {string} uuid
 */

/**
 * @typedef UserDataset
 * @property {string} datasetName
 * @property {string} datasetId
 * @property {string} omicsType
 */

/**
 * @typedef Organism
 * @property {string} name
 * @property {string} taxcode
 */

/**
 * @typedef Project
 * @property {string} projectName
 * @property {string} projectId
 */

/**
 * @typedef ExperimentDesign
 * @property {string} datasetName
 * @property {string} datasetId
 * @property {string} omicsType
 */

/**
 * @typedef CustomPathwayList
 * @property {string} pathwayName
 * @property {string} pathwayId
 * @property {string} pathwayJSON
 */

/**
 * @typedef CanonicalPathwayList
 * @property {string} title
 * @property {string} name
 * @property {string} link
 */

/**
 * @typedef RawPathwaySkeleton
 * @property {RawPathwaySkeletonMetadata} pathway
 * @property {Array} nodes //TODO: Create explicit types for these
 * @property {Array} links
 */

/**
 * @typedef RawPathwaySkeletonMetadata
 * @property {string} name
 * @property {string} org
 * @property {string} title
 */

/**
 * @typedef UserProteomicsData
 * @property {Array} ptmInputList
 * @property {Array} fpInputList
 * @property {Object} userDatasetTypes
 * @property {String} organismOfFirstDataset
 */

/**
 * @typedef InternalDatabaseData
 * @property {Array} ptmInputList
 * @property {Array} fpInputList
 */



export function apiValidator(api) {
    //For now, only check that every method is implemented
    //This does not test if the signature of the method is correct, but enough is enough...
    const requiredMethods = [
        'getDefaultSessionId',
        'getBackendName',
        'refreshSessionId',
        'getUserDatasetList',
        'renewSession',
        'getOrganisms',
        'getProjects',
        'getExperimentDesigns',
        'getCustomPathwayList',
        'getCanonicalPathwayList',
        'getPathwaySkeleton',
        'getUserProteomicsData',
        'getInternalDatabaseData',
        'storeCustomPathway',
        'getFilteredPathwayIds',
        'getCustomDataUploadComponent',
        'getUserEnrichmentResults',
        'getInternalDatabaseEnrichmentResults',
        'getCurveData',
    ];
    return requiredMethods.every((method) => {
        const functionExists = typeof api[method] === 'function'
        if (!functionExists) {
            console.error(`Your backend API needs to implement '${method}'!`)
        }
        return functionExists
    })
}

