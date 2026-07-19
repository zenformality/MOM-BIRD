# Touch the Pipe If You Hate Your Mom

A Flappy Bird-style game with a jumpscare twist — hit a pipe and face your mom.

## About

A Flappy Bird clone built with Python and Pygame. Navigate the bird through pipes, but be careful — touching a pipe triggers a jumpscare featuring your mom.

## Features

- Classic Flappy Bird gameplay
- Custom jumpscare image and sound (replace with your own assets)
- Placeholder jumpscare drawing if assets are missing
- Score tracking
- Menu, gameplay, jumpscare, and game over states

## Requirements

- Python 3.8+
- pygame

Install dependencies:

```bash
pip install pygame
```

## Assets

The game expects two asset files. Update the paths in `main.py` (lines 17-18) to point to your files:

```python
MOM_IMAGE_PATH   = "path/to/mom.png"      # Jumpscare image (recommended 480x640)
SCARE_SOUND_PATH = "path/to/scare.mp3"    # Jumpscare sound effect
```

Placeholders are used if files are not found.

## Controls

| Action | Key |
|--------|-----|
| Flap / Start / Restart | Space / Up Arrow / Left Click |
| Quit | Escape |

## Run

```bash
python main.py
```
OR 

```bash
py main.py 
```
## Game States

- **Menu** — Press Space or click to start
- **Playing** — Flap through pipes, avoid hitting them
- **Jumpscare** — Triggered on collision; plays sound and shows image
- **Dead** — Shows final score; press Space or R to restart

## Controls Summary

| State | Action |
|-------|--------|
| Menu | Space / Click → Start |
| Playing | Space / Up / Click → Flap |
| Dead | Space / R → Restart |
| Any | Escape → Quit |

## Configuration

Constants at the top of `main.py` control gameplay:

| Constant | Default | Description |
|----------|---------|-------------|
| `W, H` | 480, 640 | Window dimensions |
| `GRAVITY` | 0.5 | Gravity per frame |
| `JUMP_VEL` | -9 | Jump velocity |
| `PIPE_VEL` | 3 | Pipe scroll speed |
| `PIPE_GAP` | 190 | Gap between pipes |
| `PIPE_FREQ` | 90 | Frames between pipe spawns |

## Assets Location

Place your assets in the `assets/` folder and update the paths in `main.py`:

```
MOM-BIRD/
├── assets/
│   ├── mom.png      # Jumpscare image
│   └── scare.mp3    # Jumpscare sound
├── main.py
└── README.md
```

## License

MIT License

---

Made by zenx.pc
