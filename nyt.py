#!/usr/bin/env python3

from email.quoprimime import unquote
import browser_cookie3
import requests
import requests.utils
import os
import decompress
import re
import json
import puz
import sys
import html
import datetime
import time
import base64
import version

CACHE_DATA = False
# Debug code to log all URL requests and their responses, set to None
# to disable logging, any string enables (and is replaced with a log filename)
LOG_CALLS = None

# These unicode characters are just used to draw the crossword grid to stdout
BLOCK_LEFT = "\u2590"
BLOCK_MID = "\u2588"
BLOCK_RIGHT = "\u258c"
TITLE_LINE = "\u2501"

# Different possibilities for each cell in the NYT's JSON data structure
NYT_TYPE_BLOCK = 0     # Black cell, no clues or answer
NYT_TYPE_NORMAL = 1    # Normal cell, could be a rebus
NYT_TYPE_CIRCLED = 2   # Cell with a circle around it as for letters part of a theme
NYT_TYPE_GRAY = 3      # A cell filled in as gray
NYT_TYPE_INVISIBLE = 4 # An "invisible" cell, generally something outside the main grid

LATIN1_SUBS = {
    # For converting clues etc. into Latin-1 (ISO-8859-1) format;
    # value None means let the encoder insert a Latin-1 equivalent
    u'“': u'"',
    u'”': u'"',
    u'‘': u"'",
    u'’': u"'",
    u'–': u'-',
    u'—': u'--',
    u'…': u'...',
    u'№': u'No.',
    u'π': u'pi',
    u'€': u'EUR',
    u'•': u'*',
    u'†': u'[dagger]',
    u'‡': u'[double dagger]',
    u'™': u'[TM]',
    u'‹': u'<',
    u'›': u'>',
    u'←': u'<--',
    u'■': None,
    u'☐': None,
    u'→': u'-->',
    u'♣': None,
    u'√': None,
    u'♠': None,
    u'✓': None,
    u'♭': None,
    u'♂': None,
    u'★': u'*',
    u'θ': u'theta',
    u'β': u'beta',
    u'Č': None,
    u'𝚫': u'Delta',
    u'❤︎': None,
    u'✔': None,
    u'⚓': None,
    u'♦': None,
    u'♥': None,
    u'☹': None,
    u'☮': None,
    u'☘': None,
    u'◯': None,
    u'▢': None,
    u'∑': None,
    u'∃': None,
    u'↓': None,
    u'⁎': u'*',
    u'η': u'eta',
    u'α': u'alpha',
    u'Ω': u'Omega',
    u'ō': None,
}
# Some rules to remove HTML like things with text versions for the .puz files
HTML_TO_TEXT_RULES = [
    ("<i>(.*?)</i>", "_\\1_"),              # "<i>Italic</i>" -> "_Italic_"
    ("<em>(.*?)</em>", "_\\1_"),            # "<em>Italic</em>" -> "_Italic_"
    ("<sub>(.*?)</sub>", "\\1"),            # "KNO<sub>3</sub>" -> "KNO3"
    ("<sup>([0-9 ]+)</sup>", "^\\1"),       # "E=MC<sup>2</sup>" -> "E=MC^2"
    ("<sup>(.*?)</sup>", "\\1"),            # "103<sup>rd</sup>" -> "103rd" (Note, after the numeric 'sup')
    ("<br( /|)>", " / "),                   # "A<br>B<br>C" -> "A / B / C"
    ("<s>(.*?)</s>", "[*cross out* \\1]"),  # "<s>Crossed Out</s>" -> "[*cross out* Crossed out]"
    ("<[^>]+>", ""),                        # Remove other things that look like HTML, but leave bare "<" alone.
    ("&nbsp;", " "),                        # Replace HTML's non-breaking spaces into normal spaces
]


# Work around https://github.com/borisbabic/browser_cookie3/issues/104
def chrome_bugfix(**kargs):
    args = {
        'linux_cookies':[
                '~/.config/google-chrome/Default/Cookies',
                '~/.config/google-chrome-beta/Default/Cookies'
            ],
        'windows_cookies':[
                {'env':'APPDATA', 'path':'..\\Local\\Google\\Chrome\\User Data\\Default\\Cookies'},
                {'env':'APPDATA', 'path':'..\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies'},
                {'env':'LOCALAPPDATA', 'path':'Google\\Chrome\\User Data\\Default\\Cookies'},
                {'env':'LOCALAPPDATA', 'path':'Google\\Chrome\\User Data\\Default\\Network\\Cookies'},
                {'env':'APPDATA', 'path':'Google\\Chrome\\User Data\\Default\\Cookies'},
                {'env':'APPDATA', 'path':'Google\\Chrome\\User Data\\Default\\Network\\Cookies'}
            ],
        'osx_cookies': ['~/Library/Application Support/Google/Chrome/Default/Cookies'],
        'windows_keys': [
                {'env':'APPDATA', 'path':'..\\Local\\Google\\Chrome\\User Data\\Local State'},
                {'env':'LOCALAPPDATA', 'path':'Google\\Chrome\\User Data\\Local State'},
                {'env':'APPDATA', 'path':'Google\\Chrome\\User Data\\Local State'}
            ],
        'os_crypt_name':'chrome',
        'osx_key_service' : 'Chrome Safe Storage',
        'osx_key_user' : 'Chrome'
    }
    for key, value in kargs.items():
        args[key] = value    

    cookies = browser_cookie3.ChromiumBased(browser='Chrome', **args)
    return cookies.load()


# Work around https://github.com/borisbabic/browser_cookie3/issues/104
def chromium_bugfix(**kargs):
    args = {
        'linux_cookies':['~/.config/chromium/Default/Cookies'],
        'windows_cookies':[
                {'env':'APPDATA', 'path':'..\\Local\\Chromium\\User Data\\Default\\Cookies'},
                {'env':'APPDATA', 'path':'..\\Local\\Chromium\\User Data\\Default\\Network\\Cookies'},
                {'env':'LOCALAPPDATA', 'path':'Chromium\\User Data\\Default\\Cookies'},
                {'env':'LOCALAPPDATA', 'path':'Chromium\\User Data\\Default\\Network\\Cookies'},
                {'env':'APPDATA', 'path':'Chromium\\User Data\\Default\\Cookies'},
                {'env':'APPDATA', 'path':'Chromium\\User Data\\Default\\Network\\Cookies'}
        ],
        'osx_cookies': ['~/Library/Application Support/Chromium/Default/Cookies'],
        'windows_keys': [
                {'env':'APPDATA', 'path':'..\\Local\\Chromium\\User Data\\Local State'},
                {'env':'LOCALAPPDATA', 'path':'Chromium\\User Data\\Local State'},
                {'env':'APPDATA', 'path':'Chromium\\User Data\\Local State'}
        ],
        'os_crypt_name':'chromium',
        'osx_key_service' : 'Chromium Safe Storage',
        'osx_key_user' : 'Chromium'
    }
    for key, value in kargs.items():
        args[key] = value    

    cookies = browser_cookie3.ChromiumBased(browser='Chromium', **args)
    return cookies.load()


def get_browsers():
    return {
        # Work around https://github.com/borisbabic/browser_cookie3/issues/104
        # "Chrome": browser_cookie3.chrome,
        # "Chromium": browser_cookie3.chromium,
        "Chrome": chrome_bugfix,
        "Chromium": chromium_bugfix,

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


# Internal helper to load a URL, optionally log the data, to make
# debugging remotely a tiny bit easier
def get_url(cookies, url):
    cookies = requests.utils.dict_from_cookiejar(cookies)
    cookies = requests.utils.cookiejar_from_dict(cookies)
    if LOG_CALLS is not None:
        with open(LOG_CALLS, "a", newline="", encoding="utf-8") as f:
            f.write("URL " + url + "\n")
            f.write("COOKIES " + json.dumps(cookies, default=str) + "\n")
            try:
                f.write("COOKIES_RAW " + json.dumps(requests.utils.dict_from_cookiejar(cookies)) + "\n")
            except:
                pass
    resp = requests.get(url, cookies=cookies).content
    if LOG_CALLS is not None:
        with open(LOG_CALLS, "a", newline="", encoding="utf-8") as f:
            f.write("RESPONSE " + base64.b64encode(resp).decode("utf-8") + "\n")
    resp = resp.decode("utf-8")
    return resp


def load_cookies(browser):
    # Pull out the nytimes cookies from the user's browser
    cookies = get_browsers()[browser](domain_name='nytimes.com')
    return cookies


def get_puzzle_from_id(cookies, puzzle_id):
    # Get the puzzle itself
    puzzle_url = f"https://nyt-games-prd.appspot.com/svc/crosswords/v6/puzzle/{puzzle_id}.json"
    new_format = get_url(cookies, puzzle_url)
    new_format = json.loads(new_format)

    # The response is formatted somewhat differently than it used to be, so create a format
    # that looks like it used to
    resp = new_format["body"][0]
    resp["meta"] = {}
    # TODO: Notes might be stored elsewhere, need to verify
    for cur in ["publicationDate", "title", "editor", "copyright", "constructors", "notes"]:
        if cur in new_format:
            resp["meta"][cur] = new_format[cur]
    resp["dimensions"]["columnCount"] = resp["dimensions"]["width"]
    resp["dimensions"]["rowCount"] = resp["dimensions"]["height"]

    resp["gamePageData"] = resp

    return resp


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

        cookies = load_cookies(browser)
        for _ in range(4):
            # Load the webpage, its inline javascript includes the puzzle data
            resp = get_url(cookies, url)

            # NY Times is moving to a new system for puzzles, handle both, since 
            # it doesn't seem to have migrated 100% of the accounts out there

            # Option #1, see if this is the old style encoded javascript blob:
            # Look for the javascript, it's easist here to just use a regex
            m = re.search("(pluribus|window.gameData) *= *['\"](?P<data>.*?)['\"]", resp)
            if m is not None:
                # Pull out the data element
                resp = m.group("data")
                if "%" in resp:
                    # Which is url-encoded
                    resp = decompress.decode(resp)
                    # And LZString compressed
                    resp = decompress.decompress(resp)
                else:
                    # New format, this is now base64 encoded
                    resp = base64.b64decode(resp).decode("utf-8")
                    # And _then_ url-encoded
                    resp = decompress.decode(resp)
                # And a JSON blob
                resp = json.loads(resp)
                # All done, we can stop retries
                break

            # Option #2, try the new version with a gaming REST endpoint:
            # Try to find the puzzle description:
            m = re.search("window\\.gameData *= *(?P<json>{.*?})", resp)
            if m is not None:
                # Pull out the puzzle key
                key = m.group("json")
                key = json.loads(key)
                key = key['filename']

                # Request the puzzle meta-data
                api = f"https://nyt-games-prd.appspot.com/svc/crosswords/v6/puzzle/{key}.json"
                metadata = get_url(cookies, api)
                metadata = json.loads(metadata)

                resp = get_puzzle_from_id(cookies, metadata['id'])

                # All done
                break

            # Something didn't look right, try again
            time.sleep(1)

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
    # set; the Across Lite v1.3 format only supports Latin-1 encoding

    # Use table to convert the most common Unicode glyphs
    for search, replace in LATIN1_SUBS.items():
        if replace is not None:
            s = s.replace(search, replace)

    # Convert anything remaining using replacements like '\N{WINKING FACE}'
    s = s.encode('ISO-8859-1', 'namereplace').decode('ISO-8859-1')

    # Replace HTML like things into plain text
    for pattern, repl in HTML_TO_TEXT_RULES:
        s = re.sub(pattern, repl, s)

    return s


def gridchar(c):
    if 'answer' in c:
        # The usual case: just one letter
        return latin1ify(c['answer'][0])
    if 'moreAnswers' in c:
        # 2022-05-01 'Blank Expressions' includes grid answers without
        # an actual 'answer', only an array of 'moreAnswers'
        for a in c['moreAnswers']:
            if len(a) == 1:
                # First single-character one
                return latin1ify(a)
        # No single-character answers
        return 'X'

    # Black square
    return '.'


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
    p.solution = ''.join(gridchar(x) for x in data['cells'])
    p.fill = ''.join('-' if 'answer' in x else '.' for x in data['cells'])

    # And the clues, they're HTML text here, so decode them, Across Lite expects them in
    # crossword order, not the NYT clue order, order them correctly
    seen = set()
    clues = []
    for cell in data['cells']:
        for clue in cell.get('clues', []):
            if clue not in seen:
                seen.add(clue)
                temp = data['clues'][clue]['text']
                if isinstance(temp, list):
                    temp = temp[0]
                if isinstance(temp, dict):
                    temp = temp.get("plain", "")
                clues.append(latin1ify(html.unescape(temp)))
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

    # See if any grid squares are marked up with circles
    if any(x['type'] in (NYT_TYPE_CIRCLED, NYT_TYPE_GRAY) for x in data['cells'] if 'type' in x):
        markup = p.markup()
        markup.markup = [0] * (p.width * p.height)

        for i, cell in enumerate(data['cells']):
            if 'type' in cell and cell['type'] in (NYT_TYPE_CIRCLED, NYT_TYPE_GRAY):
                markup.markup[cell.get('index', i)] = puz.GridMarkup.Circled

    # Check for any notes in puzzle (e.g., Sep 11, 2008)
    if data['meta'].get('notes', None) is not None:
        p.notes = '\n\n'.join(latin1ify(x['text']) for x in data['meta']['notes']
                              if 'text' in x)

    # All done
    return p

def version_warn():
    ver = version.get_ver_from_github()
    if ver is not None:
        if ver > version.VERSION:
            print(f"Info: Version {ver} is available, consider upgrading if any issues occur")
            print("")

def main():
    if len(sys.argv) == 4:
        browser, url, output_fn = sys.argv[1:4]
        if browser not in get_browsers():
            print(f"ERROR: Unknown browser '{browser}', please select one of:")
            for key in get_browsers():
                print(f"  {key}")
            exit(1)
    else:
        version_warn()
        browser = pick_browser()
        url = input("Enter the NY Times crossword URL: ")
        if len(url) == 0:
            print("No URL specified")
            exit(1)
        output_fn = input("Enter the output filename: ")
        if len(url) == 0:
            print("No output file specified")
            exit(1)

    global LOG_CALLS
    if LOG_CALLS is not None:
        LOG_CALLS = output_fn + ".log"
        with open(LOG_CALLS, "a", newline="", encoding="utf-8") as f:
            f.write("LOG " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + "\n")

    try:
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
    except:
        print("ERROR! " * 10)
        import traceback
        traceback.print_exc()
        print("ERROR! " * 10)
        print("Settings: ", [browser, url, output_fn, version.VERSION])
        print("")
        print("Please report issues to https://www.reddit.com/user/nobody514/")
        print("")
        input("Press enter to continue...")


if __name__ == "__main__":
    main()
