#!/usr/bin/env python3

from datetime import datetime, timedelta
import json
import nyt
import os
import sys
import textwrap
import time

def clean_date(val):
    if val == "now":
        # Make now actually tomorrow's date, to grab tomorrow's puzzle
        # if called near 10pm, and it's harmless to go too far in the future
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        return val

def main():
    if len(sys.argv) != 5:
        print(textwrap.dedent(f"""
            Usage:
                {os.path.split(__file__)[-1]} [browser] [start date] [end date] [dest folder]

            Will download all puzzles from start to end date, inclusive, skipping over
            any files that already exist.  Can use "now" for today's date, otherwise they
            must be formatted in yyyy-mm-dd
        """))
        exit(1)

    # Crack command line options    
    browser = sys.argv[1]
    if browser not in nyt.get_browsers():
        print(f"ERROR: Unknown browser '{browser}', please select one of:")
        for key in nyt.get_browsers():
            print(f"  {key}")
        exit(1)
    start, end = clean_date(sys.argv[2]), clean_date(sys.argv[3])
    dest_folder = sys.argv[4]
    if not os.path.isdir(dest_folder):
        print(f"{dest_folder} does not exist!")

    # The endpoint that the NYTimes website uses for it's calendar
    api = "https://nyt-games-prd.appspot.com/svc/crosswords/v3/51312474/puzzles.json?publish_type=daily&sort_order=asc&sort_by=print_date&date_start=START&date_end=END"
    api = api.replace("START", start).replace("END", end)

    # Call into the helper here to load the endpoint
    cookies = nyt.load_cookies(browser)
    data = json.loads(nyt.get_url(cookies, api))

    # Run through each puzzle
    for cur in data["results"]:
        # Sometimes they publish just a PDF, ignore those
        if cur["format_type"] == "Normal":
            x = cur["print_date"]
            fn = os.path.join(dest_folder, x + ".puz")
            if not os.path.isfile(fn):
                # It's a new puzzle, grab it, conver it to a .puz file, and save it out
                data = nyt.get_puzzle_from_id(cookies, cur["puzzle_id"])
                puz = nyt.data_to_puz(data)
                puz.save(fn)
                print(f"Created '{fn}'")
                # Don't want to torture the website
                time.sleep(1.0)
            else:
                print(f"'{fn}' already exists.")

    print("All done.")

if __name__ == "__main__":
    main()
