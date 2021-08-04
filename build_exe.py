#!/usr/bin/env python3

import subprocess

cmd = "python -m PyInstaller --onefile --name nytxw_puz nyt.py"
print("$ " + cmd)
subprocess.check_call(cmd, shell=True)
