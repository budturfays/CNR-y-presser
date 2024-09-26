import sys
import os
import urllib.request
from gui import start_gui  # Import your main GUI function from gui.py

expected_session_key = None

def validate_session_key(session_key):
    return session_key == expected_session_key

def download_image(url, local_path):
    try:
        urllib.request.urlretrieve(url, local_path)
        print(f"Downloaded {local_path}")
    except Exception as e:
        print(f"Failed to download {local_path}: {e}")

def main():
    

    if len(sys.argv) != 2:
        print("Session key is required")
        sys.exit(1)

    session_key = sys.argv[1]
    global expected_session_key
    expected_session_key = session_key

    if not validate_session_key(session_key):
        print("Invalid session key")
        sys.exit(1)

    # Proceed with the main GUI after validating the session key
    print("Session key validated. Running the program...")
    image_url = "https://www.dropbox.com/scl/fi/puoy7zfz4msmjqfjeuap1/roi.png?rlkey=1n5quyjtzetbjq1n2ew67wsgz&st=mpfy3ce8&dl=1"
    local_image_path = os.path.join(os.getcwd(), "roi.png")
    download_image(image_url, local_image_path)
    
    start_gui()

if __name__ == "__main__":
    start_gui()
    #main()
