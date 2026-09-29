# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
cd babel_game
python main.py              # Main game
```

The game requires Pyxel to be installed: `pip install pyxel`

## Architecture Overview

This is a post-war Japan reconstruction simulation game (1945-1970) built with Pyxel. The codebase uses a modular, event-driven architecture with data-driven design.

### Project Structure

```
babel_game/
├── main.py                 # Entry point - initializes GameEngine and Pyxel
├── config/                 # Configuration and game balance
│   ├── game_config.py      # Screen size, grid settings, colors
│   ├── balance_config.py   # Game balance and difficulty parameters
│   └── sprite_mapping.py   # Sprite name to asset file mappings
├── core/                   # Core systems
│   ├── game_engine.py      # Main game loop, system coordination
│   ├── event_manager.py    # Event-driven communication
│   └── time_manager.py     # Game time (1945-1970 progression)
├── systems/                # Game feature systems (20 systems)
│   ├── grid_system.py         # Isometric grid and coordinate conversion
│   ├── cursor_system.py       # Mouse cursor and grid selection
│   ├── building_manager.py    # Building placement and unlock system
│   ├── population_manager.py  # Population growth and citizens
│   ├── economy_manager.py     # Money, resources, trade
│   ├── technology_manager.py  # Tech tree and unlock progression
│   ├── event_system.py        # Random events (disasters, economic boom)
│   ├── ui_manager.py          # UI rendering and input handling
│   ├── asset_manager.py       # Sprite and asset loading
│   ├── animation_manager.py   # Sprite animation system
│   ├── font_manager.py        # Japanese BDF font rendering
│   ├── difficulty_manager.py  # Easy/Normal/Hard modes
│   ├── save_manager.py        # Save/load game state
│   ├── terrain_generator.py   # Procedural terrain generation
│   ├── developer_mode.py      # Developer tools and god mode
│   └── game_completion.py     # End game scoring
├── models/                 # Data models (Building, Citizen, Tile, etc.)
├── assets/                 # Game assets (PNG sprites, atlas files)
└── data/                   # JSON game data
    └── buildings.json      # Building definitions and stats
```

### Core Architecture

**GameEngine**: Main game loop that coordinates all systems
- Initializes all systems in the correct order
- Manages the update/draw cycle
- Handles event routing between systems
- Integrates with developer mode and save system

**Event-Driven Communication**: Systems communicate through `event_manager`
- Loose coupling between systems
- Event types: `year_changed`, `build_requested`, `game_completed`, etc.
- Subscribe/publish pattern for extensibility

**Time System**: `TimeManager` handles game progression
- Game years: 1945-1970 (25 years)
- Month/day progression
- Speed control (pause, 0.5x, 1x, 2x, 5x)
- Triggers year-based events and unlocks

### Key Systems

**GridSystem**: Isometric grid and coordinate conversion
- 32x32 grid cells (1024 total)
- Isometric projection with `grid_to_screen()` and `screen_to_grid()`
- Multi-layer tiles (terrain + buildings)
- Viewport culling for performance
- Coordinate conversion with pixel-perfect accuracy

**BuildingManager**: Building placement and unlock system
- Loads building definitions from `data/buildings.json`
- Year-based unlocks (1945-1970)
- Population prerequisites
- Building dependency chains
- 22+ historical buildings across 7 categories

**EconomyManager**: Economic simulation
- Japanese Yen (¥) currency
- Resources: money, rice, iron, wood, coal, electricity
- Monthly income/expense calculation
- Trade system
- Difficulty-based balance modifiers

**UIManager**: User interface
- Japanese text rendering via BDF font
- City info panel (bottom-left)
- Building palette (bottom-right, 2-column layout)
- 32x32 building icons
- Responsive to mouse and keyboard input

**TerrainGenerator**: Procedural terrain
- Coastline generation with cellular automata
- Multiple terrain types (grass, water, sand, mountains, etc.)
- Auto-generation on new game
- Manual terrain tools in developer mode

**SaveManager**: Save/load system
- JSON-based save format
- Saves entire game state (grid, buildings, economy, time)
- Auto-save and manual save slots
- Save file validation

**DeveloperMode**: Development tools
- God mode (infinite money, all buildings unlocked)
- Time freeze
- Terrain generation tools
- Console commands
- Debug information overlay

## Game Design Reference

### Post-War Japan Theme (1945-1970)

**Historical Periods**:
- **1945-1950**: Immediate post-war reconstruction (barracks, basic infrastructure)
- **1950-1955**: Korean War boom (light industry, economic growth)
- **1955-1970**: High Growth Period (heavy industry, high-rise buildings, nuclear power)

**Building Categories**:
- **Residential**: バラック住宅 → 木造平屋 → 市営団地 → 高層団地
- **Commercial**: 個人商店 → 商店街 → 百貨店
- **Industrial**: 小工場 → 自動車工場
- **Civic**: 派出所, 消防分団, 小学校, 総合病院
- **Infrastructure**: 道路, 国鉄駅, 火力発電所
- **Recreation**: 銭湯, 映画館
- **Special**: 原子力発電所, テレビ塔, 空港

**Economic System**:
- Currency: Japanese Yen (¥)
- Building costs: ¥10 (roads) to ¥8000 (airport)
- Income from: taxes, commercial activity, industry
- Expenses: building maintenance, resource imports

### Controls

**Camera**:
- W/A/S/D or Arrow keys: Move camera
- Z/X: Zoom in/out
- Mouse: Move cursor

**Building**:
- Left click: Place building
- Right click: Remove building
- 1-7 keys: Select building category
- Click palette: Select specific building

**UI**:
- Tab: Toggle info panel
- P: Toggle build palette
- G: Toggle grid display
- Space: Pause/resume
- Shift+1/2/3/4: Time speed (0.5x/1x/2x/5x)
- F1: Debug info
- F5/F6/F7: Difficulty (Easy/Normal/Hard)
- F2: Help screen
- Q: Quit

**Developer Mode** (when enabled):
- F8: Toggle developer console
- F9: Quick save
- F10: Quick load
- F11: Toggle god mode
- F12: Generate new terrain

## Development Notes

### Adding New Buildings

1. Add building definition to `data/buildings.json`
2. Add sprite assets to `babel_game/assets/`
3. Update sprite mapping in `config/sprite_mapping.py`
4. Implement any special behavior in `systems/building_manager.py`

### Adding New Systems

1. Create system class in `babel_game/systems/`
2. Initialize in `core/game_engine.py`
3. Register event listeners in `_register_event_listeners()`
4. Update in `GameEngine.update()` or `draw()`

### Asset Guidelines

- Sprites: PNG with #ff00ff (magenta) for transparency
- Icons: 32x32 PNG for UI palette
- Animations: Multi-frame sprites (horizontal layout)
- Font: Japanese BDF font (umplus_j10r.bdf)

### Performance Considerations

- Grid size: 32x32 for optimal performance
- Viewport culling implemented but may need optimization
- Target FPS: 60
- Sprite atlas used for efficient rendering

### Configuration

**Screen**: 800x600 (configurable in `GameConfig`)
**Grid**: 32x32 cells, 32px cell size
**Colors**: Pyxel palette (see `GameConfig.COLOR_*`)
**Difficulty**: Affects starting money, costs, and income (see `BalanceConfig`)

### Known Issues

- Viewport culling algorithm could be optimized
- Cursor precision decreases at cell boundaries
- Some edge cases in terrain generation may need refinement

## Recent Development Progress

As of the latest commits, the following systems have been implemented:
- ✅ Complete modular architecture with event system
- ✅ Terrain generation with procedural coastlines
- ✅ Save/load system with JSON persistence
- ✅ Developer mode with god mode and console
- ✅ Japanese UI with BDF font rendering
- ✅ Building unlock system based on year/population
- ✅ Economy system with multiple resources
- ✅ Population management and happiness
- ✅ Technology tree and progression

See `README.md`, `GAME_DESIGN.md`, and `docs/` for more detailed design documents.
