import psycopg
from dotenv import load_dotenv
import os

from utils import try_catch
from logger import get_logger

logger = get_logger(__name__)
load_dotenv()

def create_database_connection():
    """
    this the database connection function
    """
    try:
        conn_string = os.getenv("PGDATABASE_URL")
        with psycopg.connect(conn_string) as conn:
            print("Connection successful!")
            return conn
    except psycopg.OperationalError as e:
        print(f"Connection failed: {e}")

def executes_sql_query(query  :str , some):
    try:
        some.execute(query)
        logger.info("the query has finished ")
        return 'success' 
    except Exception as e: 
        logger.error(f"Error executing query: {e}")
        if some:
            some.close()
            return None

    

