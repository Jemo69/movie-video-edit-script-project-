import asyncio
from tortoise import Tortoise
from models import Video
from database import init_db

async def run_test():
    """
    Runs a test of the Tortoise-ORM database connection.
    It creates, retrieves, and deletes a video record.
    """
    try:
        # Initialize the database connection and generate schemas
        # This uses the configuration from database.py
        print("Initializing database for ORM test...")
        await init_db()
        print("Database initialized.")

        # Create a new video entry
        test_video_name = "test_video_123"
        test_project_link = "http://example.com/test_video.zip"
        print(f"Creating video entry: {test_video_name}")
        video = await Video.create(video_name=test_video_name, project_link=test_project_link)
        print(f"Video created with ID: {video.id}")

        # Retrieve the video entry to verify
        print(f"Retrieving video with name: {test_video_name}")
        retrieved_video = await Video.get(video_name=test_video_name)
        if retrieved_video:
            print(f"Successfully retrieved video: {retrieved_video.video_name}")
            assert retrieved_video.project_link == test_project_link
        else:
            print("Failed to retrieve video.")
            return

        # Delete the video entry
        print(f"Deleting video with ID: {retrieved_video.id}")
        await retrieved_video.delete()
        print("Video deleted.")

        # Verify deletion
        retrieved_video_after_delete = await Video.filter(video_name=test_video_name).first()
        if not retrieved_video_after_delete:
            print("Successfully verified video deletion.")
        else:
            print("Error: Video still exists after deletion.")

        print("\nORM test completed successfully!")

    except Exception as e:
        print(f"An error occurred during the ORM test: {e}")
    finally:
        # Close the database connections
        await Tortoise.close_connections()
        print("Database connections closed.")

if __name__ == "__main__":
    asyncio.run(run_test())
