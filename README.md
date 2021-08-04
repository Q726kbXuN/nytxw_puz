# NYT Crossword to Puz

Convert NY Times crosswords to Across Lite puzzles.

To run this, first download and decompress the [release](https://github.com/Q726kbXuN/nytxw_puz/releases/latest/download/nytxw_puz.zip).  Then, run the executable, and answer the two questions:

```
Enter the NY Times crossword URL: https://www.nytimes.com/crosswords/game/daily/1994/02/14
Enter the output filename: example.puz
Loading https://www.nytimes.com/crosswords/game/daily/1994/02/14...
Created example.puz
```

Alternativly, you can pass in the URL and filename from the command line.

To run the Python script directly, clone this repo, then setup the venv to download packages:
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
