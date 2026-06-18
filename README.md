Syre Music Bot 

Syre is a minimalist and high-performance Discord music bot designed for a seamless listening experience. Built with discord.py and yt-dlp, it offers an intuitive playback interface, custom audio filters, and intelligent resource management, ensuring your music never stops and your server stays organized.
The idea of Syre is pretty simple actually, I wanted to create something that felt both powerful and effortless. I personally love music, so I was looking for a music bot that could play some tracks for me.
This project taught me a lot about building persistant systems and handling real-time audio streams. It was fun making something that intrigues me, I'm currently conceptualizing a new framework designed for the humanities and philosophical discussions. Let's see how it stands out, very excited for it. 





Key Features ---

> Interactive UI: Persistent button deck for Play/Pause, Skip, Stop, and Queue management.

> Audio FX: Toggle Bassboost and Nightcore filters on the fly.

> Smart Resource Management: Automatically disconnects from voice channels when idle to save bandwidth and energy.

> Isolation: Queue management is unique to each server.





Commands ---

> !play <query>: Search for a song or paste a URL to start playing.

> !pause: Pause the current track.

> !resume: Resume playback.

> !skip: Skip the current song in the queue.

> !stop: Stop the music and clear the queue.

> !filter <name>: Apply audio effects like bassboost or nightcore.





Build with ---

> Language: Python

> Library: discord.py (for the Discord API interface)

> Audio Handling: yt-dlp (for media extraction) and FFmpeg (for audio processing)

> Configuration: python-dotenv (for secure environment variable management)
