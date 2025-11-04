# GEMINI.md

## Project Overview

This project is a 2D RPG platformer game developed in Python using the Pygame library. The game features classic platformer mechanics such as jumping, moving, and collecting items, along with RPG elements like a health system and combat. Levels are designed using the Tiled Map Editor and loaded into the game.

**Key Technologies:**
- Python
- Pygame
- PyTMX

## Building and Running

### Dependencies

The project's dependencies are listed in `requirements.txt`. You can install them using pip:

```bash
pip install -r requirements.txt
```

### Running the Game

To run the game, execute the `main.py` script:

```bash
python main.py
```

### Running Tests

The project uses a combination of the `unittest` framework and `pytest`.

To run all tests, you can use the `run_tests.py` script:

```bash
python run_tests.py
```

Alternatively, you can run individual test files directly:

```bash
python tests/test_player.py
```

The CI environment, as defined in `.github/workflows/test.yml`, also runs tests by executing the test files directly.

## Development Conventions

### Code Style

The codebase is structured in an object-oriented manner, with classes for different game components like `Player`, `Level`, `Enemy`, etc. The code is well-commented, especially in complex sections.

### Level Creation

Levels are created using the Tiled Map Editor. The resulting `.tmx` files are then parsed by the game to generate the levels. The `game/levels/level1.py` file contains hardcoded data that appears to be an export from a TMX file, which is then used to load the level.

### Testing

Tests are located in the `tests/` directory. The project uses a mix of `unittest` and `pytest`. Test files are named with a `test_` prefix (e.g., `test_player.py`). The tests cover different aspects of the game, including unit tests for individual components and integration tests.
