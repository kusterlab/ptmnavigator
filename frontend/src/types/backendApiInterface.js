//Readme: If you add a new method to this interface, also add it to 'requiredMethods' in the validator below!
/**
 * @typedef {Object} BackendApiInterface
 * @property {() => String} getDefaultSessionId
 * @property {() => String} getBackendName
 * @property {(uuid: string||undefined) => RefreshSessionIdResult} refreshSessionId
 * @property {(uuid: string||undefined) => Dataset[]} getUserDatasetList
 * @property {(uuid: string) => void} renewSession
 * @property {() => Organism[]} getOrganisms
 * @property {() => Project} getInternalProjects
 * @property {(projectId: string) => Dataset[]} getInternalDatasetsForProject
 * @property {(uuid: string) => CustomPathwayList[]} getCustomPathwayList
 * @property {(taxcode: string) => CanonicalPathwayList[]} getCanonicalPathwayList
 * @property {(taxcode: string, canonicalPathwayLink: string) => RawPathwaySkeleton} getPathwaySkeleton
 * @property {(uuid: string, userDatasets: Dataset[]) => LoadedData} loadUserDatasets
 * @property {(selectedDatasets: Dataset[]) => LoadedData} loadInternalDatasets
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
 * @typedef Dataset
 * @property {string} datasetName
 * @property {string} datasetId
 * @property {string} omicsType
 * @property {number} taxcode
 */

/**
 * @typedef Organism
 * @property {string} name
 * @property {number} taxcode
 */

/**
 * @typedef Project
 * @property {string} projectName
 * @property {string} projectId
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
 * @typedef LoadedData
 * @property {Array} ptmInputList //TODO: Need to make clear what are the mandatory fields for these (probably the same for both so you could create a type)
 * @property {Array} proteinInputList
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
        'getInternalProjects',
        'getInternalDatasetsForProject',
        'getCustomPathwayList',
        'getCanonicalPathwayList',
        'getPathwaySkeleton',
        'loadUserDatasets',
        'loadInternalDatasets',
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

