import os
from dotenv import load_dotenv
import libsql
from logger import get_logger
from typing import Dict

# Load environment variables and initialize logger
load_dotenv()
logger = get_logger(__name__)

def create_database_connection():
    """
    Creates a database connection using the Turso SDK.
    """
    database_url = os.getenv('TURSO_DATABASE_URL')
    authtoken = os.getenv('TURSO_TOKEN')
    
    if not database_url:
        raise ValueError("TURSO_DATABASE_URL environment variable not set.")
    if not authtoken:
        raise ValueError("TURSO_TOKEN environment variable not set.")
        
    return libsql.connect(database=database_url, auth_token=authtoken)

def create_table(table_name: str, columns: Dict[str, str]) -> str:
    """
    Creates a table in the database.
    """
    try:
        conn = create_database_connection()
        with conn:
            column_definitions = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            
            conn.execute(query)
            
            logger.info(f"Table '{table_name}' created successfully")
            return 'success'
    except Exception as e:
        logger.error(f"Error creating table '{table_name}': {e}")
        return 'error'

def main() -> None:
    """
    Main function to define schemas and run the table creation tasks.
    """
    video_schema: Dict[str, str] = {
        "id": "INTEGER PRIMARY KEY",
        "title": "TEXT NOT NULL",
        "path": "TEXT UNIQUE NOT NULL"
    }
    
    users_schema: Dict[str, str] = {
        "id": "INTEGER PRIMARY KEY",
        "username": "TEXT NOT NULL UNIQUE",
        "email": "TEXT UNIQUE"
    }

    create_table(table_name='video', columns=video_schema)
    create_table(table_name='Users', columns=users_schema)

if __name__ == "__main__":
    main()
