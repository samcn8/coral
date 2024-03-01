# Coral Chess GUI by Sam Nelson

Coral is an open source, cross-platform, UCI chess GUI written in Python.

## Overview

This is a "from scratch" Python chess GUI that is compatible with Universal Chess Interface (UCI) engines.

The following features are implemented:
 * User friendly chess GUI with optional highlighting of previous move and all legal moves
 * Cross-platform by use of the tkinter graphics library
 * Support for all official chess moves, including castling, en passant, and promotion (currently to queen only)
 * Live game display in standard algebraic notation
 * Opening detection / characterization based on ECO codes
 * Use of Python multiprocessing library with engine running on separate CPU, allowing for a consistently smooth GUI
 * Ability to load and play UCI-compatible chess engines

Coral is named after one of my children's hermit crabs.  Coral (the hermit crab) always likes to switch to the prettiest shell available.  Hopefully Coral (the chess GUI) will be as aesthetically pleasing as the shells.

## Running

Coral is a Python program that uses Tkinter for cross-platform graphics and Pillow for image processing.

First, install Python3 (and pip) if your system does not already have it: https://www.python.org/downloads/.

Next, install the requirements via pip:
```
pip3 install -r requirements.txt
```

You may have to install tkinter for your system.  For instance, on Ubuntu you can do:
```
sudo apt install python3-tk
```

On macOS with Homebrew, you can do:
```
brew install python-tk
```

Finally, run Coral like this:
```
python3 coral.py
```

Note that most of my testing has been done in a macOS environment and so fonts, etc, probably look best in macOS.

## Playing

The following is an annotated screenshot of the GUI:

![Coral GUI](/resources/Screen.png)

Either white or black (or both) can be played as engines or humans.  Note that at least one player must be an engine in order to have the live evaluation bar active.

To load a UCI chess engine, click the "C" button next to either the white or black player pawn image.  This will open a file selection box.  Select the binary of the UCI chess engine to load it.  Only UCI-based chess engines are currently supported by Coral.

If you are playing against a chess engine, it is important to limit the engine in some way -- either by time (using time controls or max engine time) or depth.  If the engine is not limited, it will continue to think indefinitely and not return a valid move to the GUI.

It is most common to limit the engine by time instead of depth.  One good option is to select a game time control (say, 3+2 blitz) and then do not limit the engine further by either max depth or max time.  A second good option (which gives the human an infinite amount of time) is to not select game time controls, but limit the engine max time (to, say, 5s).

The engine hash table size should be set according to the memory on your system.  With modern computers, setting this value to something like 2000MB (2GB) is reasonable if you have at least 2GB of memory free.  Do not set this value larger than the amount of memory you have available on your system or performance will suffer.  The higher this value is set, the stronger the engine will typically play.

You can play two engines (or the same engine) against each other by loading an engine for both the white and black players.  Note that all engine limiting and hash values will be the same for both engines.

Click "New Game" when ready to start a new game.  For human players, click once to select the piece to move and then click a second time on the destination square.  Dragging and dropping pieces is not currently supported.

## Contributing

Since this is just a personal hobby project, I'm not currently accepting pull requests.  However, you are free to use the code in your own GUI development in accordance with the [GNU General Public License version 3](LICENSE) (GPL v3).

## Acknowledgments

I used the following resources to help create this program:
 * The "resources/ChessPieces.png" graphics file is from: https://commons.wikimedia.org/wiki/Category:PNG_chess_pieces/Standard_transparent
 * The "resources/*.tsv" opening books are from: https://github.com/lichess-org/chess-openings/tree/master
 * Some of the square color codes are from: https://www.color-hex.com/color-palette/8548
 * Inspiration for converting between (row, col) moves and standard algebraic notation is from the stockfish-mac source code, specifically the move_to_san method in this file: https://github.com/daylen/stockfish-mac/blob/master/Chess/san.cpp