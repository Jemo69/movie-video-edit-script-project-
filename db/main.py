import os
import asyncio
from dotenv import load_dotenv
import libsql_client as libsql
from logger import get_logger
from typing import Dict

# Load environment variables and initialize logger
load_dotenv()
logger = get_logger(__name__)

async def create_database_connection() -> libsql.Client:
    """
    Asynchronously creates a database connection using the Turso SDK.
    """
    database_url: str | None = os.getenv('TURSO_DATABASE_URL')
    authtoken: str | None = os.getenv('TURSO_TOKEN')
    
    if not database_url:
        raise ValueError("TURSO_DATABASE_URL environment variable not set.")
    if not authtoken:
        raise ValueError("TURSO_TOKEN environment variable not set.")
        
    # The connect function is a coroutine, so it must be awaited
    return await libsql.create_client(database_url, auth_token=authtoken)

async def create_table(table_name: str, columns: Dict[str, str]) -> str:
    """
    Asynchronously creates a table in the database.
    
    Uses 'async with' to ensure the database connection is always closed.
    """
    try:
        # 'async with' handles opening and closing the connection
        async with await create_database_connection() as conn:
            column_definitions: list[str] = [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
            query: str = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)})"
            
            # Database operations are coroutines and must be awaited
            await conn.execute(query)
            await conn.commit()
            
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

    # Run table creation tasks concurrently
    await asyncio.gather(
        create_table(table_name='video', columns=video_schema),
        create_table(table_name='Users', columns=users_schema)
    )

if __name__ == "__main__":
    # To install the required library: uv pip install libsql-client
    # To run the script: uv run python your_script_name.py
    asyncio.run(main())

