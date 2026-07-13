import os
import subprocess
import backend.utils.sys_info as si

nb_content = """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Hello World\\n",
    "This is a test notebook."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Hello, Jupyter!\\n"
     ]
    }
   ],
   "source": [
    "print(\\"Hello, Jupyter!\\")"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}"""

with open("test.ipynb", "w") as f:
    f.write(nb_content)

pandoc_path = si.get_engine_path('pandoc')
lo_path = si.get_engine_path('libreoffice')

print("Pandoc path:", pandoc_path)
print("LO path:", lo_path)

if pandoc_path and lo_path:
    # 1. Convert IPYNB to ODT
    r1 = subprocess.run([pandoc_path, 'test.ipynb', '-o', 'test.odt'])
    print("Pandoc exit code:", r1.returncode)
    
    # 2. Convert ODT to PDF
    r2 = subprocess.run([lo_path, '--headless', '--convert-to', 'pdf', 'test.odt'])
    print("LO exit code:", r2.returncode)
    
    if os.path.exists('test.pdf'):
        print("Success! test.pdf created.")
    else:
        print("Failed to create test.pdf")
else:
    print("Missing pandoc or libreoffice")
