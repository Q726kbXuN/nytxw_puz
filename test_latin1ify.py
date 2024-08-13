#!/usr/bin/env python3

# A test harness around testing latin1ify's implementation

import os
import json
import sys
import zipfile
import nyt

if len(sys.argv) == 2 and sys.argv[1] == "sort":
    header = " " * 4
    row = header
    for key in sorted(nyt.LATIN1_SUBS):
        temp = f"{key}: {json.dumps(nyt.LATIN1_SUBS[key])}, "
        if len(temp) + len(row) >= 120:
            print(row)
            row = header
        row += temp
    print(row)
    exit(0)

if 'NYT_ROOT_DIR' not in os.environ:
    print("No 'NYT_ROOT_DIR' env variable seen, please set it to the base of the archive")

def enum_files():
    for dirpath, dirnames, filenames in os.walk(os.environ['NYT_ROOT_DIR']):
        for fn in filenames:
            # if fn.startswith("2023"):
            if fn.endswith(".zip"):
                with zipfile.ZipFile(os.path.join(dirpath, fn)) as zf:
                    for cur in zf.namelist():
                        if cur.endswith(".json"):
                            with zf.open(cur) as f:
                                yield cur, f.read()
            elif fn.endswith(".json"):
                with open(os.path.join(dirpath, fn)) as f:
                        yield fn, f.read()

checked = 0

nyt.store_latin1ify_errors = {}
for fn, cur in enum_files():
    if "acrostic" not in fn:
        new_format = json.loads(cur)
        if "dimensions" in new_format:
            print(fn)
            resp = new_format
        elif "body" in new_format:
            resp = new_format["body"][0]
            resp["meta"] = {}
            # TODO: Notes might be stored elsewhere, need to verify
            for cur in ["publicationDate", "title", "editor", "copyright", "constructors", "notes"]:
                if cur in new_format:
                    resp["meta"][cur] = new_format[cur]
            resp["dimensions"]["columnCount"] = resp["dimensions"]["width"]
            resp["dimensions"]["rowCount"] = resp["dimensions"]["height"]

            resp["gamePageData"] = resp
        else:
            resp = None

        if resp is not None:
            checked += 1
            # print(json.dumps(cur))
            nyt.extra_latin1ify_message = f"  On file {fn}..."
            data = nyt.data_to_puz(resp)
            if len(nyt.store_latin1ify_errors) > 10:
                break

for key, value in nyt.store_latin1ify_errors.items():
    print(f'    {key}: "{value}", # {chr(key).encode("unicode-escape").decode("utf-8")}')

print(f"Checked {checked:,} files")
