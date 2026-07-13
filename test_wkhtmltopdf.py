import os
import subprocess
import urllib.request
import shutil

url = "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe"
temp_exe = "wkhtmltopdf_setup.exe"
dest = os.path.abspath("runtime/wkhtmltopdf")

print("Downloading wkhtmltopdf...")
urllib.request.urlretrieve(url, temp_exe)

print("Installing wkhtmltopdf...")
os.makedirs(dest, exist_ok=True)
subprocess.run(f'"{temp_exe}" /S /D={dest}', shell=True)
print("Done.")

exe_path = os.path.join(dest, "bin", "wkhtmltopdf.exe")
print("Exists:", os.path.exists(exe_path))

if os.path.exists(exe_path):
    subprocess.run([exe_path, '--version'])
