from pytubefix import YouTube
import sys
import builtins

# Mocking input to raise EOFError immediately if called, mimicking non-interactive env
def mock_input(prompt=None):
    print(f"Input requested: {prompt}")
    raise EOFError("EOF when reading a line")

builtins.input = mock_input

try:
    # Rick Roll video - usually safe to test with
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    print(f"Testing URL: {url}")
    yt = YouTube(url)
    # Accessing title triggers the fetch
    print(f"Title: {yt.title}")
except EOFError:
    print("Caught expected EOFError!")
    sys.exit(0)
except Exception as e:
    print(f"Caught unexpected exception: {e}")
    # If it's the specific error we want, we can also exit 0, but let's see.
    # The traceback showed EOFError.
    if "EOF when reading a line" in str(e):
         print("Caught expected EOFError (wrapped)!")
         sys.exit(0)
    sys.exit(1)

print("Did not catch EOFError (maybe it worked?)")
sys.exit(1)
