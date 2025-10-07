
import asyncio
from database import init_db, AsyncSessionLocal

async def main():
    print("Attempting to connect to the database using SQLAlchemy...")
    try:
        # Initialize the database connection and create tables
        await init_db()
        print("Database connection successful and tables created!")

        # Optional: Perform a simple query to further test the connection
        async with AsyncSessionLocal() as session:
            # You can add a simple query here if you have data
            pass

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
