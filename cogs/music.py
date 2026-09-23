import discord
from discord.ext import commands
from utils.audio import YTDLSource
from ui.views import PlayerControlView

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send("You must be connected to a voice channel!")

        vc = ctx.voice_client or await ctx.author.voice.channel.connect()

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
            except Exception as e:
                return await ctx.send(f"An error occurred while fetching the track: `{e}`")

        queue = self.get_queue(ctx.guild.id)

        if vc.is_playing() or vc.is_paused():
            queue.append(player)
            await ctx.send(f"Added to queue: **{player.title}**")
        else:
            vc.play(player, after=lambda e: self.play_next(ctx))
            view = PlayerControlView(self, ctx)
            await ctx.send(f"Now playing: **{player.title}**", view=view)

    def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if len(queue) > 0:
            next_player = queue.pop(0)
            ctx.voice_client.play(next_player, after=lambda e: self.play_next(ctx))
            self.bot.loop.create_task(
                ctx.send(f"Now playing: **{next_player.title}**", view=PlayerControlView(self, ctx))
            )

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            ctx.voice_client.stop()
            await ctx.send("Skipped current song!")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(name="stop", aliases=["leave"])
    async def stop(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()

        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))