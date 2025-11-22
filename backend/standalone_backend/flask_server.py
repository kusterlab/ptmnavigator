from pathlib import Path
import tomllib
import os
import sys
import datetime
import logging
import json

import pandas as pd
from flask import Flask, request, jsonify, make_response, Response
import flask.wrappers
from flask_cors import CORS

from scripts import datasetUpload, db_utils, constants

def get_version() -> str:
    """Get version of the project from pyproject file"""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]


def setup_logger():
    global LOGGER
    LOGGER = logging.getLogger('ptmnavigator_sqlite_backend')
    LOGGER.setLevel(logging.INFO)

    file_handler = logging.FileHandler('ptmnavigator_sqlite_backend.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    LOGGER.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    LOGGER.addHandler(console_handler)

    # Redirect print statements to the logger
    class LoggerWriter:
        def __init__(self, level):
            self.level = level

        def write(self, message):
            if message.strip():  # Avoid logging empty messages
                self.level(message)

        def flush(self):
            pass  # No-op for compatibility with sys.stdout/err

    # Replace stdout and stderr with logger
    sys.stdout = LoggerWriter(LOGGER.info)
    sys.stderr = LoggerWriter(LOGGER.error)


def create_app():
    setup_logger()
    application = Flask(__name__)
    CORS(application)  # Enable CORS
    print('App created.')
    return application


app = create_app()


@app.route('/', methods=['GET'])
def get_status() -> flask.wrappers.Response:
    return jsonify(status=200, version=get_version())


@app.route('/api/get_proteins_by_gene_name', methods=['GET'])
def get_proteins_by_gene_name():
    input_gene_name = request.args.get('gene_name')
    if not input_gene_name:
        return Response("Error: No gene_name supplied", 400)
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query(f"SELECT * FROM PROTEIN P WHERE P.GENE_NAME = ?",
                                   conn,
                                   params=[input_gene_name])
        return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/get_organisms', methods=['GET'])
def get_organisms():
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query(f"SELECT "
                                   f"NAME as name, "
                                   f"TAXCODE as taxcode "
                                   f"FROM ORGANISM",
                                   conn)
        return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/refresh_session', methods=['GET'])
def refresh_session():
    session_id = db_utils.create_session_id_if_not_exists(request.args.get('uuid'))
    with db_utils.get_db_connection() as conn:
        conn.execute('UPDATE USER SET LAST_ACCESSION_DATE = ? WHERE SESSION_ID = ?',
                     [datetime.datetime.now().isoformat(), session_id])
    return jsonify(session_id=session_id)


@app.route('/api/get_user_dataset_list', methods=['GET'])
def get_user_dataset_list():
    session_id = request.args.get('uuid')
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query(
            "SELECT UD.DATASET_ID AS datasetId, "
            "UD.NAME AS datasetName, "
            "UD.DATASET_TYPE AS datasetType, "
            "UD.OMICS as omics, "
            "UD.TAXCODE as taxcode "
            "FROM USER_DATASET UD "
            "JOIN USER U on UD.USER_ID = U.USER_ID "
            "WHERE U.SESSION_ID = ?",
            conn,
            params=[session_id])
    return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/upload_dataset', methods=['PUT'])
def upload_dataset():
    return datasetUpload.main(request)


@app.route('/api/get_canonical_pathway_list', methods=['GET'])
def get_canonical_pathway_list():
    taxcode = request.args.get('taxcode')
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query(
            "SELECT "
            "P.PATHWAY_NAME AS name, "
            "P.TITLE as title "
            "FROM PATHWAY P WHERE P.TAXCODE = ?",
            conn,
            params=[taxcode])
    return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/get_pathway_skeleton', methods=['GET'])
def get_pathway_skeleton():
    # TODO: For all of these guys: Errors if the parameters are missing
    pathway_id = request.args.get('pathwayId')
    with db_utils.get_db_connection() as conn:
        pathway_json = conn.execute('SELECT PATHWAY_JSON FROM PATHWAY WHERE PATHWAY_ID = ?',
                                    [pathway_id]
                                    ).fetchall()[0][0]
    return Response(pathway_json, mimetype='application/json')


@app.route('/api/get_filtered_pathway_names', methods=['GET'])
def get_filtered_pathway_names():
    # Accept a list of gene names and/or uniprot ids as search strings
    # Return the pathways that contain ALL of these
    searchStrings = request.args.get('searchStrings')
    taxcode = request.args.get('taxcode')
    result_sets = []
    for searchString in searchStrings.split(';'):
        with db_utils.get_db_connection() as conn:
            result_raw = conn.execute("""
            SELECT DISTINCT PW.PATHWAY_NAME
            FROM PROTEIN PR
            JOIN PATHWAY_TO_PROTEIN PTP ON PR.PROTEIN_ID = PTP.PROTEIN_ID
            JOIN PATHWAY PW ON PTP.PATHWAY_ID = PW.PATHWAY_ID
              WHERE (
                        LOWER(PR.UNIPROT_ACC) LIKE '%' || LOWER(?) || '%'
                    OR
                        LOWER(PR.GENE_NAME) LIKE '%' || LOWER(?) || '%'
                    )
                    AND PW.N_GENES > 0
                    AND PW.TAXCODE = ?
            """, [searchString, searchString, taxcode]).fetchall()
            result_sets.append({entry[0] for entry in result_raw})
    filtered_pathway_ids = set.intersection(*result_sets)
    return Response(json.dumps(list(filtered_pathway_ids)), mimetype='application/json')


@app.route('/api/get_user_datasets', methods=['GET'])
def get_user_datasets():
    session_id = request.args.get('sessionId')
    user_dataset_ids = request.args.get('userDatasets')
    user_dataset_ids.split(';')
    # TODO Implement


@app.route('/api/get_curve_data', methods=['GET'])
def get_curve_data():
    curve_ids = request.args.get('curveIDs')
    # There are no non-user curves currently, so this parameter is irrelevant
    # is_user_data_mode = request.args.get('isUserDataMode')
    curve_id_list = curve_ids.split(';')
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

    # Check if Factor name and unit are unique, if not, abort
    if len(data_points_result['FACTOR_NAME'].unique()) > 1:
        db_utils.throw_error('The requested curves have different factors. Please only load a single factor at a time!')
    else:
        curves_factor = data_points_result['FACTOR_NAME'].iloc[0]
    if len(data_points_result['FACTOR_UNIT'].unique()) > 1:
        db_utils.throw_error('The requested curves have different units. Please only load a single unit at a time!')
    else:
        curves_unit = data_points_result['FACTOR_UNIT'].iloc[0]
    datapoints_dictlist = data_points_result.groupby('USER_CURVE_ID').apply(
        lambda x: {'id': x.name, 'dataPoints': x[['FACTOR_VALUE', 'RESPONSE_VALUE']].values.tolist()},
        include_groups=False).tolist()
    details_dict = curve_details_result.groupby('USER_CURVE_ID').apply(
        lambda x: {key: value for key, value in x[['KEY', 'VALUE']].values}, include_groups=False)
    curve_metadata_result.set_index('USER_CURVE_ID', inplace=True)
    for datapoints_dict in datapoints_dictlist:
        curve_id = datapoints_dict['id']
        datapoints_dict['formula'] = constants.curve_formula
        datapoints_dict['escapeCharacter'] = constants.escape_character
        datapoints_dict['curveParameters'] = {}
        if 'pEC50' in details_dict[curve_id]:
            datapoints_dict['curveParameters']['E'] = 10 ** -float(details_dict[curve_id]['pEC50'])
        if 'Slope' in details_dict[curve_id]:
            datapoints_dict['curveParameters']['B'] = details_dict[curve_id]['Slope']
        if 'Back' in details_dict[curve_id]:
            datapoints_dict['curveParameters']['D'] = details_dict[curve_id]['Back']
        if 'Front' in details_dict[curve_id]:
            datapoints_dict['curveParameters']['C'] = details_dict[curve_id]['Front']

        curve_name = None  # Depending on dataset type, can be Sequence, Site Identifier, Gene Name, or Uniprot
        if pd.notna(curve_metadata_result.loc[curve_id]['MODIFIED_SEQUENCE']):
            curve_name = curve_metadata_result.loc[curve_id]['MODIFIED_SEQUENCE']
            # Add placeholder for the protein
            curve_name += ' @ {}'
        elif 'MODIFIED_SITE_ID' in details_dict[curve_id]:
            curve_name = curve_details_result[
                (curve_details_result['USER_CURVE_ID'] == curve_id) & (
                        curve_details_result['KEY'] == 'MODIFIED_SITE_ID')][
                'SITE_IDENTIFIER'].iloc[0]
            # Add placeholder for the protein
            curve_name += ' @ {}'
        else:
            curve_name = '{}'

        if pd.notna(curve_metadata_result.loc[curve_id]['GENE_NAME']):
            curve_name = curve_name.format(curve_metadata_result.loc[curve_id]['GENE_NAME'])
        else:
            curve_name = curve_name.format(curve_metadata_result.loc[curve_id]['UNIPROT_ACC'])

        experiment_name = curve_metadata_result.loc[curve_id]['EXPERIMENT']
        datapoints_dict['legendText'] = f"{curve_name} ({experiment_name})"
        datapoints_dict['tooltipTextHTML'] = f"<pre style='text-align: left'><b>{datapoints_dict['legendText']}</b><br>"

        if details_dict[curve_id].get('pEC50'):
            ec50 = 10 ** -float(details_dict[curve_id].get('pEC50'))
            ec50_formatted = '{:.2e}'.format(ec50)
            datapoints_dict['tooltipTextHTML'] += f"<br>EC50:           {ec50_formatted}<br>"
        if details_dict[curve_id].get('Fold Change'):
            fc = float(details_dict[curve_id].get('Fold Change'))
            fc_formatted = '{:.3f}'.format(fc)
            datapoints_dict['tooltipTextHTML'] += f"Fold Change:    {fc_formatted}<br>"
        if details_dict[curve_id].get('R2'):
            r2 = float(details_dict[curve_id].get('R2'))
            r2_formatted = '{:.2f}'.format(r2)
            datapoints_dict['tooltipTextHTML'] += f"R2:             {r2_formatted}<br>"
        datapoints_dict['tooltipTextHTML'] += '</pre>'

        datapoints_dict['xAxisLabel'] = f"{curves_factor} [{curves_unit}]"
        datapoints_dict['yAxisLabel'] = constants.curve_generic_yaxis_label
        if 'pEC50' in details_dict[curve_id]:
            datapoints_dict['curveHighlights'] = [10 ** -float(details_dict[curve_id].get('pEC50'))]
            # TODO: The code below often failes with 'Result too large', and error bars are not so important here.
            # if 'pEC50_Error' in details_dict[curve_id]:
            #     datapoints_dict['curveHighlightErrorBarEndpoints'] = [
            #         # TODO: Maybe divide error by 2
            #         [10 ** -(float(details_dict[curve_id]['pEC50']) - float(details_dict[curve_id]['pEC50_Error'])),
            #          10 ** -(float(details_dict[curve_id]['pEC50']) + float(details_dict[curve_id]['pEC50_Error']))]]
    return Response(json.dumps(datapoints_dictlist), mimetype='application/json')



if __name__ == '__main__':
    app.run(debug=os.getenv("PRODUCTION", '0') != '1', host='0.0.0.0', port=int(os.getenv("PORT", '3000')))
