#!/usr/bin/env python3

import subprocess
from zipfile import ZipFile
import os
import hashlib

cmd = "python setup.py py2exe"
print("$ " + cmd)
subprocess.check_call(cmd, shell=True)

zip_name = os.path.join("dist", "nytxw_puz.zip")
with ZipFile(zip_name, 'w') as zipf:
    zipf.write(os.path.join("dist", "nytxw_puz.exe"), arcname="nytxw_puz.exe")
print(f"Created {zip_name}")

with open(zip_name, "rb") as f:
    hashes = [
        (hashlib.md5(), "MD5"),
        (hashlib.sha256(), "SHA-256"),
        (hashlib.sha3_256(), "SHA-3"),
    ]
    while True:
        data = f.read(1048576)
        if len(data) == 0:
            break
        for hash, _ in hashes:
            hash.update(data)

    for hash, name in hashes:
        print(f"{name}: {hash.hexdigest()}")
