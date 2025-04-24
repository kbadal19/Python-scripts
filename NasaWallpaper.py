import os
import requests
import ctypes
import platform
from datetime import datetime
from PIL import Image
from io import BytesIO

# NASA API URL
NASA_API_KEY = "Wru18FPOWhj5buE7p3lyli6WWCPhbMdu6vE5kEI3"  # Get from https://api.nasa.gov/
NASA_APOD_URL = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"

# Directory to save the image
SAVE_DIR = os.path.expanduser("~") + "/Pictures/NASA_Wallpapers"
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_nasa_image():
    """Fetch the NASA Astronomy Picture of the Day (APOD)"""
    response = requests.get(NASA_APOD_URL)
    data = response.json()
    
    if "hdurl" in data:
        img_url = data["hdurl"]
    elif "url" in data:
        img_url = data["url"]
    else:
        print("No valid image URL found.")
        return None, None
    
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    
    # Save image
    today = datetime.now().strftime("%Y-%m-%d")
    img_path = os.path.join(SAVE_DIR, f"NASA_{today}.jpg")
    img.save(img_path, "JPEG")

    return img_path, data["title"]

def set_wallpaper(image_path):
    """Set wallpaper based on OS"""
    system = platform.system()

    if system == "Windows":
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
    elif system == "Darwin":  # macOS
        os.system(f"osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"{image_path}\"'")
    elif system == "Linux":
        os.system(f"gsettings set org.gnome.desktop.background picture-uri file://{image_path}")
    else:
        print("OS not supported for wallpaper setting.")
    
    print(f"Wallpaper set: {image_path}")

if __name__ == "__main__":
    image_path, title = fetch_nasa_image()
    
    if image_path:
        print(f"Downloaded: {title}")
        set_wallpaper(image_path)
