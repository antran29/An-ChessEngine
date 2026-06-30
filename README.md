# An Chess Engine

<p align="center">
  <img src="AChess.png" alt="An Chess Engine Logo" width="220">
</p>

## Project Overview

**An Chess Engine** is a modified educational chess engine created for my HSC Software Engineering major project. The project began as a terminal-based chess engine and was developed into a more user-friendly graphical chess application using Python and Pygame.

The purpose of this project is to make chess easier to interact with visually by allowing players to use a graphical board instead of typing moves into a terminal. The final version includes a lobby screen, clickable chess board, legal move highlighting, timers, move history, surrender option and end-game flow.

## Student Information

- **Student:** Ayden James Tran  
- **Course:** HSC Software Engineering  
- **Project Type:** Advanced App / Chess Engine  
- **Repository:** `An-ChessEngine`  

## Source Acknowledgement

This project is based on the open-source **Wake chess engine** by **Wes Doyle**. The original engine was used as a foundation for learning and development.

For this major project, I modified and extended the original terminal-based engine by adding a graphical interface, custom branding, image-based chess pieces, menu screens, click-based movement, legal move highlighting, timer functionality, move history, surrender handling and documentation.

The original source code has been acknowledged to meet academic integrity requirements.

## Main Features

- Graphical chess board built with **Pygame**
- Custom chess piece images
- Custom project logo and branding
- Lobby / main menu screen
- Click-based piece selection and movement
- Legal move highlighting
- Current-player turn validation
- Castling support
- En passant support
- Board coordinate labels
- In-game side panel
- Player timers
- Move history display
- Surrender button with confirmation
- Timer-based game-over screen
- Rematch option
- Return to main menu option
- Terminal version still available for basic UCI-style move input

## Technologies Used

- **Python 3.12** - main programming language
- **Pygame** - graphical user interface
- **NumPy** - bitboard and engine calculations
- **Pytest** - testing support
- **Visual Studio Code** - development environment
- **GitHub** - version control and project management

## Project Structure

```text
An-ChessEngine/
│
├── anchessengine/
│   ├── gui.py
│   ├── game.py
│   ├── position.py
│   ├── move.py
│   ├── board.py
│   ├── bitboard_helpers.py
│   └── ...
│
├── assets/
│   └── pieces/
│       ├── Chess_klt60.png
│       ├── Chess_kdt60.png
│       └── ...
│
├── tests/
│
├── AChess.png
├── README.md
├── TESTING.md
├── requirements.txt
├── setup.py
└── LICENSE
```

## Prerequisites

Before running the project, make sure you have:

1. **Python 3.12 installed**  
   Python 3.12 is recommended because the required packages work reliably with it.

2. **Visual Studio Code installed**  
   This project is designed to be opened and run through VS Code.

3. **Git installed**  
   Git is recommended if you want to clone the repository and push changes to GitHub.

## How to Download the Program as a ZIP

1. Go to the GitHub repository.
2. Click the green **Code** button.
3. Click **Download ZIP**.
4. Once downloaded, right click the ZIP file.
5. Select **Extract All**.
6. Open the extracted folder.

Make sure you open the main project folder that contains:

```text
README.md
requirements.txt
anchessengine/
assets/
```

## How to Open the Project in Visual Studio Code

1. Open **Visual Studio Code**.
2. Click **File**.
3. Click **Open Folder**.
4. Select the extracted `An-ChessEngine` folder.
5. Click **Select Folder**.

You should now see folders such as:

```text
anchessengine
assets
tests
```

and files such as:

```text
README.md
requirements.txt
TESTING.md
```

## Setting Up the Virtual Environment

Open the terminal in VS Code:

```text
Terminal → New Terminal
```

Create a virtual environment using Python 3.12:

```powershell
py -3.12 -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then press:

```text
Y
```

and try activating again:

```powershell
.\.venv\Scripts\Activate.ps1
```

You will know it worked when the terminal starts with:

```powershell
(.venv)
```

## Installing Required Packages

Once the virtual environment is active, run:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs:

```text
numpy
pygame
pytest
```

## How to Run the Graphical Chess Application

From the main project folder, run:

```powershell
python -m anchessengine.gui
```

This will open the graphical chess application.

## How to Use the GUI

1. Start the program.
2. Use the main menu to choose your setup options.
3. Click **Start Game**.
4. Click a piece to select it.
5. Legal moves will be highlighted.
6. Click a highlighted square to move the piece.
7. Use the side panel to view:
   - timers
   - move history
   - game status
8. Use **Surrender** if you want to resign.
9. At the end of the game, choose:
   - **Rematch**
   - **Return to Main Menu**

## How to Run the Terminal Version

The original terminal-style version can still be run using:

```powershell
python -m anchessengine.game
```

Moves are entered using UCI-style notation, such as:

```text
e2e4
g1f3
```

To quit the terminal version, type:

```text
quit
```

## How to Run Tests

To run the existing test files, use:

```powershell
python -m pytest
```

Testing evidence and manual test cases are documented in:

```text
TESTING.md
```

## Example Test Sequence

A basic move sequence for testing normal movement:

```text
e2 → e4
e7 → e5
g1 → f3
b8 → c6
```

A castling test sequence:

```text
e2 → e4
e7 → e5
g1 → f3
b8 → c6
f1 → c4
g8 → f6
e1 → g1
```

An en passant test sequence:

```text
e2 → e4
a7 → a6
e4 → e5
d7 → d5
e5 → d6
```

## Major Modifications Made

The original engine was mainly terminal-based. My major modifications include:

- rebranding the project as **An Chess Engine**
- adding custom logo and visual identity
- creating a Pygame GUI
- replacing text-based board display with a graphical board
- adding chess piece image assets
- adding click-based movement
- adding legal move highlighting
- improving GUI usability through board coordinates
- adding a menu/lobby screen
- adding timer options and clock display
- adding move history
- adding surrender confirmation
- adding game-over screen
- adding rematch and return-to-menu flow
- fixing movement validation issues for GUI use
- documenting testing in `TESTING.md`

## Known Limitations

This project is still an educational chess engine and does not include every advanced feature found in professional chess software.

Current limitations include:

- no Stockfish computer opponent
- no online multiplayer
- no cloud deployment
- no opening book
- no advanced AI difficulty system
- no saved game database

## Future Improvements

Future versions could include:

- Stockfish integration
- AI difficulty levels
- online multiplayer
- saved games
- player accounts
- match history
- puzzle mode
- analysis board
- improved animations
- sound effects
- stronger checkmate and draw detection UI

## Academic Integrity Statement

This project acknowledges that it is based on an existing open-source chess engine. The original source was used as a foundation, and the modifications made for this project are documented through GitHub commits, testing files, screenshots and project documentation.

The work submitted for this major project focuses on the planning, modification, interface development, testing, documentation and presentation of the software solution.

## Licence

This project is based on the Wake chess engine and follows the licence requirements of the original project. Any reused source code has been acknowledged.
