# SpriteForge

A lightweight, locally-hosted web app for packing game sprites into optimized sprite sheets. Built with Flask and Pillow — no cloud required, no data leaves your machine.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask)](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask)
[![License](https://img.shields.io/badge/License-MIT-green)](https://img.shields.io/badge/License-MIT-green)

---

## Features

| Feature | What it does |
|---|---|
| **Sprite Packing** | Upload multiple images and pack them into a single optimized sprite sheet PNG |
| **Shelf Algorithm** | Bin-packs sprites using a shelf/row algorithm — sorts by height, fills left-to-right, wraps to a new shelf automatically |
| **Power-of-2 Sheets** | Sheet width is always the smallest power of 2 that fits (512, 1024, 2048, …) — GPU-friendly |
| **Frame Data Export** | Downloads a JSON file with every frame's `name`, `x`, `y`, `w`, and `h` — ready to plug into your game engine |
| **Sort Modes** | Sort sprites by size (height descending) or alphabetically by filename before packing |
| **Padding Control** | Per-sprite padding from 0–16 px to prevent texture bleeding |

---

## Requirements

### Software

| Requirement | Version | Notes |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.11+ | Required |

### Python packages

All listed in `requirements.txt`:

```
flask>=3.0.0
Pillow
flask-limiter
gunicorn
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/CMgameplays/SpriteForge.git
cd SpriteForge
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Running locally

```bash
python spriteforge.py
```

The server starts on `http://127.0.0.1:5000` and opens in your browser automatically.

---

## Project structure

```
spriteforge/
├── spriteforge.py       # Flask app — all routes and packing logic
├── requirements.txt     # Python dependencies
├── Procfile             # Gunicorn entry point (for deployment)
├── templates/
│   └── index.html       # Single-page UI (HTML + CSS + JS)
└── LICENSE
```

---

## API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Main UI page |
| `POST` | `/api/pack` | Pack uploaded sprites into a sheet — returns base64 PNG + frame JSON |

### `POST /api/pack`

**Form fields:**

| Field | Type | Description |
|---|---|---|
| `images[]` | File (multiple) | Image files to pack |
| `padding` | Integer (0–16) | Per-sprite padding in pixels (default: `2`) |
| `sort` | String | Sort mode — `size` (default) or `name` |

**Response:**

```json
{
  "sheet_png": "<base64-encoded PNG>",
  "sheet_w": 1024,
  "sheet_h": 512,
  "frames": [
    { "name": "player_idle.png", "x": 2, "y": 2, "w": 64, "h": 64 },
    { "name": "player_run.png",  "x": 68, "y": 2, "w": 64, "h": 64 }
  ]
}
```

---

## Deployment

The app is production-ready with Gunicorn. It can be deployed to any WSGI-compatible host.

**Render / Railway / Fly.io:**

The `Procfile` is already configured:

```
web: gunicorn spriteforge:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
```

Just connect your GitHub repo and deploy — no extra configuration needed.

---

## License

MIT — see [LICENSE](LICENSE) for details.

© CMG Forge
