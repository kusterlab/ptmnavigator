ptm_omics = ['Phosphorylation', 'Other']

# This can be applied to the regulation column to turn everything into up, down, not or NaN
regulation_variants_map = {
    'up': ['up', 'u', '+'],
    'down': ['down', 'd'],
    'not': ['not', '-'],
    None: [None, 'nan', 'none', 'null']
}
regulation_variants_lookup = {val: key for key, vals in regulation_variants_map.items() for val in vals}

expected_colnames_fcdata_map = {
    'Modified sequence': ['modifiedsequence', 'modsequence'],
    'Psite': ['psite', 'p-site'],
    'Gene Names': ['gene_names', 'genes', 'genenames'],
    'Uniprot': ['proteinids', 'proteins', 'uniprot', 'uniprot_acc'],
    'Regulation': ['regulation'],
    'Fold Change': ['foldchange', 'fc', 'logfc'],
    'Experiment': ['experiment'],
}
additional_expected_colnames_curve_map = {
    'pEC50': ['pec50'],
    'pEC50_Error': ['logec50error', 'pec50error'],
    'Slope': ['slope', 'curveslope'],
    'Front': ['front', 'curvefront'],
    'Back': ['back', 'curveback'],
    'Fold Change': ['curvefoldchange'],
    'Regulation': ['curveregulation'],
    'Curve q-Value': ['curveq_value', 'curveqvalue'],
    'Relevance Score': ['curverelevancescore', 'relevancescore'],
    'R2': ['curver2', 'curve_r2', 'r2']
}

# Blacklist of columns that appear in decryptM/CurveCurator files but should not be imported as Datum Details
curve_columns_not_imported = {'N duplicates', 'Score', 'Raw 1', 'Raw 2', 'Raw 3', 'Raw 4', 'Raw 5', 'Raw 6', 'Raw 7',
                              'Raw 8', 'Raw 9', 'Raw 10', 'Raw 11', 'Name', 'Imputation N', 'Imputation Position',
                              'Normalized 1', 'Normalized 2', 'Normalized 3', 'Normalized 4', 'Normalized 5',
                              'Normalized 6', 'Normalized 7', 'Normalized 8', 'Normalized 9', 'Normalized 10',
                              'Normalized 11', 'Ratio 1', 'Ratio 2', 'Ratio 3', 'Ratio 4', 'Ratio 5', 'Ratio 6',
                              'Ratio 7', 'Ratio 8', 'Ratio 9', 'Ratio 10', 'Ratio 11', 'Signal Quality', 'R2',
                              'Curve Front', 'Curve Back', 'Curve AUC', 'Curve RMSE', 'Curve Slope Error',
                              'Curve Front Error', 'Curve Back Error', 'Null Model', 'Null RMSE', 'Curve F_Value',
                              'Curve P_Value', 'Curve Log P_Value', 'Curve F_Value SAM Corrected', 'Curve q-Value'}

required_arguments_for_upload = ['uuid', 'datasetType', 'taxcode', 'omics', 'datasetName',
                                 'foldChangeDataFoldChangeScale']

curve_formula = "return $C$ + ($D$ -$C$) / (1 + Math.exp($B$* (Math.log(x) - Math.log($E$))));"
escape_character = ("$")
curve_generic_yaxis_label = 'Relative Response'

quan_details_not_imported = ['MODIFIED_SITE_ID']
quan_columns_imported = ['GENE_NAME', 'UNIPROT_ACC', 'REGULATION', 'EXPERIMENT', 'MODIFIED_SEQUENCE', 'DETAILS',
                         'USER_CURVE_ID']
