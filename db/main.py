import psycopg2
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
        conn_string = os.getenv('DATABASE_URL')
        if not conn_string:
            raise ValueError("DATABASE_URL not found in environment variables.")
        conn =  psycopg2.connect(conn_string)  
        conn.autocommit = True
        cursor = conn.cursor
        return cursor
    except psycopg2.Error as e:
        logger.error(f"Error connecting to the database: {e}")
        return None

def executes_sql_query(query  :str , some):
    try:
        some.execute(query)
        return 'success' 
    except Exception as e: 
        logger.error(f"Error executing query: {e}")
        if some:
            some.close()
            return None

    

