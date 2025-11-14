from pathlib import Path
import tomllib
import os
import sys
import datetime
from contextlib import contextmanager
import sqlite3
import uuid
import logging

import pandas as pd
from flask import Flask, request, jsonify, make_response, Response
import flask.wrappers
from flask_cors import CORS

DB_FILE = Path('sqlite_backend.db')


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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
    with get_db_connection() as conn:
        res_df = pd.read_sql_query(f"SELECT * FROM PROTEIN P WHERE P.GENE_NAME = ?",
                                   conn,
                                   params=[input_gene_name])
        return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/get_organisms', methods=['GET'])
def get_organisms():
    with get_db_connection() as conn:
        res_df = pd.read_sql_query(f"SELECT "
                                   f"NAME as name, "
                                   f"TAXCODE as taxcode "
                                   f"FROM ORGANISM",
                                   conn)
        return Response(res_df.to_json(orient='records'), mimetype='application/json')


@app.route('/api/refresh_session', methods=['GET'])
def refresh_session():
    session_id = request.args.get('uuid')
    with get_db_connection() as conn:
        conn.execute('UPDATE USER SET LAST_ACCESSION_DATE = ? WHERE SESSION_ID = ?',
                     [datetime.datetime.now().isoformat(), session_id])
    return jsonify(status=200)


@app.route('/api/get_user_dataset_list', methods=['GET'])
def get_user_dataset_list():
    session_id = request.args.get('uuid')
    with get_db_connection() as conn:
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


if __name__ == '__main__':
    app.run(debug=os.getenv("PRODUCTION", '0') != '1', host='0.0.0.0', port=int(os.getenv("PORT", '3000')))
