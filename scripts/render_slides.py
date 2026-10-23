import os
import subprocess
from PIL import Image

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

base_dir = r"C:\Users\Hp\OneDrive\Desktop\RAG ChatBot\docs\carousel"

slides = ["slide1", "slide2", "slide3", "slide4"]
rendered_images = []

for s in slides:
    html_file = os.path.join(base_dir, f"{s}.html")
    png_file = os.path.join(base_dir, f"{s}_real.png")
    jpg_file = os.path.join(base_dir, f"{s}.jpg")
    
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1200,1200",
        f"--screenshot={png_file}",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]
    
    print(f"Rendering {s}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    if os.path.exists(png_file):
        # Convert to high-quality JPG
        img = Image.open(png_file).convert("RGB")
        img.save(jpg_file, "JPEG", quality=95)
        rendered_images.append(img)
        print(f"Successfully saved {jpg_file}")
    else:
        print(f"Failed to render {s}: {res.stderr}")

if len(rendered_images) == 4:
    pdf_path = os.path.join(base_dir, "ClinicDocs_AI_CaseStudy.pdf")
    rendered_images[0].save(
        pdf_path,
        save_all=True,
        append_images=rendered_images[1:],
        quality=95
    )
    print(f"Successfully generated 4-slide PDF: {pdf_path}")
