# TODO: For all endpoints: Errors if a parameter is missing (generic method that receives all 'get's)
# TODO: Type Hints
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

from scripts import datasetUpload, db_utils, constants, datasetRetrieval


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
        db_utils.throw_error("No gene_name supplied")
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


@app.route('/api/store_user_enrichment_result', methods=['PUT'])
def store_user_enrichment_result():
    enrichment_type_name = request.args.get('enrichmentType')
    with db_utils.get_db_connection() as conn:
        response = conn.execute('SELECT ENRICHMENT_TYPE_ID FROM ENRICHMENT_TYPE WHERE NAME = ?',
                                [enrichment_type_name]
                                ).fetchall()
    if len(response) > 0:
        enrichment_type_id = response[0][0]
    else:
        db_utils.throw_error(f"Could not find an enrichment type id for: {enrichment_type_name}")
    with db_utils.get_db_connection() as conn:
        conn.execute(
            'INSERT INTO USER_DATASET_ENRICHMENT_RESULT(DATASET_ID, ENRICHMENT_TYPE_ID, ENRICHMENT_JSON) VALUES (?,?,?)',
            [request.args.get('datasetId'), enrichment_type_id, json.dumps(request.json['data'])])
    return jsonify(status=200)


@app.route('/api/store_custom_pathway', methods=['PUT'])
def store_custom_pathway():
    # Get the user ID from the UUID
    user_id = db_utils.get_user_id_from_uuid(request.args.get('uuid'))
    # Get or create pathway ID
    custom_pathway_id = request.args.get('customPathwayId')
    if not custom_pathway_id:
        with db_utils.get_db_connection() as conn:
            custom_pathway_id = conn.execute(
                'SELECT MAX(CUSTOM_PATHWAY_ID)+1 FROM USER_CUSTOM_PATHWAY').fetchall()[0][0] or 1
    # Insert
    with db_utils.get_db_connection() as conn:
        conn.execute(
            'INSERT INTO USER_CUSTOM_PATHWAY (CUSTOM_PATHWAY_ID, USER_ID, PATHWAY_NAME, PATHWAY_JSON) VALUES (?,?,?,?)',
            [custom_pathway_id, user_id, request.args.get('customPathwayName'), request.args.get('skeleton')])
    return jsonify(status=200)


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


@app.route('/api/get_custom_pathway_list', methods=['GET'])
def get_custom_pathway_list():
    session_id = request.args.get('uuid')
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query(
            "SELECT "
            "CUSTOM_PATHWAY_ID AS pathwayId, "
            "PATHWAY_NAME AS pathwayName, "
            "PATHWAY_JSON AS pathwayJson "
            "FROM USER_CUSTOM_PATHWAY UCP JOIN USER U on U.USER_ID = UCP.USER_ID "
            "WHERE U.SESSION_ID = ?",
            conn,
            params=[session_id])
    return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/get_pathway_skeleton', methods=['GET'])
def get_pathway_skeleton():
    pathway_name = request.args.get('pathwayName')
    with db_utils.get_db_connection() as conn:
        pathway_json = conn.execute('SELECT PATHWAY_JSON FROM PATHWAY WHERE PATHWAY_NAME = ?',
                                    [pathway_name]
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
    user_dataset_ids = request.args.get('datasetIds')

    response_raw = datasetRetrieval.get_user_datasets(session_id, user_dataset_ids.split(';'))
    return Response(json.dumps(response_raw), mimetype='application/json')


@app.route('/api/get_curve_data', methods=['GET'])
def get_curve_data():
    curve_ids = request.args.get('curveIDs')
    # There are no non-user curves currently, so this parameter is irrelevant
    # is_user_data_mode = request.args.get('isUserDataMode')

    response_dict = datasetRetrieval.get_curve_data(curve_ids.split(';'))
    return Response(json.dumps(response_dict), mimetype='application/json')


@app.route('/api/get_user_enrichment_results', methods=['GET'])
def get_user_enrichment_results():
    session_id = request.args.get('sessionId')
    user_dataset_id = request.args.get('userDatasetId')
    enrichment_type_id = request.args.get('enrichmentTypeId')
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query("""
            SELECT ET.NAME              AS enrichmentType,
                   UDER.ENRICHMENT_JSON AS enrichmentJSON
            FROM USER_DATASET_ENRICHMENT_RESULT UDER
                     JOIN ENRICHMENT_TYPE ET on UDER.ENRICHMENT_TYPE_ID = ET.ENRICHMENT_TYPE_ID
                     JOIN USER_DATASET UD ON UDER.DATASET_ID = UD.DATASET_ID
                    JOIN USER U ON UD.USER_ID = U.USER_ID
            WHERE UD.DATASET_ID = ?
            AND U.SESSION_ID = ?
            AND UDER.ENRICHMENT_TYPE_ID = ?;
            """, conn, params=[user_dataset_id, session_id, enrichment_type_id])
    print(res_df)
    return Response(json.dumps(
        {user_dataset_id: [
            {'enrichmentType': res_df.iloc[0].enrichmentType, 'enrichmentJSON': res_df.iloc[0].enrichmentJSON}]
         }
    ), mimetype='application/json')
    # return Response(json.dumps({user_dataset_id: res_df.to_json(orient='records')}), mimetype='application/json')


@app.route('/api/get_enrichment_types', methods=['GET'])
def get_enrichment_types():
    with db_utils.get_db_connection() as conn:
        res_df = pd.read_sql_query("""
            SELECT ET.NAME as name,
                   ET.SHORT as short,
                   ET.ENRICHMENT_TYPE_ID as enrichmentTypeId,
                   ET.ENRICHMENT_CLASS as enrichmentClass,
                   ET.DESCRIPTION as tooltipHtml,
                   ET.ADDITIONAL_INFO as additionalInfoRaw,
                   group_concat(O.NAME, ';') AS applicableOmics  FROM ENRICHMENT_TYPE ET
            JOIN ENRICHMENT_TYPE_TO_OMIC ETTO on ET.ENRICHMENT_TYPE_ID = ETTO.ENRICHMENT_TYPE_ID
            JOIN OMIC O ON ETTO.OMIC_ID = O.OMIC_ID
            GROUP BY ET.ENRICHMENT_TYPE_ID;
        """,
                                   conn)
    res_df['applicableOmics'] = res_df['applicableOmics'].apply(lambda s: s.split(';'))
    additional_info_columns = res_df['additionalInfoRaw'].apply(lambda infodict: pd.Series(json.loads(infodict)))
    res_df_joined = pd.concat([res_df.drop('additionalInfoRaw', axis=1), additional_info_columns], axis=1)
    return Response(res_df_joined.to_json(orient='records'), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=os.getenv("PRODUCTION", '0') != '1', host='0.0.0.0', port=int(os.getenv("PORT", '3000')))
