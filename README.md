# MOM-BIRD

A Flappy Bird-style game built with Python and Pygame. Navigate the bird through pipes — touch a pipe and face the consequences.

## About

MOM-BIRD is a challenging arcade game where you control a bird navigating through an endless series of pipes. Touch a pipe and you'll trigger a jumpscare featuring a custom image and sound. The game features smooth bird physics, animated wings, scrolling ground, and a distinctive jumpscare mechanic.

**Made by zenx.pc**

## Features

- Flappy Bird-style gameplay with smooth physics
- Animated bird with wing flapping and tilt based on velocity
- Scrolling ground with seamless tiling
- Procedurally generated pipes with consistent gaps
- Custom jumpscare image and sound support (with procedural fallback)
- Score tracking with high score persistence
- Clean game over and restart flow

## Requirements

- Python 3.8+
- Pygame 2.0+

Install dependencies:

```bash
pip install pygame
```

## Installation

```bash
git clone https://github.com/zenx-pc/MOM-BIRD.git
cd MOM-BIRD
pip install pygame
```

## Usage

Run the game:

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `SPACE` / `UP` / `Mouse Click` | Flap / Jump |
| `R` | Restart after game over |
| `ESC` / `Q` / Close Window | Quit |

### Custom Assets

The game supports custom jumpscare assets. Edit these paths in `main.py`:

```python
MOM_IMAGE_PATH = "assets/mom.png"        # Jumpscare image (480x640 recommended)
SCARE_SOUND_PATH = "assets/scare.mp3"    # Jumpscare sound effect
```

If assets are not found, procedural fallbacks are used automatically.

### Asset Requirements

| Asset | Recommended Size | Format |
|-------|------------------|--------|
| mom.png | 480 × 640 px | PNG (with transparency) |
| scare.mp3 | — | MP3 / OGG / WAV |

Place assets in the `assets/` directory or update the paths in `main.py`.

## Project Structure

```
MOM-BIRD/
├── main.py          # Main game file
├── buildozer.spec   # Buildozer configuration for Android builds
├── assets/
│   ├── mom.png      # Custom jumpscare image (optional)
│   └── scare.mp3    # Custom jumpscare sound (optional)
└── README.md
```

## Building for Android (Optional)

This project includes a `buildozer.spec` configuration for building an Android APK using Buildozer.

```bash
# Install buildozer (Linux/WSL recommended)
pip install buildozer

# Build debug APK
buildozer -v android debug
```

Note: Building for Android requires a Linux environment (WSL on Windows works). The game uses Pygame which is supported via the python-for-android toolchain.

## Configuration

Key game constants in `main.py` (lines 10-18):

```python
W, H = 480, 640          # Window dimensions
GRAVITY = 0.5            # Gravity strength
FLAP_STRENGTH = -9       # Jump velocity
PIPE_GAP = 160           # Gap between pipes
PIPE_SPEED = 3           # Pipe scroll speed
PIPE_SPAWN = 1500        # Pipe spawn interval (ms)
```

Adjust these values to tune difficulty.

## License

This project is open source. Feel free to modify and distribute.

## Author

**zenx.pc**