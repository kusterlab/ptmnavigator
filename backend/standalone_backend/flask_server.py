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

    response_dict = datasetRetrieval.get_curve_data(curve_ids.split(';'))
    return Response(json.dumps(response_dict), mimetype='application/json')



if __name__ == '__main__':
    app.run(debug=os.getenv("PRODUCTION", '0') != '1', host='0.0.0.0', port=int(os.getenv("PORT", '3000')))
