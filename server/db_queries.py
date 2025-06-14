import sqlite3
from contextlib import closing
import server_utils

# def add_db_session(session_id, instrument_id, is_test=False):
#     db_filename = server_utils.get_db_filename(is_test)
#     insert_sql = 'INSERT INTO sessions (session_id, instrument_id) VALUES (?, ?)'
#     with sqlite3.connect(db_filename) as connection:
#         with closing(connection.cursor()) as cursor:
#             cursor.execute(insert_sql, (session_id, instrument_id))
#             connection.commit()

# def refresh_db_session(session_id, instrument_id, is_test=False):
#     db_filename = server_utils.get_db_filename(is_test)
#     update_sql = """UPDATE sessions
#                     SET last_updated = datetime('now')
#                     WHERE session_id = ? AND instrument_id = ?;
#                  """
#     with sqlite3.connect(db_filename) as connection:
#         with closing(connection.cursor()) as cursor:
#             cursor.execute(update_sql, (session_id, instrument_id))
#             connection.commit()

def add_or_refresh_db_session(session_id, instrument_id, is_test=False):
    db_filename = server_utils.get_db_filename(is_test)
    update_sql = """INSERT INTO sessions (session_id, instrument_id)
                    VALUES (?, ?)
                    ON CONFLICT(session_id, instrument_id)
                    DO UPDATE SET last_updated = datetime('now');
                 """
    with sqlite3.connect(db_filename) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(update_sql, (session_id, instrument_id))
            connection.commit()

def get_db_instruments(is_test=False):
    db_filename = server_utils.get_db_filename(is_test)
    get_instrument_sql = "SELECT * FROM instruments;"
    with sqlite3.connect(db_filename) as connection:
        connection.row_factory = sqlite3.Row  # This is the magic
        with closing(connection.cursor()) as cursor:
            cursor.execute(get_instrument_sql)
            rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    return data

def get_instrument_sessions(instrument_id, is_test=False):
    db_filename = server_utils.get_db_filename(is_test)
    get_sessions_sql = """
        SELECT
        *,
        (julianday(last_updated) - julianday(created_at)) * 86400 AS duration_in_seconds
        FROM sessions
        WHERE instrument_id = ? AND duration_in_seconds >= 120
        ORDER BY last_updated DESC
        LIMIT 5;
    """
    with sqlite3.connect(db_filename) as connection:
        connection.row_factory = sqlite3.Row  # This is the magic
        with closing(connection.cursor()) as cursor:
            cursor.execute(get_sessions_sql, (instrument_id,))
            rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    return data
