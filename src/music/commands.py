from discord.ext import commands
from src.music.player import MusicPlayer

def setup_music_commands(bot):
    """
    Registers the music-related commands to the bot.

    Args:
        bot (commands.Bot): The instance of the bot where commands will be registered.
    """
    # Create an instance of the MusicPlayer to handle music functionality
    music_player = MusicPlayer(bot)

    @bot.command(name="play")
    async def play(ctx, *args):
        """
        Command to play a song or add it to the queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            *args: The search query or link to the song to be played.
        """
        await music_player.play(ctx, *args)

    @bot.command(name="pause")
    async def pause(ctx):
        """
        Command to pause the currently playing song.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.pause(ctx)

    @bot.command(name="resume")
    async def resume(ctx):
        """
        Command to resume the currently paused song.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.resume(ctx)

    @bot.command(name="stop")
    async def stop(ctx):
        """
        Command to stop the music and disconnect the bot from the voice channel.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.stop(ctx)

    @bot.command(name="skip")
    async def skip(ctx):
        """
        Command to skip the currently playing song and play the next one in the queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.skip(ctx)

    @bot.command(name="queue")
    async def show_queue(ctx):
        """
        Command to display the current music queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.show_queue(ctx)

    @bot.command(name="clear")
    async def clear_queue(ctx):
        """
        Command to clear the current music queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        await music_player.clear_queue(ctx)

