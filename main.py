import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True 

bot = commands.Bot(command_prefix='!', intents=intents)

server_states = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="music"))

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    
    if voice_client and voice_client.channel and len(voice_client.channel.members) == 1:
        guild_id = member.guild.id
        if guild_id in server_states:
            del server_states[guild_id]
            
        await voice_client.disconnect()
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="music"))

def get_state(guild_id):
    if guild_id not in server_states:
        server_states[guild_id] = {
            "queue": [],
            "filters": {"bassboost": False, "nightcore": False},
            "current": None
        }
    return server_states[guild_id]

def build_ffmpeg_options(state):
    options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }
    
    audio_filters = []
    if state["filters"]["bassboost"]:
        audio_filters.append("equalizer=f=60:width_type=h:width=50:g=10")
    if state["filters"]["nightcore"]:
        audio_filters.append("atempo=1.25,asetrate=44100*1.25")
        
    if audio_filters:
        options['options'] += f' -af "{",".join(audio_filters)}"'
        
    return options

def play_next(ctx):
    guild_id = ctx.guild.id
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    state = get_state(guild_id)
    
    if not voice_client:
        return

    if state["queue"]:
        next_track = state["queue"].pop(0)
        state["current"] = next_track
        
        audio_source = discord.FFmpegPCMAudio(
            next_track['url'], 
            executable="./ffmpeg.exe", 
            **build_ffmpeg_options(state)
        )
        voice_client.play(audio_source, after=lambda e: play_next(ctx))
        
        bot.loop.create_task(bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name=next_track['title'])
        ))
        asyncio.run_coroutine_threadsafe(send_embed(ctx, next_track), bot.loop)
    else:
        state["current"] = None
        bot.loop.create_task(bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="music")
        ))

class PlaybackControlView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="⏮️ Restart", style=discord.ButtonStyle.secondary)
    async def restart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        state = get_state(interaction.guild.id)
        if voice_client and state["current"]:
            await interaction.response.defer()
            state["queue"].insert(0, state["current"])
            voice_client.stop()
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

    @discord.ui.button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.primary)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if not voice_client:
            return await interaction.response.send_message("Not connected to voice.", ephemeral=True)
            
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Paused.", ephemeral=True)
        elif voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Resumed.", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            await interaction.response.defer()
            voice_client.stop()

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if voice_client:
            get_state(interaction.guild.id)["queue"] = []
            voice_client.stop()
            await interaction.response.send_message("Stopped and cleared queue.", ephemeral=False)

    @discord.ui.button(label="📜 Queue", style=discord.ButtonStyle.secondary)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = get_state(interaction.guild.id)
        if not state["queue"]:
            return await interaction.response.send_message("Queue is empty.", ephemeral=True)

        queue_str = "\n".join(f"{i}. {t['title']}" for i, t in enumerate(state["queue"], start=1))
        embed = discord.Embed(title="Queue", description=queue_str, color=0xD5D8C1)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def send_embed(ctx, video_data):
    state = get_state(ctx.guild.id)
    embed = discord.Embed(title=video_data['title'], url=video_data.get('webpage_url'), color=0xD5D8C1)
    embed.set_author(name="NOW PLAYING")
    if video_data.get('thumbnail'):
        embed.set_image(url=video_data['thumbnail'])

    duration = f"{video_data.get('duration', 0)//60}:{video_data.get('duration', 0)%60:02d}"
    fx = [k for k, v in state["filters"].items() if v]
    
    embed.add_field(name="Length", value=f"`{duration}`", inline=True)
    embed.add_field(name="Requester", value=ctx.author.mention, inline=True)
    embed.add_field(name="FX", value=f"`{', '.join(fx) if fx else 'None'}`", inline=True)
    embed.set_footer(text=f"Source: {video_data.get('uploader', 'Unknown')} | Syre")

    await ctx.send(embed=embed, view=PlaybackControlView(ctx))

@bot.command(name='play')
async def play(ctx, *, song_name):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first.")
    
    voice_client = ctx.voice_client
    if not voice_client:
        voice_client = await ctx.author.voice.channel.connect()
    elif voice_client.channel != ctx.author.voice.channel:
        await voice_client.move_to(ctx.author.voice.channel)

    await ctx.send(f"Searching: `{song_name}`...")

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'default_search': 'ytsearch'}
    loop = asyncio.get_event_loop()
    info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(song_name, download=False))
    video_data = info['entries'][0] if 'entries' in info else info

    state = get_state(ctx.guild.id)
    if voice_client.is_playing() or voice_client.is_paused():
        state["queue"].append(video_data)
        await ctx.send(f"Queued: **{video_data['title']}**")
    else:
        state["current"] = video_data
        voice_client.play(discord.FFmpegPCMAudio(video_data['url'], executable="./ffmpeg.exe", **build_ffmpeg_options(state)), after=lambda e: play_next(ctx))
        await send_embed(ctx, video_data)

@bot.command()
async def bassboost(ctx):
    state = get_state(ctx.guild.id)
    state["filters"]["bassboost"] = not state["filters"]["bassboost"]
    await ctx.send(f"Bass Boost: {'ON' if state['filters']['bassboost'] else 'OFF'}")

@bot.command()
async def nightcore(ctx):
    state = get_state(ctx.guild.id)
    state["filters"]["nightcore"] = not state["filters"]["nightcore"]
    await ctx.send(f"Nightcore: {'ON' if state['filters']['nightcore'] else 'OFF'}")

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        get_state(ctx.guild.id)["queue"] = []
        ctx.voice_client.stop()

@bot.command(aliases=['q'])
async def queue(ctx):
    state = get_state(ctx.guild.id)
    if not state["queue"]:
        return await ctx.send("Queue is empty.")
    
    msg = "\n".join(f"{i}. {t['title']}" for i, t in enumerate(state["queue"], start=1))
    await ctx.send(f"**Queue:**\n{msg}")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        if ctx.guild.id in server_states:
            del server_states[ctx.guild.id]

bot.run(TOKEN)