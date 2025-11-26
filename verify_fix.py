import sys
import builtins
from unittest.mock import MagicMock

# Mocking input to raise EOFError immediately if called
def mock_input(prompt=None):
    print(f"Input requested: {prompt}")
    raise EOFError("EOF when reading a line")

builtins.input = mock_input

# Mock database stuff to avoid needing real DB connection for this test
sys.modules['database'] = MagicMock()
sys.modules['storage.main'] = MagicMock()
sys.modules['models'] = MagicMock()

try:
    from main import video_downloader
    
    # Test with a known video
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"Testing URL: {url}")
    
    # We expect this to NOT raise EOFError now
    result = video_downloader(url)
    
    if result:
        print("Video downloader returned successfully (or at least didn't crash with EOFError)")
        print(f"Result: {result}")
    else:
        print("Video downloader returned None (expected if download fails for other reasons, but not EOFError)")

except EOFError:
    print("Caught EOFError! Fix failed.")
    sys.exit(1)
except Exception as e:
    print(f"Caught unexpected exception: {e}")
    # If it's not EOFError, we consider it a pass for this specific issue
    sys.exit(0)
