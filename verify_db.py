from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Mock env vars if not present, just to test the import and engine creation
if not os.getenv("TURSO_DATABASE_URL"):
    os.environ["TURSO_DATABASE_URL"] = "libsql://test-db.turso.io"
if not os.getenv("TURSO_TOKEN"):
    os.environ["TURSO_TOKEN"] = "test-token"

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL").replace("libsql://", "")
TURSO_TOKEN = os.getenv("TURSO_TOKEN")

try:
    print("Attempting to create engine with sqlite+libsql...")
    engine = create_engine(
        f"sqlite+libsql://{TURSO_DATABASE_URL}?secure=true",
        connect_args={"auth_token": TURSO_TOKEN},
        echo=True
    )
    # Try to connect (this might fail if creds are bad, but we want to see if the MODULE loads)
    # If the module is missing, it fails at create_engine or connect
    print("Engine created. Attempting to connect...")
    with engine.connect() as conn:
        print("Connected successfully!")
except Exception as e:
    print(f"Caught exception: {e}")
    if "NoSuchModuleError" in str(e):
        print("FAIL: sqlalchemy-libsql still not working.")
        exit(1)
    else:
        print("Pass: Module loaded, error is likely just connection/auth related which is expected with dummy creds.")
        exit(0)
