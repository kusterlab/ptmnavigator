from . import db_utils, constants
import pandas as pd


def get_curve_data(curve_id_list: [str]):
    data_points_result, curve_details_result, curve_metadata_result = load_curve_information_from_database(
        curve_id_list)
    curves_factor, curves_unit = get_curves_factor_and_unit(data_points_result)
    datapoints_dictlist = create_datapoints_dictlist(data_points_result)
    details_dict = create_details_dict(curve_details_result)
    curve_metadata_result.set_index('USER_CURVE_ID', inplace=True)
    return combine_results(datapoints_dictlist, details_dict, curve_metadata_result, curve_details_result,
                           curves_factor, curves_unit)


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


def create_details_dict(curve_details_result):
    return curve_details_result.groupby('USER_CURVE_ID').apply(
        lambda x: {key: value for key, value in x[['KEY', 'VALUE']].values}, include_groups=False)


def create_datapoints_dictlist(data_points_result):
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
