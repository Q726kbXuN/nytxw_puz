#!/usr/bin/env python3

# A test harness around testing latin1ify's implementation
import nyt
import json, os, sys, zipfile

_commands = []
def cmd(cmd, args, desc):
    def helper(func):
        _commands.append({"cmd": cmd, "args": args, "desc": desc, "func": func})
        def wrapper(*args2, **kwargs):
            return func(*args2, **kwargs)
        return wrapper
    return helper

@cmd("sort", 0, "= Pretty print and sort the LATIN1_SUBS variable")
def show_sorted():
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

def enum_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
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

@cmd("test_archive", 1, "<root_dir> = Check all files in an archive folder")
def test_archive(root_dir):
    checked = 0

    nyt.store_latin1ify_errors = {}
    for fn, cur in enum_files(root_dir):
        if "acrostic" not in fn:
            new_format = json.loads(cur)
            if "dimensions" in new_format:
                print(fn)
                resp = new_format
            elif "body" in new_format:
                resp = new_format["body"][0]
                resp["meta"] = {}
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

@cmd("use_loader", 1, "<loader_py> = Use a loader module to test puzzles")
def use_loader(loader_py):
    import importlib
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader('loader', loader=None))
    with open(loader_py, "rb") as f:
        code = f.read()
    module.__file__ = loader_py
    exec(code, module.__dict__)

    nyt.store_latin1ify_errors = {}
    checked = 0

    for pretty, fn in module.get_puzzles():
        if not module.is_unusual(pretty):
            data = module.load_puzzle(fn)
            checked += 1
            nyt.extra_latin1ify_message = f"  On file {pretty}..."
            for clue in data["clues"]:
                nyt.latin1ify(clue['clue'])
            if len(nyt.store_latin1ify_errors) > 10:
                break

    for key, value in nyt.store_latin1ify_errors.items():
        print(f'    {key}: "{value}", # {chr(key).encode("unicode-escape").decode("utf-8")}')

    print(f"Checked {checked:,} files")

def main():
    args = sys.argv[1:]
    for cur in _commands:
        if len(args) == cur['args'] + 1 and args[0] == cur['cmd']:
            cur['func'](*args[1:])
            exit(0)

    print("Usage:")
    _commands.sort(key=lambda x: x['cmd'])
    for cur in _commands:
        print(f"  {cur['cmd']} {cur['desc']}")

if __name__ == "__main__":
    main()
