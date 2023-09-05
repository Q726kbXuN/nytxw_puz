#!/usr/bin/env python3

# This next line must be exactly this format
VERSION = "1.13"
# The location of this file on GitHub
SELF_URL = "https://raw.githubusercontent.com/Q726kbXuN/nytxw_puz/master/version.py"

import re

# Pull out a version from a string version of this file
def get_ver_from_source(data):
    if hasattr(data, 'read'):
        data = data.read()
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    
    m = re.search('VERSION *= *"(?P<ver>[0-9.]+)"', data)
    if m is None:
        return None
    
    return m.group("ver")

# Get the version of this file on GitHub
def get_ver_from_github():
    from urllib.request import urlopen
    try:
        resp = urlopen(SELF_URL, timeout=5).read()
        return get_ver_from_source(resp)
    except:
        return None

# Simple command line test of this
if __name__ == "__main__":
    print(f"Version embedded in file: '{VERSION}'")
    with open(__file__, "r") as f:
        print(f"Version found in file: '{get_ver_from_source(f)}'")
    print(get_ver_from_github())