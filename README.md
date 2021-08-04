# NYT Crossword to Puz

Convert NY Times crosswords to Across Lite puzzles.

Before running, you'll need to log into the NY Times website in a browser.  Then setup the venv to download packages:
```
python -m venv .venv
.venv\Scripts\activate.bat
```

And install the packages:
```
python -m pip install -r requirements.txt
```

Then, to use:
```
nyt.py https://www.nytimes.com/crosswords/game/daily/2021/08/03 2021-08-03.puz
```
