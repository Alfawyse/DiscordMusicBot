import discord
import asyncio
import yt_dlp
from youtube_search import YoutubeSearch

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}
        self.ytdl = yt_dlp.YoutubeDL({"format": "bestaudio/best"})
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }

    async def play(self, ctx, *args):
        if ctx.author.voice is None:
            return await ctx.send("Please join a voice channel first!")

        voice_client = self.voice_clients.get(ctx.guild.id)
        if voice_client and voice_client.is_playing():
            if ctx.guild.id not in self.queues:
                self.queues[ctx.guild.id] = []
            self.queues[ctx.guild.id].append(" ".join(args))
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
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(link)

        if not self.voice_clients[ctx.guild.id].is_playing():
            await self.select_and_play(ctx)

        if option:
            await ctx.send(f"Now playing: **{option['title']}** - Duration: {option['duration']}")

    async def select_and_play(self, ctx):
        if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
            return

        link = self.queues[ctx.guild.id].pop(0)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)

        self.voice_clients[ctx.guild.id].play(
            player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        )
        await ctx.send("Now playing!")

    async def play_next(self, ctx):
        if self.queues[ctx.guild.id] != []:
            link = self.queues[ctx.guild.id].pop(0)
            await self.play(ctx, link)

    async def pause(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].pause()

    async def resume(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].resume()

    async def stop(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]

    async def skip(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send("Skipped current track!")

    async def show_queue(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            queue_list = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(self.queues[ctx.guild.id])])
            await ctx.send(f"Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is currently empty!")

    async def clear_queue(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send("There is no queue to clear!")
