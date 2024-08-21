import discord
import asyncio
import yt_dlp
from youtube_search import YoutubeSearch
from src.music.queue import MusicQueue  # Asegúrate de ajustar la ruta de importación según tu estructura de carpetas

class MusicPlayer:
    def __init__(self, bot):
        """
        Initializes a new instance of the MusicPlayer class.

        Args:
            bot (commands.Bot): The Discord bot instance to which this player is attached.
        """
        self.bot = bot
        self.voice_clients = {}
        self.queue = MusicQueue()  # Instancia de MusicQueue
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }

    async def play(self, ctx, *args):
        """
        Plays a song or adds it to the queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            *args: The search query or link to the song to be played.
        """
        if ctx.author.voice is None:
            return await ctx.send("Please join a voice channel first!")

        voice_client = self.voice_clients.get(ctx.guild.id)
        if voice_client and voice_client.is_playing():
            self.queue.add_to_queue(ctx.guild.id, " ".join(args))
            await ctx.send("Song added to the queue!")
            return

        if ctx.guild.id not in self.voice_clients:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client

        link = args[0]
        if "youtube.com" in link or "youtu.be" in link:
            await self.add_and_play(ctx, link)
            return

        search_query = " ".join(args)
        results = YoutubeSearch(search_query, max_results=1).to_dict()
        if not results:
            return await ctx.send("No results found!")

        option = results[0]
        link = "https://www.youtube.com" + option['url_suffix']
        await self.add_and_play(ctx, link, option)

    async def add_and_play(self, ctx, link, option=None):
        """
        Adds a song to the queue and plays it if nothing else is playing.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            link (str): The URL of the song to be played.
            option (dict, optional): Additional information about the song.
        """
        self.queue.add_to_queue(ctx.guild.id, link)

        if not self.voice_clients[ctx.guild.id].is_playing():
            await self.select_and_play(ctx)

        if option:
            await ctx.send(f"Now playing: **{option['title']}** - Duration: {option['duration']}")

    async def select_and_play(self, ctx):
        """
        Selects the next song from the queue and plays it.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        link = self.queue.get_next_song(ctx.guild.id)
        if not link:
            return

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)

        self.voice_clients[ctx.guild.id].play(
            player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        )
        await ctx.send("Now playing!")

    async def play_next(self, ctx):
        """
        Plays the next song in the queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        link = self.queue.get_next_song(ctx.guild.id)
        if link:
            await self.play(ctx, link)

    async def pause(self, ctx):
        """
        Pauses the currently playing song.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].pause()

    async def resume(self, ctx):
        """
        Resumes the currently paused song.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].resume()

    async def stop(self, ctx):
        """
        Stops the music and disconnects the bot from the voice channel.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]

    async def skip(self, ctx):
        """
        Skips the currently playing song and plays the next one in the queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send("Skipped current track!")

    async def show_queue(self, ctx):
        """
        Displays the current music queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        queue_list = self.queue.get_queue(ctx.guild.id)
        if queue_list:
            formatted_queue = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(queue_list)])
            await ctx.send(f"Queue:\n{formatted_queue}")
        else:
            await ctx.send("The queue is currently empty!")

    async def clear_queue(self, ctx):
        """
        Clears the current music queue.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
        """
        self.queue.clear_queue(ctx.guild.id)
        await ctx.send("Queue cleared!")
