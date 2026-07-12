import os
import sys
import urllib.request
import zipfile
import subprocess
import shutil
import re

# Resolve workspace root
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(WORKSPACE_ROOT, "runtime")

def reporthook(blocknum, blocksize, totalsize):
    """Callback for progress reporting in console."""
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = f"\rDownloading... {percent:3.1f}% [{readsofar} / {totalsize} bytes]"
        sys.stdout.write(s)
        sys.stdout.flush()
    else:
        sys.stdout.write(f"\rDownloading... {readsofar} bytes")
        sys.stdout.flush()

def download_file(url, target_path):
    print(f"\nFetching: {url}")
    print(f"Target: {target_path}")
    try:
        # User-Agent header to avoid HTTP 403/404 CDN filtering
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, target_path, reporthook)
        print("\nDownload completed successfully.")
        return True
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False

def extract_zip(zip_path, extract_dir):
    print(f"Extracting ZIP: {zip_path} -> {extract_dir}")
    os.makedirs(extract_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("Extraction completed successfully.")
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

def extract_msi(msi_path, target_dir):
    """Extracts Windows MSI files into a directory using built-in msiexec admin installation."""
    print(f"Extracting MSI: {msi_path} -> {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    try:
        # Run msiexec administrative installation
        cmd = [
            "msiexec",
            "/a",
            os.path.abspath(msi_path),
            "/qb",
            f"TARGETDIR={os.path.abspath(target_dir)}"
        ]
        print(f"Running administrative install: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("MSI administrative extraction completed.")
            return True
        else:
            print(f"MSI extraction failed: {result.stderr.decode('utf-8', errors='ignore')}")
            return False
    except Exception as e:
        print(f"MSI extraction process failed: {e}")
        return False

def setup_pandoc():
    dest = os.path.join(RUNTIME_DIR, "pandoc")
    if os.path.exists(os.path.join(dest, "pandoc.exe")):
        print("Pandoc already configured.")
        return
        
    temp_zip = os.path.join(RUNTIME_DIR, "pandoc.zip")
    url = "https://github.com/jgm/pandoc/releases/download/3.1.11.1/pandoc-3.1.11.1-windows-x86_64.zip"
    
    if download_file(url, temp_zip):
        temp_extract = os.path.join(RUNTIME_DIR, "pandoc_temp")
        if extract_zip(temp_zip, temp_extract):
            # Move binary out of nested zip directory to target
            nested_folder = os.path.join(temp_extract, "pandoc-3.1.11.1")
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(nested_folder):
                src_path = os.path.join(nested_folder, f)
                dest_path = os.path.join(dest, f)
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)
                shutil.move(src_path, dest)
            shutil.rmtree(temp_extract)
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def setup_ffmpeg():
    dest = os.path.join(RUNTIME_DIR, "ffmpeg")
    if os.path.exists(os.path.join(dest, "ffmpeg.exe")):
        print("FFmpeg already configured.")
        return
        
    temp_zip = os.path.join(RUNTIME_DIR, "ffmpeg.zip")
    url = "https://github.com/GyanD/codexffmpeg/releases/download/6.0/ffmpeg-6.0-essentials_build.zip"
    
    if download_file(url, temp_zip):
        temp_extract = os.path.join(RUNTIME_DIR, "ffmpeg_temp")
        if extract_zip(temp_zip, temp_extract):
            nested_folder = os.path.join(temp_extract, "ffmpeg-6.0-essentials_build", "bin")
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(nested_folder):
                shutil.move(os.path.join(nested_folder, f), os.path.join(dest, f))
            shutil.rmtree(temp_extract)
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def setup_poppler():
    dest = os.path.join(RUNTIME_DIR, "poppler")
    if os.path.exists(os.path.join(dest, "bin", "pdftoppm.exe")) or os.path.exists(os.path.join(dest, "pdftoppm.exe")):
        print("Poppler already configured.")
        return
        
    temp_zip = os.path.join(RUNTIME_DIR, "poppler.zip")
    url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip"
    
    if download_file(url, temp_zip):
        temp_extract = os.path.join(RUNTIME_DIR, "poppler_temp")
        if extract_zip(temp_zip, temp_extract):
            nested_folder = os.path.join(temp_extract, "poppler-24.02.0")
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(nested_folder):
                src_path = os.path.join(nested_folder, f)
                dest_path = os.path.join(dest, f)
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)
                shutil.move(src_path, dest)
            shutil.rmtree(temp_extract)
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def setup_imagemagick():
    dest = os.path.join(RUNTIME_DIR, "imagemagick")
    if os.path.exists(os.path.join(dest, "magick.exe")):
        print("ImageMagick already configured.")
        return
        
    temp_zip = os.path.join(RUNTIME_DIR, "imagemagick.zip")
    
    # Dynamically extract current ImageMagick download URL
    print("Scraping ImageMagick archive for active portable zip filename...")
    try:
        req = urllib.request.Request(
            "https://imagemagick.org/archive/binaries/",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8')
        # Search for link matching ImageMagick-7.1.1-xx-portable-Q16-x64.zip
        links = re.findall(r'href="(ImageMagick-7\.1\.1-\d+-portable-Q16-x64\.zip)"', html)
        if not links:
            # Fallback search matching HDRI versions
            links = re.findall(r'href="(ImageMagick-7\.1\.1-\d+-portable-Q16-HDRI-x64\.zip)"', html)
            
        if links:
            url = "https://imagemagick.org/archive/binaries/" + links[-1]
            print(f"Found active ImageMagick URL: {url}")
        else:
            raise Exception("No matching ImageMagick portable zip links found.")
    except Exception as e:
        print(f"Failed to dynamically query ImageMagick archive: {e}")
        # Secure static fallback
        url = "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-34-portable-Q16-x64.zip"
        
    if download_file(url, temp_zip):
        extract_zip(temp_zip, dest)
        if os.path.exists(temp_zip):
            os.remove(temp_zip)

def setup_ghostscript():
    dest = os.path.join(RUNTIME_DIR, "ghostscript")
    if os.path.exists(os.path.join(dest, "gswin64c.exe")):
        print("Ghostscript already configured.")
        return
        
    temp_exe = os.path.join(RUNTIME_DIR, "ghostscript_setup.exe")
    url = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10021/gs10021w64.exe"
    
    if download_file(url, temp_exe):
        os.makedirs(dest, exist_ok=True)
        print(f"Running Ghostscript silent installation: {temp_exe} /S /D={dest}")
        # Run NSIS installer silently
        try:
            cmd = f'"{temp_exe}" /S /D={dest}'
            subprocess.run(cmd, shell=True, check=True)
            print("Ghostscript silent install completed successfully.")
            # Move binary out of bin to gs root if needed, or copy it
            bin_path = os.path.join(dest, "bin")
            if os.path.exists(bin_path):
                for f in os.listdir(bin_path):
                    shutil.move(os.path.join(bin_path, f), os.path.join(dest, f))
        except Exception as e:
            print(f"Ghostscript installation execution failed: {e}")
        finally:
            if os.path.exists(temp_exe):
                os.remove(temp_exe)

def setup_tesseract():
    dest = os.path.join(RUNTIME_DIR, "tesseract")
    if os.path.exists(os.path.join(dest, "tesseract.exe")):
        print("Tesseract already configured.")
        return
        
    temp_exe = os.path.join(RUNTIME_DIR, "tesseract_setup.exe")
    url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.0.20221222/tesseract-ocr-w64-setup-v5.3.0.20221222.exe"
    
    if download_file(url, temp_exe):
        os.makedirs(dest, exist_ok=True)
        print(f"Running Tesseract silent installation: {temp_exe} /VERYSILENT /SUPPRESSMSGBOXES /DIR={dest}")
        try:
            # Run Inno Setup installer silently
            cmd = f'"{temp_exe}" /VERYSILENT /SUPPRESSMSGBOXES /DIR="{dest}"'
            subprocess.run(cmd, shell=True, check=True)
            print("Tesseract silent install completed successfully.")
        except Exception as e:
            print(f"Tesseract installation execution failed: {e}")
        finally:
            if os.path.exists(temp_exe):
                os.remove(temp_exe)

def setup_libreoffice():
    dest = os.path.join(RUNTIME_DIR, "libreoffice")
    if os.path.exists(os.path.join(dest, "program", "soffice.exe")):
        print("LibreOffice already configured.")
        return
        
    temp_msi = os.path.join(RUNTIME_DIR, "libreoffice.msi")
    # Fetch from stable archive (permanent download)
    url = "https://downloadarchive.documentfoundation.org/libreoffice/old/7.6.4.1/win/x86_64/LibreOffice_7.6.4.1_Win_x86-64.msi"
    
    if download_file(url, temp_msi):
        temp_extract = os.path.join(RUNTIME_DIR, "lo_temp")
        if extract_msi(temp_msi, temp_extract):
            # Extract moves it to lo_temp/LibreOffice/
            nested_folder = os.path.join(temp_extract, "LibreOffice")
            os.makedirs(dest, exist_ok=True)
            for f in os.listdir(nested_folder):
                src_path = os.path.join(nested_folder, f)
                dest_path = os.path.join(dest, f)
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)
                shutil.move(src_path, dest)
            shutil.rmtree(temp_extract)
        if os.path.exists(temp_msi):
            os.remove(temp_msi)

def run_all_setups():
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    
    print("======================================================================")
    print("       AeroPDF Universal Portable Runtimes Downloader                 ")
    print("======================================================================")
    
    setup_pandoc()
    setup_ffmpeg()
    setup_poppler()
    setup_tesseract()
    setup_ghostscript()
    setup_imagemagick()
    setup_libreoffice()
    
    print("\n======================================================================")
    print(" All bundled portable runtimes downloaded and configured successfully! ")
    print("======================================================================")

if __name__ == "__main__":
    run_all_setups()
