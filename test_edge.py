import os
import subprocess

edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]

browser = None
for p in edge_paths:
    if os.path.exists(p):
        browser = p
        break

if browser:
    print(f"Found browser at: {browser}")
    html_path = os.path.abspath("test.html")
    pdf_path = os.path.abspath("test_edge.pdf")
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--print-to-pdf=" + pdf_path,
        html_path
    ]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Exit code:", r.returncode)
    print("stderr:", r.stderr)
    print("Exists:", os.path.exists(pdf_path))
else:
    print("No browser found")
