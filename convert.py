from PIL import Image
import os
from pathlib import Path

# Convert images to WebP format with a target width while maintaining aspect ratio
# Settings
input_folder = "input_images"
output_folder = "output_images"
target_width = 1080  # px

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Allowed formats
valid_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

def convert_to_webp(img_path, output_path):
    try:
        with Image.open(img_path) as img:
            # Maintain aspect ratio
            w_percent = (target_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            img = img.resize((target_width, h_size), Image.LANCZOS)
            
            # Save as WebP
            img.save(output_path, "WEBP", quality=80)
            print(f"✅ Converted: {img_path} → {output_path}")
    except Exception as e:
        print(f"❌ Error processing {img_path}: {e}")

# Process all images
for filename in os.listdir(input_folder):
    ext = os.path.splitext(filename)[1].lower()
    if ext in valid_extensions:
        in_path = os.path.join(input_folder, filename)
        out_name = os.path.splitext(filename)[0] + ".webp"
        out_path = os.path.join(output_folder, out_name)
        convert_to_webp(in_path, out_path)

print("🎉 All images converted.")
