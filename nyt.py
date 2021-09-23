#!/usr/bin/env python3

import browser_cookie3
import requests
import os
import decompress
import re
import json
import puz
import sys
import html
import datetime

CACHE_DATA = False

BLOCK_LEFT = "\u2590"
BLOCK_MID = "\u2588"
BLOCK_RIGHT = "\u258c"
TITLE_LINE = "\u2501"

LATIN1_SUBS = {
    # For converting clues etc. into Latin-1 (ISO-8859-1) format;
    # adapted from https://github.com/kberg/kpuz
    u"“": u'"',
    u"”": u'"',
    u"‘": u"'",
    u"’": u"'",
    u"–": u"--",
    u"—": u"---",
    u"…": u"...",
    u"№": u"No.",
    u"π": u"pi",
    u"🔥": u"[emoji: fire]",
    u"🙈": u"[emoji: monkey with hands over eyes]",
    u"👉🏾": u"[emoji: hand pointing right]",
    u"👆🏻": u"[emoji: hand pointing up]",
    u"🤘🏽": u"[emoji: hand with raised index and pinky finger]",
    u"✊🏿": u"[emoji: fist]",
    u"ǐ": "i",
}


def get_browsers():
    return {
        "Chrome": browser_cookie3.chrome,
        "Chromium": browser_cookie3.chromium,
        "Opera": browser_cookie3.opera,
        "Microsoft Edge": browser_cookie3.edge,
        "Firefox": browser_cookie3.firefox,
    }


def pick_browser():
    # Ask the user for which browser they want to use
    if os.name == "nt":
        homedir = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        homedir = format(os.path.expanduser("~"))

    options = get_browsers()
    settings_file = os.path.join(homedir, 'nytxw_puz.json')
    settings = {}
    if os.path.isfile(settings_file):
        with open(settings_file) as f:
            settings = json.load(f)

    default = settings.get('default')
    while True:
        default_number = None
        keys = list(sorted(options))
        for i, desc in enumerate(keys):
            print(f" {i+1}) {desc}")
            if default is not None and desc == default:
                default_number = str(i + 1)
        
        selection = input(f"Please select a browser that's logged into NYTimes.com{' [' + default_number + ']' if default_number else ''}: ")
        try:
            if len(selection) == 0 and default_number:
                selection = default_number
            selection = int(selection)
            if selection >= 1 and selection <= len(options):
                selection = keys[selection - 1]
                break
        except:
            pass
    
    settings['default'] = selection
    if default != selection:
        with open(settings_file, 'wt') as f:
            json.dump(settings, f)

    return selection


def get_puzzle(url, browser):
    cache = {}
    if CACHE_DATA:
        # Simple cache, useful for debugging, grows to stupid
        # size over time, so it's off generally
        if os.path.isfile(".cached.json"):
            with open(".cached.json", "r", encoding="utf-8") as f:
                cache = json.load(f)

    if url not in cache:
        print(f"Loading {url}...")
        # Pull out the nytimes cookies from the user's browser
        cookies = get_browsers()[browser](domain_name='nytimes.com')
        # Load the webpage, its inline javascript includes the puzzle data
        resp = requests.get(url, cookies=cookies).content
        resp = resp.decode("utf-8")
        # Look for the javascript, it's easist here to just use a regex
        m = re.search("(pluribus|window.gameData) *= *['\"](?P<data>.*?)['\"]", resp)
        # Pull out the data element
        resp = m.group("data")
        # Which is url-encoded
        resp = decompress.decode(resp)
        # And LZString compressed
        resp = decompress.decompress(resp)
        # And a JSON blob
        resp = json.loads(resp)
        cache[url] = resp
        if CACHE_DATA:
            with open(".cached.json", "w", newline="", encoding="utf-8") as f:
                json.dump(cache, f)
    
    return cache[url]


def print_puzzle(p):
    # Dump out the puzzle, just a helper mostly to debug things
    p = p['gamePageData']
    width, height = p["dimensions"]["columnCount"], p["dimensions"]["rowCount"]
    for y in range(height):
        row = " "
        extra = ""
        shown = ""
        for x in range(width):
            cell = y * width + x
            cell = p["cells"][cell]
            if 'moreAnswers' in cell:
                # This is an oddball answer, note all the possibilities
                row += "- "
                temp = []
                if 'answer' in cell:
                    temp += [cell['answer']]
                temp += cell['moreAnswers']['valid']
                temp = f" ({', '.join(temp)})"
                if temp != shown:
                    shown = temp
                    extra += temp
            elif 'answer' in cell:
                # Normal answer, but if it's a rebus answer, show the first character
                # and the rebus answer to the side
                if len(cell['answer']) > 1:
                    extra += " " + cell['answer']
                    row += cell['answer'][0].lower() + " "
                else:
                    row += cell['answer'] + " "
            else:
                # Non-clue cell, just mark it
                row += "# "

        # Turn the "#" into block characters
        for x in range(len(row), 0, -1):
            row = row.replace(" " + "# " * x, BLOCK_LEFT + BLOCK_MID.join([BLOCK_MID] * x) + BLOCK_RIGHT)

        # And output the results
        print(" " + row + extra)


def latin1ify(s):
    # Make a Unicode string compliant with the Latin-1 (ISO-8859-1) character
    # set; the Across Lite format only supports Latin-1 encoding
    for search, replace in LATIN1_SUBS.items():
        s = s.replace(search, replace)
    return s


def data_to_puz(puzzle):
    p = puz.Puzzle()
    data = puzzle['gamePageData']

    # Basic header
    p.title = 'New York Times Crossword'
    if 'publicationDate' in data['meta']:
        year, month, day = data['meta']['publicationDate'].split('-')
        d = datetime.date(int(year), int(month), int(day))
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        dow = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
               'Saturday', 'Sunday']
        p.title = ('NY Times, ' + dow[d.weekday()] + ', ' + months[d.month] +
                   ' ' + str(d.day) + ', ' + str(d.year))
        if 'title' in data['meta']:
            p.title += ' ' + latin1ify(data['meta']['title'].upper())
    elif 'title' in data['meta']:
        p.title = latin1ify(data['meta']['title'].upper())
    p.author = ', '.join(latin1ify(c) for c in data['meta']['constructors'])
    if 'editor' in data['meta']:
        p.author += ' / ' + latin1ify(data['meta']['editor'])
    if 'copyright' in data['meta']:
        p.copyright = '© ' + data['meta']['copyright'] + ', The New York Times'

    # Pull out the size of the puzzle
    p.height = data["dimensions"]["rowCount"]
    p.width = data["dimensions"]["columnCount"]

    # Fill out the main grid
    p.solution = ''.join(latin1ify(x['answer'][0]) if 'answer' in x
                         else '.' for x in data['cells'])
    p.fill = ''.join('-' if 'answer' in x else '.' for x in data['cells'])

    # And the clues, they're HTML text here, so decode them, Across Lite expects them in
    # crossword order, not the NYT clue order, order them correctly
    seen = set()
    clues = []
    for cell in data['cells']:
        for clue in cell['clues']:
            if clue not in seen:
                seen.add(clue)
                clues.append(latin1ify(html.unescape(data['clues'][clue]['text'])))
    p.clues = clues

    # See if any of the answers is multi-character (rebus)
    if max([len(x['answer']) for x in data['cells'] if 'answer' in x]) > 1:
        # We have at least one rebus answer, so setup the rebus data fields
        rebus = p.create_empty_rebus()

        # And find all the rebus answers and add them to the data
        for cell in data['cells']:
            if 'answer' in cell and len(cell['answer']) > 1:
                rebus.add_rebus(latin1ify(cell['answer']))
            else:
                rebus.add_rebus(None)

    # All done
    return p


def main():
    if len(sys.argv) == 4:
        browser, url, output_fn = sys.argv[1:4]
        if browser not in get_browsers():
            print(f"ERROR: Unknown browser '{browser}', please select one of:")
            for key in get_browsers():
                print(f"  {key}")
            exit(1)
    else:
        browser = pick_browser()
        url = input("Enter the NY Times crossword URL: ")
        output_fn = input("Enter the output filename: ")

    # url = "https://www.nytimes.com/crosswords/game/daily/2021/06/03"
    # output_fn = "test.puz"

    # Get the puzzle from NYT, the first time this is called
    # the cookie will be archived
    puzzle = get_puzzle(url, browser)

    # Useful for debugging, hidden by default since 
    # showing the solution kinda defeats the point
    # print_puzzle(puzzle)

    # And turn the puzzle data from NYT into a puz data structure
    output = data_to_puz(puzzle)
    output.save(output_fn)
    print(f"Created {output_fn}")


if __name__ == "__main__":
    main()
