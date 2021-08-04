#!/usr/bin/env python3

import subprocess
from zipfile import ZipFile
import os

cmd = "python -m PyInstaller --onefile --name nytxw_puz nyt.py"
print("$ " + cmd)
subprocess.check_call(cmd, shell=True)

zip_name = os.path.join("dist", "nytxw_puz.zip")
with ZipFile(zip_name, 'w') as zipf:
    zipf.write(os.path.join("dist", "nytxw_puz.exe"), arcname="nytxw_puz.exe")
print(f"Created {zip_name}")
