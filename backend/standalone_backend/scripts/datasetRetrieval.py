from . import db_utils, constants
import pandas as pd


def load_user_data_from_database(session_id, dataset_id_list):
    with db_utils.get_db_connection() as conn:
        meta_data_result = pd.read_sql_query(
            f"""
           SELECT UD.DATASET_ID, UD.NAME, UD.DATASET_TYPE, UD.OMICS, UD.TAXCODE
            FROM USER_DATASET UD
            JOIN USER U ON U.USER_ID = UD.USER_ID
            WHERE U.SESSION_ID = ? 
            AND UD.DATASET_ID IN ({','.join(['?'] * len(dataset_id_list))})""",
            conn,
            params=[session_id] + dataset_id_list)

        quan_data_result = pd.read_sql_query(
            f"""
            SELECT UQD.*, P.GENE_NAME, P.UNIPROT_ACC FROM USER_QUANTIFICATION_DATA UQD
            JOIN USER_DATASET UD ON UD.DATASET_ID = UQD.DATASET_ID
            JOIN USER U ON UD.USER_ID = U.USER_ID
            JOIN PROTEIN P ON P.PROTEIN_ID = UQD.PROTEIN_ID
            WHERE U.SESSION_ID = ? 
            AND UD.DATASET_ID IN ({','.join(['?'] * len(dataset_id_list))})""",
            conn,
            params=[session_id] + dataset_id_list)

        detail_data_result = pd.read_sql_query(
            f"""
            SELECT UDD.*, MS.SITE_IDENTIFIER
            FROM USER_DATUM_DETAIL UDD
            JOIN USER_QUANTIFICATION_DATA UQD on UDD.USER_DATUM_ID = UQD.USER_DATUM_ID
            JOIN USER_DATASET UD ON UD.DATASET_ID = UQD.DATASET_ID
            JOIN USER U ON UD.USER_ID = U.USER_ID
            LEFT JOIN MODIFIED_SITE MS ON MS.MODIFIED_SITE_ID = UDD.VALUE AND UDD.KEY = 'MODIFIED_SITE_ID'
            WHERE U.SESSION_ID = ? 
            AND UD.DATASET_ID IN ({','.join(['?'] * len(dataset_id_list))})""",
            conn,
            params=[session_id] + dataset_id_list)

    return meta_data_result, quan_data_result, detail_data_result


def create_quan_data_detail_dicts(detail_data_result):
    # Add the site identifiers as details, if they exist
    site_identifier_series = detail_data_result[
        (detail_data_result['KEY'] == 'MODIFIED_SITE_ID') & (pd.notna(detail_data_result['SITE_IDENTIFIER']))
        ].groupby('USER_DATUM_ID')['SITE_IDENTIFIER'].agg(list)  # .agg(lambda identifiers: ', '.join(identifiers))

    detail_data_result = pd.concat(
        [detail_data_result, pd.DataFrame({'KEY': 'Modified Site(s)', 'VALUE': site_identifier_series}).reset_index()])

    # Now turn all details into dictionaries
    return detail_data_result.groupby('USER_DATUM_ID').apply(
        lambda x: {key: value for key, value in x[['KEY', 'VALUE']].values
                   if key not in constants.quan_details_not_imported}, include_groups=False)


def construct_quan_data_dict_list(quan_and_details_df, is_ptm_level, is_curve_data):
    quan_and_details_df = quan_and_details_df[constants.quan_columns_imported].rename(
        {
            'REGULATION': 'regulation',
            'GENE_NAME': 'geneNames',
            'UNIPROT_ACC': 'uniprotAccs',
            'DETAILS': 'details',
        }, axis=1)

    if is_curve_data:
        quan_and_details_df['hiddenDetails'] = quan_and_details_df.apply(
            lambda row: {'Curve ID': row['USER_CURVE_ID']},
            axis=1)
    # Always drop the column now, because it also exists for non-curve data (but it's always NA)
    quan_and_details_df.drop('USER_CURVE_ID', axis=1, inplace=True)

    # Move experiment name and modified sequence (if exists) into details
    quan_and_details_df['details'] = quan_and_details_df.apply(
        lambda row: row['details'] |
                    {'Experiment Name': row['EXPERIMENT']} |
                    ({'Modified Sequence': row['MODIFIED_SEQUENCE']} if pd.notna(row['MODIFIED_SEQUENCE']) else {}),
        axis=1)
    quan_and_details_df.drop(['EXPERIMENT', 'MODIFIED_SEQUENCE'], axis=1, inplace=True)

    return quan_and_details_df.to_dict(orient='records')


def combine_results(datapoints_dictlist, details_dict, curve_metadata_result, curve_details_result,
                    curves_factor, curves_unit):
    for datapoints_dict in datapoints_dictlist:
        curve_id = datapoints_dict['id']
        insert_curve_formula(datapoints_dict)
        insert_curve_parameters(details_dict[curve_id], datapoints_dict)
        curve_name = determine_curve_name(curve_metadata_result.loc[curve_id], details_dict[curve_id],
                                          curve_details_result, curve_id)

        experiment_name = curve_metadata_result.loc[curve_id]['EXPERIMENT']
        insert_curve_legend_text(datapoints_dict, curve_name, experiment_name)
        insert_curve_tooltip_text(datapoints_dict, details_dict[curve_id])
        insert_axis_labels(datapoints_dict, curves_factor, curves_unit)
        insert_curve_highlights(details_dict[curve_id], datapoints_dict)

    return datapoints_dictlist


def insert_axis_labels(datapoints_dict, curves_factor, curves_unit):
    datapoints_dict['xAxisLabel'] = f"{curves_factor} [{curves_unit}]"
    datapoints_dict['yAxisLabel'] = constants.curve_generic_yaxis_label


def insert_curve_legend_text(datapoints_dict, curve_name, experiment_name):
    datapoints_dict['legendText'] = f"{curve_name} ({experiment_name})"


def insert_curve_tooltip_text(datapoints_dict, details_dict_of_curve):
    datapoints_dict['tooltipTextHTML'] = f"<pre style='text-align: left'><b>{datapoints_dict['legendText']}</b><br>"

    if details_dict_of_curve.get('pEC50'):
        ec50 = 10 ** -float(details_dict_of_curve.get('pEC50'))
        ec50_formatted = '{:.2e}'.format(ec50)
        datapoints_dict['tooltipTextHTML'] += f"<br>EC50:           {ec50_formatted}<br>"
    if details_dict_of_curve.get('Fold Change'):
        fc = float(details_dict_of_curve.get('Fold Change'))
        fc_formatted = '{:.3f}'.format(fc)
        datapoints_dict['tooltipTextHTML'] += f"Fold Change:    {fc_formatted}<br>"
    if details_dict_of_curve.get('R2'):
        r2 = float(details_dict_of_curve.get('R2'))
        r2_formatted = '{:.2f}'.format(r2)
        datapoints_dict['tooltipTextHTML'] += f"R2:             {r2_formatted}<br>"
    datapoints_dict['tooltipTextHTML'] += '</pre>'


def determine_curve_name(metadata_of_curve, details_dict_of_curve, curve_details_result, curve_id):
    # Depending on dataset type, can be Sequence, Site Identifier, Gene Name, or Uniprot
    if pd.notna(metadata_of_curve['MODIFIED_SEQUENCE']):
        curve_name = metadata_of_curve['MODIFIED_SEQUENCE']
        # Add placeholder for the protein
        curve_name += ' @ {}'
    elif 'MODIFIED_SITE_ID' in details_dict_of_curve:
        curve_name = curve_details_result[
            (curve_details_result['USER_CURVE_ID'] == curve_id) & (
                    curve_details_result['KEY'] == 'MODIFIED_SITE_ID')][
            'SITE_IDENTIFIER'].iloc[0]
        # Add placeholder for the protein
        curve_name += ' @ {}'
    else:
        curve_name = '{}'

    if pd.notna(metadata_of_curve['GENE_NAME']):
        curve_name = curve_name.format(metadata_of_curve['GENE_NAME'])
    else:
        curve_name = curve_name.format(metadata_of_curve['UNIPROT_ACC'])

    return curve_name


def insert_curve_formula(datapoints_dict):
    datapoints_dict['formula'] = constants.curve_formula
    datapoints_dict['escapeCharacter'] = constants.escape_character


def insert_curve_parameters(details_dict_of_curve, datapoints_dict):
    datapoints_dict['curveParameters'] = {}
    if 'pEC50' in details_dict_of_curve:
        datapoints_dict['curveParameters']['E'] = 10 ** -float(details_dict_of_curve['pEC50'])
    if 'Slope' in details_dict_of_curve:
        datapoints_dict['curveParameters']['B'] = details_dict_of_curve['Slope']
    if 'Back' in details_dict_of_curve:
        datapoints_dict['curveParameters']['D'] = details_dict_of_curve['Back']
    if 'Front' in details_dict_of_curve:
        datapoints_dict['curveParameters']['C'] = details_dict_of_curve['Front']


def insert_curve_highlights(details_dict_of_curve, datapoints_dict):
    if 'pEC50' in details_dict_of_curve:
        datapoints_dict['curveHighlights'] = [10 ** -float(details_dict_of_curve.get('pEC50'))]
        # TODO: The code below often failes with 'Result too large', and error bars are not so important here.
        # if 'pEC50_Error' in details_dict_of_curve:
        #     datapoints_dict['curveHighlightErrorBarEndpoints'] = [
        #         # TODO: Maybe divide error by 2
        #         [10 ** -(float(details_dict_of_curve['pEC50']) - float(details_dict_of_curve['pEC50_Error'])),
        #          10 ** -(float(details_dict_of_curve['pEC50']) + float(details_dict_of_curve['pEC50_Error']))]]


def create_curve_details_dict(curve_details_result):
    return curve_details_result.groupby('USER_CURVE_ID').apply(
        lambda x: {key: value for key, value in x[['KEY', 'VALUE']].values}, include_groups=False)


def create_curve_datapoints_dictlist(data_points_result):
    return data_points_result.groupby('USER_CURVE_ID').apply(
        lambda x: {'id': x.name, 'dataPoints': x[['FACTOR_VALUE', 'RESPONSE_VALUE']].values.tolist()},
        include_groups=False).tolist()


def get_curves_factor_and_unit(data_points_result):
    # Check if Factor name and unit are unique, if not, abort
    if len(data_points_result['FACTOR_NAME'].unique()) > 1:
        db_utils.throw_error('The requested curves have different factors. Please only load a single factor at a time!')
    else:
        curves_factor = data_points_result['FACTOR_NAME'].iloc[0]
    if len(data_points_result['FACTOR_UNIT'].unique()) > 1:
        db_utils.throw_error('The requested curves have different units. Please only load a single unit at a time!')
    else:
        curves_unit = data_points_result['FACTOR_UNIT'].iloc[0]
    return curves_factor, curves_unit


def load_curve_information_from_database(curve_id_list):
    with db_utils.get_db_connection() as conn:
        data_points_result = pd.read_sql_query(
            f"SELECT * FROM USER_CURVE_DATA WHERE USER_CURVE_ID IN ({','.join(['?'] * len(curve_id_list))})",
            conn,
            params=curve_id_list)
        curve_details_result = pd.read_sql_query(
            f"""
                    SELECT UQD.USER_CURVE_ID, UDD.KEY, UDD.VALUE, MS.SITE_IDENTIFIER
                    FROM USER_DATUM_DETAIL UDD
                    JOIN USER_QUANTIFICATION_DATA UQD ON UDD.USER_DATUM_ID = UQD.USER_DATUM_ID
                    LEFT JOIN MODIFIED_SITE MS ON MS.MODIFIED_SITE_ID = UDD.VALUE AND UDD.KEY = 'MODIFIED_SITE_ID'
                    WHERE UQD.USER_CURVE_ID IN ({','.join(['?'] * len(curve_id_list))})
                    """,
            conn,
            params=curve_id_list)

        curve_metadata_result = pd.read_sql_query(
            f"""
                    SELECT UQD.USER_CURVE_ID, UQD.MODIFIED_SEQUENCE, UQD.EXPERIMENT, P.GENE_NAME, P.UNIPROT_ACC
                    FROM USER_QUANTIFICATION_DATA UQD
                    JOIN PROTEIN P ON P.PROTEIN_ID = UQD.PROTEIN_ID
                    WHERE UQD.USER_CURVE_ID IN ({','.join(['?'] * len(curve_id_list))})
                    """,
            conn,
            params=curve_id_list)
    return data_points_result, curve_details_result, curve_metadata_result


def get_user_datasets(session_id, dataset_id_list):
    ptm_input_list = []
    protein_input_list = []

    meta_data_result, quan_data_result, detail_data_result = load_user_data_from_database(
        session_id, dataset_id_list
    )
    if meta_data_result.empty:
        print(f'No data retrieved. '
              f'Datasets {dataset_id_list} either do not exist or they do not match the session id {session_id}.')
        return {
            "ptmInputList": ptm_input_list,
            "proteinInputList": protein_input_list
        }

    quan_data_result.set_index('USER_DATUM_ID', inplace=True)
    detail_dicts = create_quan_data_detail_dicts(detail_data_result)

    # Join the details dicts as a column into the main data frame
    quan_and_details = quan_data_result.merge(detail_dicts.rename('DETAILS'), left_index=True, right_index=True)

    # Iterate over datasets and then decide on the fly whether to add to ptm or to protein list
    for index, rowdict in meta_data_result.iterrows():
        if rowdict['OMICS'] in constants.ptm_omics:
            ptm_input_list += construct_quan_data_dict_list(
                quan_and_details[quan_and_details['DATASET_ID'] == rowdict['DATASET_ID']].copy(),
                True,
                rowdict['DATASET_TYPE'] == 'Curve'
            )
        else:
            protein_input_list += construct_quan_data_dict_list(
                quan_and_details[quan_and_details['DATASET_ID'] == rowdict['DATASET_ID']].copy(),
                False,
                rowdict['DATASET_TYPE'] == 'Curve'
            )

    return {
        "ptmInputList": ptm_input_list,
        "proteinInputList": protein_input_list,
        "datasetInfo": meta_data_result.to_dict(orient='records')
    }


def get_curve_data(curve_id_list: [str]):
    data_points_result, curve_details_result, curve_metadata_result = load_curve_information_from_database(
        curve_id_list)
    curves_factor, curves_unit = get_curves_factor_and_unit(data_points_result)
    datapoints_dictlist = create_curve_datapoints_dictlist(data_points_result)
    details_dict = create_curve_details_dict(curve_details_result)
    curve_metadata_result.set_index('USER_CURVE_ID', inplace=True)
    return combine_results(datapoints_dictlist, details_dict, curve_metadata_result, curve_details_result,
                           curves_factor, curves_unit)
