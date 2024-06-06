import sqlite3
from config.config import Config
from urllib.parse import urlparse

def get_db_path_from_uri(uri):
    parsed_uri = urlparse(uri)
    # Strip leading slashes from the path if needed
    return parsed_uri.path.lstrip('/')

def create_tables():
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_path = get_db_path_from_uri(db_uri)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = {
        "user": """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """,
        "groceries": """
            CREATE TABLE IF NOT EXISTS groceries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "tasks": """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT,
                completed INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "settings": """
            CREATE TABLE IF NOT EXISTS settings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                route_origin TEXT NOT NULL,
                route_destination TEXT NOT NULL,
                email TEXT NOT NULL,
                telegram_account TEXT,
                address TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "message": """
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "user_choice": """
            CREATE TABLE IF NOT EXISTS user_choice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                choice TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "family_member": """
            CREATE TABLE IF NOT EXISTS family_member (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """,
        "alembic_version": """
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num TEXT PRIMARY KEY
            )
        """
    }

    for table_name, create_statement in tables.items():
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if not cursor.fetchone():
            print(f"Creating table {table_name}")
            cursor.execute(create_statement)
        else:
            print(f"Table {table_name} already exists")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
