import psycopg2
from dotenv import load_dotenv
import os

from utils import TryCatch
load_dotenv()

def create_database_connection():
    """
    this the database connection function
    """
    conn_string = os.getenv('DATABASE_URL')
    if not conn_string:
        raise ValueError("DATABASE_URL not found in environment variables.")
    conn =  psycopg2.connect(conn_string)  
    conn.autocommit = True
    cursor = conn.cursor
    return cursor 

def executes_sql_query(query  :str , some):
    try:
        some.execute(query)
        return 'success' 
    except Exception as e: 
        if some:
            some.close
            return None

    

