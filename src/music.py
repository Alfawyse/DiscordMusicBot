from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import yt_dlp
import os
from youtube_search import YoutubeSearch

def run_bot():
    
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix=".", intents=intents)
    voice_clients = {}
    queues = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link)

    async def select_option(ctx, results):
        options = "\n".join([f"{i + 1}. {results[i]['title']}" for i in range(len(results))])
        await ctx.send(f"Select a song by typing its number:\n{options}")

        def check(message):
            return message.author == ctx.author and message.content.isdigit() and 0 < int(message.content) <= len(results)

        try:
            response = await client.wait_for("message", check=check, timeout=30)
            index = int(response.content) - 1
            return results[index]
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return None

    @client.command(name="play")
    async def play(ctx, *args):
        try:
            if ctx.author.voice is None:
                return await ctx.send("Please join a voice channel first!")

            voice_client = voice_clients.get(ctx.guild.id)
            if voice_client and voice_client.is_playing():
                if ctx.guild.id not in queues:
                    queues[ctx.guild.id] = []
                queues[ctx.guild.id].append(" ".join(args))
                await ctx.send("Song added to the queue!")
                return
            
            if ctx.guild.id not in voice_clients:
                voice_client = await ctx.author.voice.channel.connect()
                voice_clients[ctx.guild.id] = voice_client

            link = args[0]
            if "youtube.com" in link or "youtu.be" in link:
                await add_and_play(ctx, link)
                return

            search_query = " ".join(args)
            results = YoutubeSearch(search_query, max_results=1).to_dict()
            if not results:
                return await ctx.send("No results found!")

            option = results[0]
            link = "https://www.youtube.com" + option['url_suffix']
            await add_and_play(ctx, link, option)
        except Exception as e:
            print(e)

    async def add_and_play(ctx, link, option=None):
        try:
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(link)

            if not voice_clients[ctx.guild.id].is_playing():
                await select_and_play(ctx)

            if option:
                await ctx.send(f"Now playing: **{option['title']}** - Duration: {option['duration']}")
        except Exception as e:
            print(e)

    async def select_and_play(ctx):
        if ctx.guild.id not in queues or not queues[ctx.guild.id]:
            return
        
        link = queues[ctx.guild.id].pop(0)
        
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send("Now playing!")


    @client.command(name="clear")
    async def clear_queue(ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send("There is no queue to clear!")

    @client.command(name="pause")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

    @client.command(name="resume")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    @client.command(name="stop")
    async def stop(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
        except Exception as e:
            print(e)

    @client.command(name="skip")
    async def skip(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await play_next(ctx)
            await ctx.send("Skipped current track!")
        except Exception as e:
            print(e)
    
    @client.command(name="queue")
    async def show_queue(ctx):
        if ctx.guild.id in queues and queues[ctx.guild.id]:
            queue_list = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(queues[ctx.guild.id])])
            await ctx.send(f"Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is currently empty!")
            
    client.run(TOKEN)

run_bot()























