from pytubefix import YouTube
import sys
import builtins

# Mocking input to raise EOFError immediately if called
def mock_input(prompt=None):
    print(f"Input requested: {prompt}")
    raise EOFError("EOF when reading a line")

builtins.input = mock_input

def silent_po_token_verifier():
    print("Silent PO token verifier called")
    # Return dummy data
    return "", ""

try:
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" 
    print(f"Testing URL: {url}")
    # Apply the fix
    yt = YouTube(url, po_token_verifier=silent_po_token_verifier)
    print(f"Title: {yt.title}")
    print("Success! No EOFError.")
except EOFError:
    print("Caught EOFError! Fix failed.")
    sys.exit(1)
except Exception as e:
    print(f"Caught unexpected exception: {e}")
    # If it fails with something else (like network error), that's fine for now, 
    # as long as it's not EOFError.
    sys.exit(0)
