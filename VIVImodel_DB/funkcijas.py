import sqlite3


def connect():
    return sqlite3.connect("vilcieni.db")


def create_table():
    with connect() as database:
        database.execute("""
            CREATE TABLE IF NOT EXISTS vilcieni (
                vilciens_id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelis TEXT NOT NULL,
                numurs TEXT NOT NULL,
                built INTEGER,
                category TEXT,
                info TEXT
            )
        """)


def add_vilciens(modelis, numurs, built, category, info):
    modelis = modelis.strip()
    numurs = numurs.strip()
    category = category.strip()
    info = info.strip()

    if not modelis or not numurs:
        raise ValueError("Modelis un numurs ir obligāti!")

    if built.strip():
        built = int(built)
    else:
        built = None

    with connect() as database:
        cursor = database.execute("""
            INSERT INTO vilcieni
                (modelis, numurs, built, category, info)
            VALUES (?, ?, ?, ?, ?)
        """, (modelis, numurs, built, category, info))

        return cursor.lastrowid


def get_vilcieni():
    with connect() as database:
        return database.execute("""
            SELECT vilciens_id, modelis, numurs,
                   built, category, info
            FROM vilcieni
            ORDER BY vilciens_id
        """).fetchall()


def get_vilciens(vilciens_id):
    with connect() as database:
        return database.execute("""
            SELECT vilciens_id, modelis, numurs,
                   built, category, info
            FROM vilcieni
            WHERE vilciens_id = ?
        """, (vilciens_id,)).fetchone()


def delete_vilciens(vilciens_id):
    with connect() as database:
        database.execute(
            "DELETE FROM vilcieni WHERE vilciens_id = ?",
            (vilciens_id,)
        )


def update_vilciens(
    vilciens_id, modelis, numurs, built, category, info
):
    built = int(built) if built.strip() else None

    with connect() as database:
        database.execute("""
            UPDATE vilcieni
            SET modelis = ?, numurs = ?, built = ?,
                category = ?, info = ?
            WHERE vilciens_id = ?
        """, (
            modelis, numurs, built, category, info, vilciens_id
        ))


create_table()
