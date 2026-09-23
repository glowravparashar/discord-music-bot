import discord

class PlayerControlView(discord.ui.View):
    def __init__(self, music_cog, ctx):
        super().__init__(timeout=None)
        self.cog = music_cog
        self.ctx = ctx

    @discord.ui.button(label="Pause/Resume", style=discord.ButtonStyle.secondary, emoji="⏯️")
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.voice_client:
            if self.ctx.voice_client.is_playing():
                self.ctx.voice_client.pause()
                await interaction.response.send_message("Paused playback.", ephemeral=True)
            elif self.ctx.voice_client.is_paused():
                self.ctx.voice_client.resume()
                await interaction.response.send_message("Resumed playback.", ephemeral=True)
            else:
                await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.voice_client and (self.ctx.voice_client.is_playing() or self.ctx.voice_client.is_paused()):
            self.ctx.voice_client.stop()
            await interaction.response.send_message("Skipped track.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing to skip.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.ctx.voice_client:
            if self.ctx.guild.id in self.cog.queues:
                self.cog.queues[self.ctx.guild.id].clear()
            self.ctx.voice_client.stop()
            await self.ctx.voice_client.disconnect()
            await interaction.response.send_message("Stopped audio and disconnected.", ephemeral=True)