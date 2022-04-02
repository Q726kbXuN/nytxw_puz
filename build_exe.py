#!/usr/bin/env python3

import subprocess
from zipfile import ZipFile
import os
import hashlib
import re
import version

def run(cmd):
    print(cmd)
    subprocess.check_call(cmd, shell=True)

with open("version.py", "r", encoding="utf-8") as f:
    data = f.read()
data = re.sub(
    '(?P<pre>VERSION *= *"[0-9]+\\.)(?P<ver>[0-9]+)(?P<suf>")', 
    lambda m: f"{m.group('pre')}{int(m.group('ver'))+1:02d}{m.group('suf')}", 
    data,
)
with open("version.py", "w", newline="", encoding="utf-8") as f:
    f.write(data)

run("git add version.py")
run(f'git commit -m "Update version to {version.get_ver_from_source(data)}"')
run("python setup.py py2exe")

def get_dist_files():
    dirs = [("dist", "")]
    while len(dirs) > 0:
        dirname, pretty = dirs.pop(0)
        for cur in os.listdir(dirname):
            if cur != "nytxw_puz.zip":
                fn = os.path.join(dirname, cur)
                pn = cur if len(pretty) == 0 else pretty + "/" + cur
                if os.path.isfile(fn):
                    yield fn, pn
                elif os.path.isdir(fn):
                    dirs.append((fn, pn))

zip_name = os.path.join("dist", "nytxw_puz.zip")
with ZipFile(zip_name, 'w') as zipf:
    for fn, pn in get_dist_files():
        zipf.write(fn, pn)

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
