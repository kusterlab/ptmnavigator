//Readme: If you add a new method to this interface, also add it to 'requiredMethods' in the validator below!
/**
 * @typedef {Object} BackendApiInterface
 * @property {() => String} getDefaultSessionId
 * @property {() => String} getBackendName
 * @property {(uuid: string||undefined) => String} refreshSessionId
 * @property {(uuid: string||undefined) => Dataset[]} getUserDatasetList
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
 * @property {() => EnrichmentType[]} getEnrichmentTypes
 * @property {(sessionId: String, userDatasetIds: String, enrichmentTypeId: String) => Object} loadUserEnrichmentResults
 * @property {(projectId: String, experimentDesignIds: String) => Object} loadInternalDatabaseEnrichmentResults
 * @property {(curveIds: Array, isUserDataMode: Boolean) => Array} loadCurveData
 //TODO: Make Object types more precise
 * @property {(formData: FormData, params: Object) => Object} uploadDataset
 * @property {(params: Object) => null } performUserDatasetEnrichment
 * @property {(uuid: string, datasetId: number ) => null } deleteDataset
 */


/**
 * @typedef Dataset
 * @property {string} datasetName
 * @property {string} datasetId
 * @property {string} datasetType //TODO provide enumeration of possible values
 * @property {string} omics //TODO provide enumeration of possible values
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

/**
 * @typedef EnrichmentType
 * @property {string} name
 * @property {string} short
 * @property {number} enrichmentTypeId
 * @property {string[]} applicableOmics
 * @property {'KinaseActivity'|'Pathway'} enrichmentClass
 * @property {string} tooltipHtml
 * @property {string} parametersHtml
 * @property {string[]} stringColumns
 * @property {string} sortColumn
 * @property {boolean} sortDesc
 * @property {KAIDetails|undefined} kaiDetails //Needs to be KAIDetails if enrichmentClass === 'KinaseActivity', else it can be undefined
 */

/**
 * @typedef KAIDetails
 * @property {string} kinaseColname
 * @property {string|undefined} scoreColnamePrefix
 * @property {string|undefined} significanceColnamePrefix
 * @property {boolean} higherScoreIsStrongerEnrichment
 * @property {boolean} hasDirection
 * @property {boolean} directionFromSignificance
 * @property {boolean} isAlreadyLogTransformed
 */



export function apiValidator(api) {
    //For now, only check that every method is implemented
    //This does not test if the signature of the method is correct, but enough is enough...
    const requiredMethods = [
        'getDefaultSessionId',
        'getBackendName',
        'refreshSessionId',
        'getUserDatasetList',
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
        'loadUserEnrichmentResults',
        'loadInternalDatabaseEnrichmentResults',
        'loadCurveData',
        'uploadDataset',
        'performUserDatasetEnrichment',
        'deleteDataset'
    ];
    return requiredMethods.every((method) => {
        const functionExists = typeof api[method] === 'function'
        if (!functionExists) {
            console.error(`Your backend API needs to implement '${method}'!`)
        }
        return functionExists
    })
}

