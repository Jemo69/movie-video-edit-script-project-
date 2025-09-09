from turso_python.connection import TursoConnection
from turso_python.crud import TursoCRUD , TursoSchemaManager
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

        database_url = os.getenv('TURSO_DATABASE_URL')
        authtoken = os.getenv('TURSO_TOKEN')
        conn= TursoConnection(
            database_url=database_url,
            authtoken=authtoken
        )
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")

def schema_generator(query  :dict[str , str] , name : str ):
    try:
        some = create_database_connection()
        schema_manager = TursoSchemaManager(some)
        schema_manager.create_table(name ,query)
        logger.info("the query has finished ")
        return 'success' 
    except Exception as e: 
        logger.error(f"Error executing query: {e}")

    

