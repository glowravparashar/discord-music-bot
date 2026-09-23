# Syre

A simple, self-hosted Discord music bot built with Python, `discord.py`, and `yt-dlp`.

## Why I built it
Most public music bots are either paid, bloated, or frequently offline. I built Syre to have a clean, self-hosted alternative for streaming music without restrictions, and to practice building a modular bot architecture using Cogs and Discord UI components.

## Features
- Direct audio streaming via `yt-dlp` and `FFmpeg`
- Interactive button controls (Play/Pause, Skip, Stop)
- Modular codebase structure (`cogs`, `ui`, `utils`)

## Structure
```text
discord-music-bot/
├── cogs/            # Command modules (music, general)
├── ui/              # Interactive button views
├── utils/           # Audio extraction logic
├── .env             # Bot token and prefix configuration
├── config.py        # Environment variables loader
├── main.py          # Entry point
└── README.md



>Install :

Bash
pip install discord.py yt-dlp python-dotenv PyNaCl
Create .env in root:


>Create .env in root:

Code snippet
DISCORD_TOKEN=your_token_here
COMMAND_PREFIX=!

>Run:

Bash
python main.py


>To push this:

```bash
git add README.md
git commit -m "update readme with quickstart"
git push origin main
