# Enemy Respawn After Player Death - Feature Documentation

## Overview
This feature ensures that enemies respawn when the player dies and respawns. Previously, killed enemies would remain dead even after player respawn, making subsequent attempts easier.

## Changes Made

### 1. Player Class (`game/player.py`)

#### Added respawn callback support:
- **Line 93-94**: Added `self.on_respawn` callback attribute that can be set by the level
- **Line 578-583**: Modified `respawn()` method to call the `on_respawn` callback if it's set

```python
# Callback, который может быть установлен уровнем для обработки респавна игрока
self.on_respawn = None
```

```python
# Вызываем callback респавна, если он установлен (для возрождения врагов и т.д.)
if callable(self.on_respawn):
    try:
        self.on_respawn()
    except Exception as e:
        print(f"[Player] on_respawn callback failed: {e}")
```

### 2. Level Class (`game/levels/level1.py`)

#### Added enemy tracking and respawn system:
- **Line 48-49**: Added `self.initial_enemy_data = []` to store initial enemy spawn data
- **Line 365**: Store the initial enemy data when loading objects from XML
- **Line 87-88**: Set the `on_respawn` callback in `set_player()` method
- **Line 467-526**: Added `respawn_killed_enemies()` method that:
  - Counts current alive enemies by type
  - Counts initial enemies by type
  - Creates new enemy instances for any that are missing
  - Properly initializes their sprites and adds them to the enemy group

```python
# Store initial enemy spawn data
self.initial_enemy_data = enemies_data

# Set callback
if hasattr(self.player, "on_respawn"):
    self.player.on_respawn = self.respawn_killed_enemies
```

### 3. Tests (`tests/test_enemy_respawn.py`)

Added comprehensive unit tests:
- `test_player_has_respawn_callback`: Verifies player has the callback attribute
- `test_player_respawn_calls_callback`: Verifies callback is called on respawn
- `test_player_respawn_without_callback`: Verifies respawn works without callback

### 4. Test Runner (`run_tests.py`)

- **Line 21**: Added `test_enemy_respawn` to the test files list

## How It Works

1. **Level Initialization**: When a level is created, it stores the initial enemy spawn data in `initial_enemy_data`
2. **Player Setup**: When the player is set in the level, the level registers its `respawn_killed_enemies` method as the player's `on_respawn` callback
3. **Enemy Death**: When enemies are killed during gameplay, they are removed from the `enemies` sprite group
4. **Player Death**: When the player dies and the respawn timer expires, `player.respawn()` is called
5. **Enemy Respawn**: The player's respawn method triggers the `on_respawn` callback, which:
   - Compares current enemy count vs initial enemy count by type
   - Creates new instances of missing enemies at their original positions
   - Adds them back to the level's `enemies` group

## Testing

Run the test suite to verify the feature:
```bash
python run_tests.py
```

All tests should pass, including the 3 new enemy respawn tests.

## Game Behavior

**Before this change:**
- Kill enemy → Player dies → Player respawns → Enemy stays dead

**After this change:**
- Kill enemy → Player dies → Player respawns → Enemy respawns at original position
