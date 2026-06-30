# TESTING.md

## An Chess Engine Testing Evidence

**Project:** An Chess Engine  
**Course:** HSC Software Engineering  
**Test type:** Manual GUI testing, rule validation testing, usability testing, timer testing and regression testing  
**Main run command:**

```bash
python -m anchessengine.gui
```

**Terminal engine run command, if required:**

```bash
python -m anchessengine.game
```

---

## 1. Testing Purpose

The purpose of testing was to confirm that An Chess Engine functions correctly after being modified from a terminal-based chess engine into an interactive graphical chess application. Testing focused on confirming that users can operate the program through the Pygame GUI, move pieces by clicking, view legal move highlights, use the lobby menu, use timers, view move history, surrender, return to the menu and follow core chess rules.

Testing also aimed to identify and fix issues caused by the GUI layer, including incorrect legal move highlighting, pieces moving to illegal squares, rooks not moving horizontally from edge files, kings moving into danger, repeated warning messages and timer behaviour when a player runs out of time.

---

## 2. Test Environment

| Item | Details |
|---|---|
| Operating System | Windows |
| IDE | Visual Studio Code |
| Language | Python 3.12 |
| GUI Library | Pygame |
| Main GUI File | `anchessengine/gui.py` |
| Core Engine Files | `anchessengine/position.py`, `anchessengine/move.py`, `anchessengine/bitboard_helpers.py` |
| Assets | `assets/pieces/` chess piece images, `AChess.png` logo |
| Version Control | GitHub |

---

## 3. Installation and Setup Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| SET-01 | Virtual environment activates | Run `.\.venv\Scripts\Activate.ps1` | Terminal shows `(.venv)` | Virtual environment activates | Pass |
| SET-02 | Dependencies install | Run `python -m pip install -r requirements.txt` | Required packages install without error | NumPy and Pygame install | Pass |
| SET-03 | Pygame import test | Run `python -c "import pygame; print(pygame.version.ver)"` | Pygame version prints | Pygame version displays | Pass |
| SET-04 | GUI launches | Run `python -m anchessengine.gui` | Lobby window opens | GUI opens successfully | Pass |
| SET-05 | Terminal version still runs | Run `python -m anchessengine.game` | Terminal board loads | Terminal version remains available | Pass |

---

## 4. Lobby and Menu UI Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| UI-01 | Lobby screen displays | Launch GUI | Start menu appears before game board | Lobby screen appears first | Pass |
| UI-02 | Logo appears | Check left side of menu | `AChess.png` logo appears | Logo appears on left side | Pass |
| UI-03 | Flavour text displays | Read left side text | Chess-themed description appears | Flavour text displays | Pass |
| UI-04 | Player-vs-player option removed | Check menu options | No unnecessary player-vs-player dropdown appears | Menu is simplified | Pass |
| UI-05 | First turn dropdown works | Click first-turn option | Option expands or cycles between available choices | User can select first-turn option | Pass |
| UI-06 | Timer dropdown works | Click timer option | Timer choices appear or cycle | Timer setting can be changed | Pass |
| UI-07 | Start Game button works | Click Start Game | Game screen opens | Game screen loads | Pass |
| UI-08 | Quit button works | Click Quit | Program closes | Program exits | Pass |
| UI-09 | Resizable menu | Resize window | Menu elements stay within frame | Menu scales with window | Pass |
| UI-10 | Solid colour layout | View menu | Left and right panels use solid colours | Solid menu layout displays | Pass |

---

## 5. Chess Board GUI Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| GUI-01 | Board displays | Start game | 8x8 chessboard appears | Board appears | Pass |
| GUI-02 | Piece images display | Start game | All pieces appear on starting squares | Piece images appear correctly | Pass |
| GUI-03 | Board coordinates display | Start game | Files `a-h` and ranks `1-8` display | Coordinates display | Pass |
| GUI-04 | Piece selection | Click own piece | Selected square highlights | Highlight appears | Pass |
| GUI-05 | Empty square click | Click empty square without selected piece | No piece selected | Empty square does not remain selected | Pass |
| GUI-06 | Opponent piece click | Click opponent piece on current turn | Program does not select opponent piece | Selection is rejected | Pass |
| GUI-07 | Repeated warning control | Click opponent piece repeatedly | Warning should not flood move history/status | Warning message is limited | Pass |
| GUI-08 | Legal move highlights | Select a piece | Legal target squares highlight in a different colour | Legal moves are shown | Pass |
| GUI-09 | Capture highlights | Select piece with available capture | Capture square has capture highlight | Capture square is visually different | Pass |
| GUI-10 | Move execution | Click piece then legal target | Piece moves and board updates | Move is completed | Pass |
| GUI-11 | Illegal move rejection | Try illegal move | Piece does not move | Illegal move rejected | Pass |

---

## 6. Basic Piece Movement Tests

| Test ID | Piece | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| MOVE-01 | White pawn single move | `e2 → e3` | Pawn moves one square forward | Pawn moves | Pass |
| MOVE-02 | White pawn double move | `e2 → e4` from starting position | Pawn moves two squares | Pawn moves | Pass |
| MOVE-03 | Blocked pawn | Place piece in front of pawn and try forward move | Pawn cannot move through piece | Move rejected | Pass |
| MOVE-04 | Pawn diagonal capture | Move pawn diagonally onto enemy piece | Enemy piece captured | Capture works | Pass |
| MOVE-05 | Knight movement | Select `g1` knight | Only legal knight moves appear, such as `f3` and `h3` at start | Correct knight moves shown | Pass |
| MOVE-06 | Knight illegal movement | Try moving knight like a bishop/rook | Move rejected | Illegal move rejected | Pass |
| MOVE-07 | Bishop movement | Clear diagonal and move bishop | Bishop moves diagonally | Bishop moves | Pass |
| MOVE-08 | Bishop blocked path | Try moving bishop through piece | Move rejected | Blocked path rejected | Pass |
| MOVE-09 | Rook vertical movement | Clear file and move rook up/down | Rook moves vertically | Rook moves | Pass |
| MOVE-10 | Rook horizontal movement | Clear rank and move rook left/right | Rook moves horizontally | Rook moves after ray fix | Pass |
| MOVE-11 | Queen movement | Move queen along valid file/rank/diagonal | Queen moves correctly | Queen moves | Pass |
| MOVE-12 | King one-square move | Move king one legal square | King moves one square | King moves | Pass |
| MOVE-13 | King into danger | Try moving king onto attacked square | Move rejected | King cannot move into danger | Pass |

---

## 7. Special Rule Tests

| Test ID | Rule | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| SPEC-01 | Kingside castling | Clear `f1` and `g1`, then move `e1 → g1` | King moves to `g1`, rook moves to `f1` | Castling works | Pass |
| SPEC-02 | Queenside castling | Clear `b1`, `c1`, `d1`, then move `e1 → c1` | King moves to `c1`, rook moves to `d1` | Castling works | Pass |
| SPEC-03 | Black castling | Clear black castling path and move `e8 → g8` or `e8 → c8` | Black castles correctly | Castling works | Pass |
| SPEC-04 | Castling blocked | Try castling while pieces are between king and rook | Castling not allowed | Move rejected | Pass |
| SPEC-05 | Castling through check | Try castling through an attacked square | Castling not allowed | Move rejected | Pass |
| SPEC-06 | Castling after king moved | Move king, move back, then try castling | Castling not allowed | Castling right removed | Pass |
| SPEC-07 | Castling after rook moved | Move rook, move back, then try castling | Castling not allowed | Castling right removed | Pass |
| SPEC-08 | En passant | `e2→e4`, `a7→a6`, `e4→e5`, `d7→d5`, `e5→d6` | White pawn captures black pawn en passant | En passant works | Pass |
| SPEC-09 | En passant expires | Make another move before en passant capture | En passant no longer available | Opportunity expires | Pass |
| SPEC-10 | Pawn promotion | Move pawn to final rank | Promotion should be handled or documented | Needs final check | To verify |
| SPEC-11 | Check detection | Put king in check | Engine should prevent illegal king responses | Check behaviour works through king safety validation | Pass |
| SPEC-12 | Checkmate detection | Play/checkmate test position | Game should identify checkmate if supported | Needs final check | To verify |
| SPEC-13 | Stalemate detection | Create stalemate test position | Game should identify stalemate if supported | Needs final check | To verify |

---

## 8. Timer Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TIME-01 | No Timer option | Select No Timer and start | No countdown affects game | Game plays without clock loss | Pass |
| TIME-02 | Timer option applies | Select a timed option and start | White and Black clocks appear | Timers display in side panel | Pass |
| TIME-03 | Clock format | Start timed game | Clock shows `MM:SS:CS` | Timer displays in minute:second:centisecond format | Pass |
| TIME-04 | Current player clock decreases | Start timed game | Clock decreases only for player to move | Active player's timer decreases | Pass |
| TIME-05 | Increment after move | Use increment timer and make a move | Player receives added seconds after moving | Increment applies | Pass |
| TIME-06 | Timer reaches zero | Let a player run out of time | Game ends and opponent wins | End-game screen appears | Pass |
| TIME-07 | Timer stops after game over | Game ends on time | Clocks stop updating | Timer stops | Pass |

---

## 9. Move History and Status Panel Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| HIST-01 | Move appears in history | Make a legal move | Move is added to move history | Move appears | Pass |
| HIST-02 | Multiple moves display | Play several moves | Move list updates without replacing old moves | History displays multiple moves | Pass |
| HIST-03 | Illegal move does not flood history | Attempt illegal moves repeatedly | Move history is not filled with warnings | Warnings are limited/status-based | Pass |
| HIST-04 | Status messages update | Select piece, move piece, attempt illegal move | Status panel updates clearly | Status messages appear | Pass |
| HIST-05 | Side panel remains visible | Play game in resizable window | Timer and move history stay visible | Side panel appears | Pass |

---

## 10. Surrender and End-Game Flow Tests

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| END-01 | Surrender button appears | Start game | Surrender button visible in side panel | Button appears | Pass |
| END-02 | Surrender asks confirmation | Click Surrender once | Confirmation message appears | Confirmation appears | Pass |
| END-03 | Confirm surrender | Click Surrender again | Opponent wins and game over screen appears | Game ends | Pass |
| END-04 | Cancel surrender | Click elsewhere after first surrender click | Confirmation is cancelled | Confirmation clears | Pass |
| END-05 | Game-over winner text | Win on time or surrender | Screen shows White Wins or Black Wins | Winner displayed | Pass |
| END-06 | Rematch button | Click Rematch on game-over screen | New game starts | New game starts | Pass |
| END-07 | Return to menu | Click Return to Main Menu | Lobby screen appears | Menu appears | Pass |
| END-08 | Escape to menu | Press ESC during game | Returns to main menu | ESC returns to menu | Pass |

---

## 11. Regression Tests

These tests were used after changes were made to confirm that earlier features were not broken.

| Test ID | Change Tested | Regression Check | Expected Result | Status |
|---|---|---|---|---|
| REG-01 | Rebrand from Wake to An Chess Engine | Run terminal engine | Program still runs | Pass |
| REG-02 | Pygame GUI added | Run GUI | Board displays | Pass |
| REG-03 | Image assets replaced font symbols | Start GUI | Pieces display correctly | Pass |
| REG-04 | Legal move highlights added | Select piece | Highlight appears | Pass |
| REG-05 | Rook ray fix | Move rook horizontally after clearing path | Rook moves correctly | Pass |
| REG-06 | King safety fix | Try king move into check | Move rejected | Pass |
| REG-07 | Lobby redesign | Start GUI | Menu loads before board | Pass |
| REG-08 | Timer and side panel added | Start timed game | Clocks and history remain visible | Pass |
| REG-09 | Surrender added | Use surrender flow | Game-over screen appears | Pass |
| REG-10 | Removed unnecessary mode option | Open menu | No unused bot/player-vs-player option appears | Pass |

---

## 12. Security and Robustness Tests

Although this is a desktop chess application rather than a web application, defensive programming and robustness were still tested.

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| SEC-01 | Invalid GUI click | Click outside normal game controls | Program should not crash | No crash | Pass |
| SEC-02 | Illegal chess move | Attempt invalid piece movement | Move rejected safely | Move rejected | Pass |
| SEC-03 | Wrong turn selection | Click opponent piece on current turn | Opponent piece cannot be moved | Selection rejected | Pass |
| SEC-04 | Missing image asset check | Temporarily remove one asset and run | Program shows loading error rather than corrupt game state | To be checked if needed | To verify |
| SEC-05 | Window close handling | Close window using X | Program exits cleanly | Program exits | Pass |
| SEC-06 | Menu return handling | Press ESC | Program returns to menu cleanly | ESC works | Pass |

---

## 13. Performance and Usability Testing

| Test ID | Test | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| PERF-01 | GUI load time | Launch GUI | Menu opens quickly | Loads quickly | Pass |
| PERF-02 | Move response time | Click piece and target square | Move updates immediately | Moves update quickly | Pass |
| PERF-03 | Resizable window | Resize window | UI scales and remains readable | Menu scales | Pass |
| PERF-04 | Coordinate readability | View board | Coordinates can be read easily | Coordinates visible | Pass |
| PERF-05 | Highlight readability | Select pieces on light and dark squares | Highlight visible on both colours | Highlight visible | Pass |
| PERF-06 | Move history readability | Play several moves | Move history remains readable | Move history readable | Pass |

---

## 14. Issues Found and Fixes Made

| Issue | Cause | Fix Applied | Status |
|---|---|---|---|
| Unicode chess pieces appeared as boxes | Font did not support chess symbols | Replaced Unicode pieces with PNG image assets | Fixed |
| Piece images looked off-centre | Transparent padding in images | Cropped transparent padding before scaling | Fixed |
| Rooks could not move horizontally from edge files | Incorrect ray boundary logic | Fixed sliding ray boundaries in `bitboard_helpers.py` | Fixed |
| Knight highlights showed illegal squares | Engine checked all pieces of same type together | Legal move preview now checks the selected piece properly | Fixed |
| Kings could move into danger | GUI preview needed king-safety validation | Added king-safety filtering for legal moves | Fixed |
| Menu options went out of frame | Fixed-size menu layout | Added resizable/scalable menu layout | Fixed |
| Timer reached zero without proper end flow | No complete game-over state | Added timer-based game-over screen | Fixed |
| Repeated warning spam | Warning printed every invalid click | Limited repeated warning/status messages | Fixed |
| No surrender flow | Missing game control | Added surrender button and confirmation | Fixed |
| Unnecessary player-vs-player option | No bot option existed | Removed unused mode option | Fixed |

---

## 15. Evidence to Include in Submission

Add screenshots of the following to the documentation or presentation:

1. Lobby/menu screen with logo and timer options
2. Game screen with board, side panel, timers and move history
3. Legal move highlighting after selecting a piece
4. Castling highlight or successful castling move
5. En passant test sequence or final en passant position
6. Timer game-over screen
7. Surrender confirmation and end-game screen
8. GitHub commit history showing modifications over time
9. `requirements.txt` showing Pygame dependency
10. Source acknowledgement in `README.md`

---

## 16. Known Limitations and Future Improvements

The current project is a strong graphical version of the original terminal chess engine, but future improvements could include:

- Stockfish integration for computer opponent difficulty levels
- More advanced checkmate and stalemate end-game messages if not fully detected in all positions
- Pawn promotion selection menu if promotion is not already fully interactive
- Sound effects for moves, captures and check
- Save/load game feature
- Online multiplayer
- Opening book support
- More formal automated unit tests for all chess rules

---

## 17. Testing Summary

Testing shows that An Chess Engine has been successfully modified from a terminal-only chess engine into a graphical chess application. The GUI supports clickable piece movement, legal move highlighting, core chess rules, castling, en passant, timers, move history, surrender, game-over screens, rematch and menu navigation.

The most important fixes were the sliding-piece ray correction, selected-piece legal move validation, king safety validation and improved GUI flow. These changes make the application more usable, easier to demonstrate and more appropriate for a Software Engineering major project.
