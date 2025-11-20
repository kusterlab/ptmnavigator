from pathlib import Path
from contextlib import contextmanager
import sqlite3
import uuid
import datetime

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


def get_user_id_from_uuid(session_id):
    if not session_id:
        return None
    with get_db_connection() as conn:
        res = conn.execute('SELECT U.USER_ID FROM USER U WHERE U.SESSION_ID = ?', [session_id]).fetchall()
        if len(res) > 0:
            return res[0][0]
        else:
            return None


def create_session_id_if_not_exists(session_id):
    if not get_user_id_from_uuid(session_id):
        new_session_id = str(uuid.uuid4()).replace('-', '').upper()
        with get_db_connection() as conn:
            conn.execute('INSERT INTO USER(SESSION_ID,LAST_ACCESSION_DATE) VALUES (?,?)',
                         [new_session_id, datetime.datetime.now().isoformat()])
        session_id = new_session_id
    return session_id


def retrieve_user_id(session_id):
    session_id = create_session_id_if_not_exists(session_id)
    user_id = get_user_id_from_uuid(session_id)
    return user_id
