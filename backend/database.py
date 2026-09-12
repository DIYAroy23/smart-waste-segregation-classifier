import sqlite3


DATABASE_NAME = "waste_history.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            category TEXT NOT NULL,
            bin_type TEXT NOT NULL,
            disposal TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_scan(
    filename,
    prediction,
    confidence,
    category,
    bin_type,
    disposal
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO scan_history
        (
            filename,
            prediction,
            confidence,
            category,
            bin_type,
            disposal
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        filename,
        prediction,
        confidence,
        category,
        bin_type,
        disposal
    ))

    connection.commit()
    connection.close()


def get_history():

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM scan_history
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    history = [dict(row) for row in rows]

    connection.close()

    return history