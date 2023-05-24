# TombstoneTunnels
[![Windows build](https://github.com/Odyssey-Games/TombstoneTunnels/actions/workflows/build-windows.yml/badge.svg?branch=main)](https://github.com/Odyssey-Games/TombstoneTunnels/actions/workflows/build-windows.yml)
[![Linux build](https://github.com/Odyssey-Games/TombstoneTunnels/actions/workflows/build-linux.yml/badge.svg)](https://github.com/Odyssey-Games/TombstoneTunnels/actions/workflows/build-linux.yml)

## Ideas

- top-down
- dungeon crawler
- rogue-like
- multiplayer
- co-op -> one team that plays together / maybe also singleplayer -> difficulty scales with player count
- un-dead mobs (skeletons, zombies)
- randomly generated levels
- close-range/melee combat

## Testing

<details>

<summary>Setup virtual environment: (recommended):</summary>

1. Create virtual environment: `python -m venv env`
2. Activate virtual environment: `.\env\Scripts\activate` (Windows) or `source env/bin/activate` (Unix)

</details>

1. Install dependencies: `pip install -r requirements.txt`
2. Run server: `python server/src/server.py`
3. Run client: `python client/src/client.py`

Running the dedicated server via docker is recommended: `docker run -d -p 5857:5857/udp krxwallo/tt-server`