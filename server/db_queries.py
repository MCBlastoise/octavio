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
