#!/usr/bin/env python3

UPDATE_VERSION = True
# PATCH_BROWSER_COOKIE3 = False

from zipfile import ZipFile
import hashlib
import os
import platform
import re
import shutil
import subprocess
import version

def run(cmd):
    print("$ " + cmd)
    subprocess.check_call(cmd, shell=True)

def get_dist_files(target_zip_name):
    if isinstance(target_zip_name, str):
        target_zip_name = {target_zip_name}
    dirs = [("dist", "")]
    while len(dirs) > 0:
        dirname, pretty = dirs.pop(0)
        for cur in os.listdir(dirname):
            if cur not in target_zip_name:
                fn = os.path.join(dirname, cur)
                pn = cur if len(pretty) == 0 else pretty + "/" + cur
                if os.path.isfile(fn):
                    yield fn, pn
                elif os.path.isdir(fn):
                    dirs.append((fn, pn))

def build_windows():
    clean_dirs('build', 'dist')
    if UPDATE_VERSION:
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

    # if PATCH_BROWSER_COOKIE3:
    #     import browser_cookie3
    #     with open(os.path.join("patch", "patched_init.py"), "rt") as f:
    #         data = f.read()
    #     with open(browser_cookie3.__file__, "wt") as f:
    #         f.write(data)

    # run("python setup.py py2exe")
    run("pyinstaller nyt.py --onefile")

    zip_name = os.path.join("dist", "nytxw_puz.zip")
    with ZipFile(zip_name, 'w') as zipf:
        for fn, pn in get_dist_files("nytxw_puz.zip"):
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

def clean_dirs(*dir_names):
    for cur in dir_names:
        if os.path.isdir(cur):
            print(f"$ rm -rf {cur}")
            shutil.rmtree(cur)

def build_mac():
    clean_dirs('build', 'dist')
    run('pyinstaller nyt.py --onefile')

    if platform.processor() == 'arm':
        dest_zip = 'nytxw_puz_mac.zip'
    elif platform.processor() == 'i386':
        dest_zip = 'nytxw_puz_mac_x64.zip'
    else:
        raise Exception(platform.processor())

    zip_name = os.path.join("dist", dest_zip)
    with ZipFile(zip_name, 'w') as zipf:
        for fn, pn in get_dist_files(dest_zip):
            zipf.write(fn, pn)

if os.name == 'nt':
    build_windows()
else:
    build_mac()
