#!/usr/bin/env python3

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import nyt

puzzle_data = """
. . . x x x x a x x x . . . x x x
n y t i m e s c r o s s w o r d s
x x x x x x x r . . x x e x x x .
x x x x x x x o . x x x b x x x .
x x . . . . x s . x x x p x x x .
x x . x x x x s x x x x a x x x x
x x . x x x x l x x x x g x . x x
x x x x x x x i x x x x e x . x x
. c o n v e r t . x x . . . . x x
. x x x x x x e . x x x x x x x x
. x x x x x x . . x x x x x x x x
x x x . . . x x x x x x x x . . .
"""

def add_clue(x, y, puzzle, x_dir, y_dir):
    puzzle["temp"][(x, y, x_dir, y_dir)] = len(puzzle['clues'])
    clue = ""
    while x < len(puzzle_data[0]) and y < len(puzzle_data) and puzzle_data[y][x] != ".":
        clue += puzzle_data[y][x]
        x += x_dir
        y += y_dir
    if "x" in clue:
        clue = "-"
    puzzle['clues'].append({"text": clue.upper()})


def main():
    global puzzle_data

    puzzle = {
        "dimensions": {
            "rowCount": 0,
            "columnCount": 0,
        },
        "cells": [],
        "clues": [
        ],
        "meta": {
            "constructors": [],
        },
        "temp": {},
    }
    output_fn = "logo_puzzle.puz"

    puzzle_data = [x.strip("\r\n").split(" ") for x in puzzle_data.split("\n") if len(x.strip("\r\n"))]

    for y in range(len(puzzle_data)):
        for x in range(len(puzzle_data[0])):
            if puzzle_data[y][x] != ".":
                if x < len(puzzle_data[0]) - 1:
                    if x == 0:
                        if puzzle_data[y][x + 1] != ".":
                            add_clue(x, y, puzzle, 1, 0)
                    else:
                        if puzzle_data[y][x-1] == "." and puzzle_data[y][x+1] != ".":
                            add_clue(x, y, puzzle, 1, 0)
                if y < len(puzzle_data) - 1:
                    if y == 0:
                        if puzzle_data[y + 1][x] != ".":
                            add_clue(x, y, puzzle, 0, 1)
                    else:
                        if puzzle_data[y-1][x] == "." and puzzle_data[y+1][x] != ".":
                            add_clue(x, y, puzzle, 0, 1)

    puzzle['dimensions']['columnCount'] = len(puzzle_data[0])
    puzzle['dimensions']['rowCount'] = len(puzzle_data)

    for y, row in enumerate(puzzle_data):
        for x, cell in enumerate(row):
            if cell == ".":
                puzzle['cells'].append({'clues': []})
            else:
                puzzle['cells'].append({'answer': cell.upper(), 'clues': []})
            if (x, y, 1, 0) in puzzle['temp']:
                puzzle['cells'][-1]['clues'].append(puzzle['temp'][(x, y, 1, 0)])
            if (x, y, 0, 1) in puzzle['temp']:
                puzzle['cells'][-1]['clues'].append(puzzle['temp'][(x, y, 0, 1)])

    puzzle['gamePageData'] = puzzle

    nyt.print_puzzle(puzzle)
    output = nyt.data_to_puz(puzzle)
    output.save(output_fn)
    print(f"Created {output_fn}")


if __name__ == "__main__":
    main()
