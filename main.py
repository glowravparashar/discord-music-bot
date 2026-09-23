import os
import asyncio
import discord
from discord.ext import commands
from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    # Calculates total members across all servers the bot is in
    total_members = sum(g.member_count for g in bot.guilds)
    
    # Sets the Discord status to "Watching r/music | X servers & Y redditors"
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"r/music | {len(bot.guilds)} servers & {total_members} redditors"
        )
    )
    
    print(f"✓ Syre is online and moderation-free.")
    print(f"✓ Connected as {bot.user.name} ({bot.user.id})")
    print("------------------------------------------")

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        if not TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable is missing from .env")
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())