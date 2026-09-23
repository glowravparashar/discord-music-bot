import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Responds with the bot's current latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: `{latency}ms`")

    @commands.command(name="info")
    async def info(self, ctx):
        """Displays information about the bot."""
        embed = discord.Embed(
            title="Syre Music Bot",
            description="A modular Discord music bot built with discord.py, yt-dlp, and FFmpeg.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Prefix", value="`!`", inline=True)
        embed.add_field(name="Status", value="Online & Ready", inline=True)
        embed.set_footer(text="Type !help to see available commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))