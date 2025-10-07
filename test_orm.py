import asyncio
from sqlalchemy.future import select
from database import init_db, AsyncSessionLocal
from models import Video

async def run_test():
    """
    Runs a test of the SQLAlchemy ORM database connection.
    It creates, retrieves, and deletes a video record.
    """
    try:
        # Initialize the database connection and create tables
        print("Initializing database for ORM test...")
        await init_db()
        print("Database initialized.")

        async with AsyncSessionLocal() as session:
            # Create a new video entry
            test_video_name = "test_video_123"
            test_project_link = "http://example.com/test_video.zip"
            print(f"Creating video entry: {test_video_name}")
            video = Video(video_name=test_video_name, project_link=test_project_link)
            session.add(video)
            await session.commit()
            await session.refresh(video)
            print(f"Video created with ID: {video.id}")

            # Retrieve the video entry to verify
            print(f"Retrieving video with name: {test_video_name}")
            result = await session.execute(select(Video).filter(Video.video_name == test_video_name))
            retrieved_video = result.scalars().first()
            if retrieved_video:
                print(f"Successfully retrieved video: {retrieved_video.video_name}")
                assert retrieved_video.project_link == test_project_link
            else:
                print("Failed to retrieve video.")
                return

            # Delete the video entry
            print(f"Deleting video with ID: {retrieved_video.id}")
            await session.delete(retrieved_video)
            await session.commit()
            print("Video deleted.")

            # Verify deletion
            result = await session.execute(select(Video).filter(Video.video_name == test_video_name))
            retrieved_video_after_delete = result.scalars().first()
            if not retrieved_video_after_delete:
                print("Successfully verified video deletion.")
            else:
                print("Error: Video still exists after deletion.")

        print("\nORM test completed successfully!")

    except Exception as e:
        print(f"An error occurred during the ORM test: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())