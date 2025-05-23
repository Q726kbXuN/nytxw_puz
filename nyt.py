#!/usr/bin/env python3

import base64, browser_cookie3, datetime, decompress, html, json
import os, puz, re, requests, requests.utils, sys, time, version
if sys.version_info >= (3, 11): from datetime import UTC
else: import datetime as datetime_fix; UTC=datetime_fix.timezone.utc

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
    # For converting clues etc. into Latin-1 (ISO-8859-1) format
    9: ' ', 10: ' ', 13: ' ', 133: '', 134: ' ', 135: ' ', 140: ' ', 142: ' ', 144: ' ', 145: ' ', 146: ' ', 147: ' ', 
    148: ' ', 150: ' ', 151: ' ', 154: ' ', 160: ' ', 161: '!', 162: 'cents', 163: 'Pounds', 165: 'Yen', 
    167: '[Section sign]', 169: '[Copyright symbol]', 172: '', 173: '', 174: '[Registered trademark]', 175: '', 
    176: 'degrees', 177: '+/-', 178: '2', 180: "'", 182: '[Pilcrow]', 183: '*', 185: '1', 186: 'degrees', 188: '1/4', 
    189: '1/2', 190: '3/4', 191: '?', 192: 'A', 193: 'A', 194: 'A', 195: 'A', 196: 'A', 197: 'A', 198: 'AE', 199: 'C', 
    200: 'E', 201: 'E', 202: 'E', 203: 'E', 204: 'I', 205: 'I', 206: 'I', 208: 'D', 209: 'N', 210: 'O', 211: 'O', 
    212: 'O', 213: 'O', 214: 'O', 215: '*', 216: 'O', 218: 'U', 220: 'U', 223: 'B', 224: 'a', 225: 'a', 226: 'a', 
    227: 'a', 228: 'a', 229: 'a', 230: 'ae', 231: 'c', 232: 'e', 233: 'e', 234: 'e', 235: 'e', 236: 'i', 237: 'i', 
    238: 'i', 239: 'i', 240: 'o', 241: 'n', 242: 'o', 243: 'o', 244: 'o', 245: 'o', 246: 'o', 247: '/', 248: 'o', 
    249: 'u', 250: 'u', 251: 'u', 252: 'u', 257: 'a', 259: 'a', 261: 'a', 263: 'c', 268: 'C', 269: 'c', 275: 'e', 
    297: 'i', 304: 'I', 305: 'i', 322: '', 324: 'n', 333: 'o', 338: 'AE', 339: 'ae', 345: 'r', 346: 'S', 351: 's', 
    352: 'S', 353: 's', 361: 'u', 363: 'u', 382: 'z', 402: 'f', 432: 'u', 464: 'i', 601: 'e', 621: '', 624: '', 
    628: 'N', 688: 'h', 690: 'Palatalization', 691: 'r', 695: 'w', 699: "'", 701: "'", 710: '^', 738: 's', 769: '', 
    916: '[Greek letter delta]', 919: 'H', 929: 'P', 931: '[Greek letter sigma]', 937: '[Greek letter omega]', 
    945: 'Greek letter alpha', 946: '[Greek letter beta]', 948: 'o', 950: '', 951: '[Greek Letter Eta]', 
    952: '[Greek letter theta]', 955: '[Greek letter lambda]', 956: 'u', 957: '', 958: '', 960: 'Pi', 961: 'p', 
    964: '', 967: '', 968: '[Greek letter psi]', 969: 'w', 1009: 'g', 1071: 'R', 2090: '', 2934: '', 3607: '', 
    3611: '', 3618: '', 3619: '', 3624: '', 3632: '', 3647: '[Thai Currency]', 3648: '', 3652: '', 3725: '', 3732: '', 
    3738: '', 3754: '', 3760: '', 3762: '', 3765: '', 6496: '', 6503: '', 6637: '', 7335: '', 7392: '', 7491: 'a', 
    7497: 'e', 7511: 't', 7512: 'u', 7584: 'f', 7589: '', 7590: 'x', 7789: 't', 7843: 'a', 7845: 'a', 7865: 'e', 
    7871: 'e', 7879: 'e', 7885: 'o', 7887: 'o', 7889: 'o', 7897: 'o', 7903: '', 7909: 'u', 7911: 'u', 7921: 'u', 
    8195: ' ', 8200: ' ', 8201: ' ', 8203: '', 8205: '', 8209: '-', 8211: '-', 8212: '-', 8216: "'", 8217: "'", 
    8220: '"', 8221: '"', 8224: '[Dagger]', 8225: '[Dagger]', 8226: '*', 8230: '...', 8239: ' ', 8240: '%', 8242: "'", 
    8243: '"', 8270: '*', 8288: '', 8319: 'n', 8322: '2', 8323: '3', 8326: '6', 8327: '7', 8328: '8', 8364: 'Euro', 
    8383: 'Bitcoin', 8463: 'n', 8482: '[Trademark symbol]', 8592: '[Left Arrow]', 8593: '[Up arrow]', 
    8594: '[Right arrow]', 8595: '[Down arrow]', 8617: '[Leftwards Arrow with Hook]', 8710: '[Triangle]', 8722: '-', 
    8730: '[Square root]', 8734: '[Infinity]', 8743: '[and]', 8744: '[or]', 8804: '<=', 8964: '[Down Arrowhead]', 
    8984: '[Looped Square]', 8986: '[Watch]', 9167: '[Eject]', 9186: '[White Trapezium]', 9194: '[Fast Reverse]', 
    9200: '[Alarm Clock]', 9203: '[Hourglass Not Done]', 9208: '[Pause Button]', 
    9634: '[Square with Rounded Corners]', 9651: '[Triangle]', 9654: '[Right Arrow]', 9711: '[Large circle]', 
    9728: '*', 9730: '[Umbrella]', 9733: '[Star]', 9749: '[Hot Beverage]', 9752: '[Shamrock]', 
    9757: '[Index Pointing Up]', 9758: '[Right Pointing]', 9759: '[Down Pointing]', 9760: '[Skull and Crossbones]', 
    9774: '[Peace Symbol]', 9775: '[Yin Yang]', 9785: '[Frowning Face]', 9786: '[Smiling Face]', 
    9792: '[Female Sign]', 9794: '[Male Sign]', 9800: '[Aries]', 9804: '[Leo]', 9824: '[Spade]', 9827: '[Club]', 
    9829: '[Heart]', 9830: '[Diamond]', 9835: '[Beamed Eighth Notes]', 9837: '[Flat]', 9839: '[Sharp]', 
    9851: '[Recycling Symbol]', 9872: '[Flag]', 9879: 'Alembic', 9883: '[Atom]', 9888: '[Warning]', 
    9895: '[Transgender Symbol]', 9904: '[Coffin]', 9918: '[Baseball]', 9961: '[Shinto Shrine]', 9973: '[Sailboat]', 
    9975: '[Skier]', 9986: '[Scissors]', 9992: '[Airplane]', 9993: '[Envelope]', 9994: '[Raised Fist]', 
    9996: '[V sign]', 10014: '[Cross]', 10052: '[Snowflake]', 10084: '[Red Heart]', 10145: '[Right Arrow]', 
    11014: '[Up arrow]', 11088: '[Star]', 12356: '', 12399: '', 12484: '', 19177: '', 30820: '', 30825: '', 34864: '', 
    35685: '', 36005: '', 36064: '', 36077: '', 38913: '', 38924: '', 38945: '', 38948: '', 38950: '', 38959: '', 
    38963: '', 38964: '', 39081: '', 39200: '', 39205: '', 39264: '', 39268: '', 39411: '', 39791: '', 40101: '', 
    40105: '', 40161: '', 40162: '', 40181: '', 40229: '', 55308: '[Sparrow]', 55356: '', 55357: '[Astonished Face]', 
    55358: '[Robot]', 55622: '', 55623: '', 55639: '', 56186: '', 65038: '', 65039: '', 65533: '', 
}

# Replace some emoticons and other oddball phrases that might lose meaning 
# if the individual characters are fixed
EMOTICON_SUBS = {
    '\u204e*\u2021:-)}}}}': '**|:-)}}}}',
    '==}:\u2021]]': '==}:|]]',
    '(\xb6-)': '(P-)',
    '*\u2021(:o)}': '*|(:o)}',
    '\xaf\\_(\u30c4)_/\xaf': '[Shrug Emoticon]',
    '\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28\u0e44\u0e17\u0e22': '[Thailand]',
    '\u0eaa\u0eb0\u0e9a\u0eb2\u0e8d\u0e94\u0eb5': '[Hello in Lao]',
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
    ("&quot;", '"'),                        # Replace some other entities
    ("&mdash;", "-"),
    ("&amp;", '&'),
    ("&vert;", "|"),
    ("&diams;", "\u2666"),
    ("&hearts;", "\u2665"),
    ("&spades;", "\u2660"),
    ("&clubs;", "\u2663"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&bull;", "*"),
                                            # Replace all numbered entities with the character
    ("&#([0-9]+);", lambda m: chr(int(m.group(1)))),
    ("&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16))),
]


def get_browsers():
    return {
        "Chrome": browser_cookie3.chrome,
        "Chromium": browser_cookie3.chromium,

        "Opera": browser_cookie3.opera,
        "Microsoft Edge": browser_cookie3.edge,
        "Firefox": browser_cookie3.firefox,
    }


def get_user_filename(filename):
    if os.name == "nt":
        homedir = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        homedir = format(os.path.expanduser("~"))
    return os.path.join(homedir, filename)


def pick_browser():
    # Ask the user for which browser they want to use
    options = get_browsers()
    settings_file = get_user_filename('nytxw_puz.json')
    settings = {}
    if os.path.isfile(settings_file):
        with open(settings_file) as f:
            settings = json.load(f)

    if os.path.isfile(get_cookie_cache_filename()):
        options["Cached Cookies"] = None

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


def get_cookie_cache_filename():
    return get_user_filename("nytxw_puz.cookies.json")


def load_cookies(browser):
    # Pull out the nytimes cookies from the user's browser
    # Cache the information to avoid a roundtrip to the browser if possible
    if browser == "Cached Cookies":
        with open(get_cookie_cache_filename(), "rt") as f:
            cookies = json.load(f)
    else:
        cookies = get_browsers()[browser](domain_name='nytimes.com')
        cookies = requests.utils.dict_from_cookiejar(cookies)
        with open(get_cookie_cache_filename(), "wt") as f:
            json.dump(cookies, f)

    return cookies


def get_puzzle_from_id(cookies, puzzle_id):
    # Get the puzzle itself
    puzzle_url = f"https://www.nytimes.com/svc/crosswords/v6/puzzle/{puzzle_id}.json"
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
                api = f"https://www.nytimes.com/svc/crosswords/v6/puzzle/{key}.json"
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


store_latin1ify_errors = None
extra_latin1ify_message = None
def latin1ify(s):
    source_string = s

    # Make a Unicode string compliant with the Latin-1 (ISO-8859-1) character
    # set; the Across Lite v1.3 format only supports Latin-1 encoding

    # Replace the emoticons first with an ASCII version:
    for k, v in EMOTICON_SUBS.items():
        s = s.replace(k, v)

    # Replace HTML like things into plain text
    for pattern, repl in HTML_TO_TEXT_RULES:
        s = re.sub(pattern, repl, s)

    # Use table to convert the most common Unicode glyphs
    s = s.translate(LATIN1_SUBS)

    # Convert anything remaining using replacements like '\N{WINKING FACE}'
    s = s.encode('ISO-8859-1', 'namereplace').decode('ISO-8859-1')

    s = s.strip()

    # Warn on anything left over
    for x in s:
        if not ' ' <= x <= '~':
            if extra_latin1ify_message is not None:
                print(extra_latin1ify_message)
            print(f"Warning: '{x.encode('unicode_escape').decode("utf-8")}', or '{x}' will likely cause problems")
            print(f" Source: '{source_string}'")
            print(f"Escaped: '{source_string.encode('unicode_escape').decode("utf-8")}'")
            if store_latin1ify_errors is not None:
                store_latin1ify_errors[ord(x)] = x

    return s


def gridchar(c):
    if 'answer' in c:
        # The usual case: just one letter
        return latin1ify(c['answer'][0])
    if 'moreAnswers' in c:
        # 2022-05-01 'Blank Expressions' includes grid answers without
        # an actual 'answer', only an array of 'moreAnswers'
        more = c.get('moreAnswers', [])
        if isinstance(more, dict):
            more = more['valid']

        for a in more:
            if len(a) == 1:
                # First single-character one
                return latin1ify(a)
        # No single-character answers
        return 'X'

    # Black square
    return '.'


def gridrebus(c):
    if 'answer' in c:
        if len(c['answer']) > 1:
            # This cell has a rebus answer, but first, see if we can find a 
            # answer that's already easy to use
            more = c.get('moreAnswers', [])
            if isinstance(more, dict):
                more = more['valid']
            answers = [c['answer']] + more
            for possible in answers:
                if possible == latin1ify(possible) and len(possible) > 1:
                    # This is a possibility that works well
                    return possible
            # Nothing useful, just use the first clue
            return answers[0]
    return None


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
            rebus.add_rebus(gridrebus(cell))

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
        if len(output_fn) == 0:
            print("No output file specified")
            exit(1)

    global LOG_CALLS
    if LOG_CALLS is not None:
        LOG_CALLS = output_fn + ".log"
        with open(LOG_CALLS, "a", newline="", encoding="utf-8") as f:
            f.write("LOG " + datetime.datetime.now(UTC).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S") + "\n")

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
        output.save(os.path.expanduser(output_fn))
        print(f"Created {output_fn}")
        if sys.platform == 'darwin' and hasattr(sys, 'ps1'):
            input("Press enter to continue...")
    except:
        print("ERROR! " * 10)
        import traceback
        traceback.print_exc()
        print("ERROR! " * 10)
        print("Settings: ", [browser, url, output_fn, version.VERSION])
        print("")
        print("Please report issues to https://www.reddit.com/user/nobody514/")
        print("")
        if hasattr(sys, 'ps1'):
            input("Press enter to continue...")


if __name__ == "__main__":
    main()
