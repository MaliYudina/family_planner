import sys
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse
from config.config import Config
import os

# Add the project root to the PYTHONPATH
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

def get_db_path_from_uri(uri):
    parsed_uri = urlparse(uri)
    # Check if the path starts with '///' and strip it if necessary
    if parsed_uri.path.startswith('///'):
        return parsed_uri.path[1:]
    return parsed_uri.path

# Extract the actual file path from the SQLALCHEMY_DATABASE_URI
db_uri = Config.SQLALCHEMY_DATABASE_URI
db_path = get_db_path_from_uri(db_uri)

def update_completed_groceries():
    print(f"Connecting to database at: {db_path}")  # Debug: Print the database path
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    # Connect to the SQLite database using the extracted path
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verify the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groceries';")
        if not cursor.fetchone():
            print("Error: Table 'groceries' does not exist.")
            conn.close()
            return

        # Define the time threshold (one day ago)
        time_threshold = datetime.now() - timedelta(days=2)
        formatted_threshold = time_threshold.strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"Deleting entries older than: {formatted_threshold}")  # Debug: Print the time threshold

        # Delete entries older than one day and marked as completed
        cursor.execute("""
            DELETE FROM groceries 
            WHERE datetime(date) < ? 
            AND completed = 1
        """, (formatted_threshold,))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        print("Entries deleted successfully.")  # Debug: Confirm deletion
    except sqlite3.OperationalError as e:
        print(f"SQLite OperationalError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_completed_groceries()
