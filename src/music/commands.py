from discord.ext import commands
from src.music.player import MusicPlayer


def setup_music_commands(bot, settings):
    player = MusicPlayer(bot, settings)

    @bot.command(name="play", usage="<nombre o enlace de YouTube>", help="Reproduce un enlace de YouTube o busca una canción.")
    @commands.guild_only()
    async def play(ctx, *, query=""):
        await player.play(ctx, query)

    @bot.command(name="pause", help="Pausa la canción actual.")
    @commands.guild_only()
    async def pause(ctx):
        await player.pause(ctx)

    @bot.command(name="resume", help="Continúa la canción pausada.")
    @commands.guild_only()
    async def resume(ctx):
        await player.resume(ctx)

    @bot.command(name="stop", help="Vacía la cola y desconecta el bot.")
    @commands.guild_only()
    async def stop(ctx):
        await player.stop(ctx)

    @bot.command(name="skip", help="Salta una canción.")
    @commands.guild_only()
    async def skip(ctx):
        await player.skip(ctx)

    @bot.command(name="queue", help="Muestra las canciónes pendientes.")
    @commands.guild_only()
    async def show_queue(ctx):
        await player.show_queue(ctx)

    @bot.command(name="clear", help="Vacía las canciónes pendientes.")
    @commands.guild_only()
    async def clear(ctx):
        await player.clear_queue(ctx)

    @bot.event
    async def on_voice_state_update(member, before, after):
        if member.id == bot.user.id and before.channel and after.channel is None:
            await player.handle_disconnect(member.guild.id)
