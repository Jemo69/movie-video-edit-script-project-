import os
import asyncio
from dotenv import load_dotenv
from typing import List
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



def get_table_names () -> List[str] | None:
    """
    Connects to a LibSQL database and retrieves a list of all table names.
    
    Args:
        db_url: The URL of the LibSQL database.
        auth_token: The authentication token for the database.
        
    Returns:
        A Result object containing a list of table names on success,
        or an Exception on failure.
    """
    try:
        db = create_database_connection()
        query_result =  db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row["name"] for row in query_result]
        return table_names
    except Exception as e:
         logger.error(msg=e)

def create_table(table_name: str, columns: Dict[str, str]) -> str | None:
    """
    Creates a table in the database.
    """
    try:
        conn = create_database_connection()
        tables =  get_table_names()
        if not tables:
            logger.error("Failed to retrieve table names.")
            return None
        if table_name in tables:
            logger.info(f"Table '{table_name}' already exists")
            return 'exists'
        with conn:
            column_definitions = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            
            conn.execute(query)
            
            logger.info(f"Table '{table_name}' created successfully")
            return 'success'
    except Exception as e:
        logger.error(f"Error creating table '{table_name}': {e}")
        return 'error'

async def main() -> None:
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

    await create_table(table_name='video', columns=video_schema)
    await create_table(table_name='Users', columns=users_schema)
    create_table(table_name='video', columns=video_schema)
    create_table(table_name='Users', columns=users_schema)

if __name__ == "__main__":
    asyncio.run(main())

