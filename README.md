# Sorcery - A Pygame Remake

This project is a Python-based remake of the classic adventure game "Sorcery," originally released for the Amstrad CPC. The aim is to recreate the look, feel, and gameplay of the original, leveraging the Pygame library for development.

A significant portion of the foundational code structure, game logic, and iterative refinements in this project have been developed with the assistance of an AI language model (Gemini).

## Current Status

The game is currently in active development. Key features implemented so far include:

* **Authentic Screen Layout:** The game window is structured to mimic the original Amstrad CPC display, with a dedicated game area and a bottom information panel.
* **Scaled Graphics:** Utilizes a global scaling factor to render graphics at a comfortable size while maintaining the original game's base resolution and aspect ratio (320x144 game area, 320x56 info panel, scaled up).
* **Player Character:**
    * Wizard sprite implemented with animations (idle, walk left/right).
    * Flight-based movement (up, down, left, right) controlled by arrow keys.
    * Gravity effect when not actively flying upwards.
* **Platform Collision:** Solid platforms that the player character collides with.
* **Tile-Based Level Structure:** Platforms are defined and placed based on a tile grid, adhering to the original game's 40x18 tile layout for the game area.
* **Basic Information Panel:** Displays placeholder game information (location, inventory, energy) at the bottom of the screen.

## Technologies Used

* **Python 3.x**
* **Pygame:** The core library used for game development (graphics, input, sound, etc.).

## How to Run

1.  **Ensure Python and Pygame are installed:**
    * Python can be downloaded from [python.org](https://www.python.org/).
    * Pygame can be installed via pip: `pip install pygame`
2.  **Download the Game Files:**
    * Clone this repository or download the source code.
3.  **Asset Placement:**
    * Make sure the spritesheet (`Amstrad CPC - Sorcery - Characters.png` or your specified filename) is placed in an `assets/images/` subfolder relative to the main game scripts.
    * If you are using a custom font, place it in an `assets/fonts/` subfolder and update `settings.py` accordingly.
4.  **Navigate to the Project Directory:**
    * Open a terminal or command prompt and change to the directory where you've saved the game files (e.g., where `main.py` is located).
5.  **Run the Game:**
    * Execute the main script: `python main.py`

## Controls

* **Arrow Keys:**
    * **Left/Right:** Move the wizard horizontally.
    * **Up/Down:** Make the wizard fly vertically.
* **Escape Key (ESC):** Quit the game.

## Future Goals (Examples)

* Implement all 40 original game rooms.
* Add enemies with basic AI and combat mechanics.
* Incorporate item collection and inventory system.
* Recreate the "time left" book mechanic in the info panel.
* Add sound effects and music.
* Implement game state management (start screen, game over, saving/loading).

## Acknowledgements

* **Original Game:** "Sorcery" by Virgin Games on the Amstrad CPC.
* **AI Assistance:** This project has been significantly aided by an AI language model (Gemini from Google) for code generation, debugging, and architectural suggestions.
* **[Optional]** Any other resources, tutorials, or individuals you'd like to thank.

---

Feel free to copy, paste, and modify this for your `README.md` file!
