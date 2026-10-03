"""Per-server playback, with serialized commands and one completion callback."""
import asyncio
import logging
from collections import defaultdict
from urllib.parse import urlparse

import discord
import yt_dlp

from src.music.queue import MusicQueue

log = logging.getLogger(__name__)


class MusicPlayer:
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.queue = MusicQueue()
        self.locks = defaultdict(asyncio.Lock)
        self.generations = defaultdict(int)

    @staticmethod
    def voice_client(ctx):
        return ctx.guild.voice_client

    async def require_channel(self, ctx):
        voice = getattr(ctx.author, "voice", None)
        if not voice or not voice.channel:
            await ctx.send("Entra primero a un canal de voz.")
            return False
        client = self.voice_client(ctx)
        if client and client.channel != voice.channel:
            await ctx.send("Debes estar en el mismo canal de voz que el bot.")
            return False
        return True

    def extract(self, query):
        parsed = urlparse(query)
        if parsed.scheme:
            if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
                "youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com",
                "youtu.be", "www.youtu.be",
            }:
                raise ValueError("Usa una busqueda o un enlace de YouTube.")
            target = query
        else:
            target = "ytsearch1:" + query
        options = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": False,
            "socket_timeout": 20,
            "retries": 2,
            "cachedir": False,
            "js_runtimes": {self.settings.js_runtime: {}},
        }
        if self.settings.cookies:
            options["cookiefile"] = self.settings.cookies
        # Separate instances prevent concurrent servers from sharing extractor state.
        with yt_dlp.YoutubeDL(options) as extractor:
            data = extractor.extract_info(target, download=False)
        if data and "entries" in data:
            data = next((entry for entry in data["entries"] if entry), None)
        if not data or not data.get("url"):
            raise ValueError("No se encontro audio para esa busqueda.")
        return data

    async def play(self, ctx, query):
        query = query.strip()
        if not query:
            await ctx.send("Escribe el nombre de una cancion o un enlace de YouTube.")
            return
        async with self.locks[ctx.guild.id]:
            if not await self.require_channel(ctx):
                return
            client = self.voice_client(ctx)
            if not client or not client.is_connected():
                try:
                    client = await ctx.author.voice.channel.connect()
                except (discord.DiscordException, asyncio.TimeoutError):
                    log.exception("No se pudo conectar al canal de voz")
                    await ctx.send("No pude entrar al canal. Revisa los permisos Conectar y Hablar.")
                    return
            self.queue.add_to_queue(ctx.guild.id, query)
            if client.is_playing() or client.is_paused():
                await ctx.send("Cancion agregada a la cola.")
            else:
                await self._play_next(ctx)

    async def _play_next(self, ctx):
        guild_id = ctx.guild.id
        client = self.voice_client(ctx)
        generation = self.generations[guild_id]
        loop = asyncio.get_running_loop()
        while client and client.is_connected() and not client.is_playing() and not client.is_paused():
            query = self.queue.get_next_song(guild_id)
            if query is None:
                return
            source = None
            try:
                data = await asyncio.to_thread(self.extract, query)
                if generation != self.generations[guild_id] or not client.is_connected():
                    return
                source = await asyncio.to_thread(
                    discord.FFmpegOpusAudio,
                    data["url"], executable=self.settings.ffmpeg,
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options=f'-vn -filter:a "volume={self.settings.volume}"',
                )
                if generation != self.generations[guild_id] or not client.is_connected():
                    source.cleanup()
                    return

                def after(error):
                    future = asyncio.run_coroutine_threadsafe(
                        self._finished(ctx, generation, error), loop
                    )
                    future.add_done_callback(self._callback_result)

                client.play(source, after=after)
            except Exception:
                if source:
                    source.cleanup()
                log.exception("Fallo al preparar la cancion")
                await ctx.send("No pude reproducir una cancion. Intentare la siguiente si hay mas.")
                continue
            title = discord.utils.escape_markdown(str(data.get("title") or query))[:300]
            await ctx.send(f"Reproduciendo: **{title}**")
            return

    @staticmethod
    def _callback_result(future):
        try:
            future.result()
        except Exception:
            log.exception("Fallo al avanzar la cola")

    async def _finished(self, ctx, generation, error):
        async with self.locks[ctx.guild.id]:
            if generation != self.generations[ctx.guild.id]:
                return
            if error:
                log.error("Fallo en la reproduccion: %s", error)
                await ctx.send("El audio se interrumpio. Intentare la siguiente cancion.")
            await self._play_next(ctx)

    async def handle_disconnect(self, guild_id):
        # Invalidate callbacks immediately, even if extraction holds the lock.
        self.generations[guild_id] += 1
        self.queue.clear_queue(guild_id)

    async def pause(self, ctx):
        async with self.locks[ctx.guild.id]:
            if not await self.require_channel(ctx):
                return
            client = self.voice_client(ctx)
            if client and client.is_playing():
                client.pause()
                await ctx.send("Reproduccion pausada.")
            else:
                await ctx.send("No hay una cancion reproduciendose.")

    async def resume(self, ctx):
        async with self.locks[ctx.guild.id]:
            if not await self.require_channel(ctx):
                return
            client = self.voice_client(ctx)
            if client and client.is_paused():
                client.resume()
                await ctx.send("Reproduccion reanudada.")
            else:
                await ctx.send("No hay una cancion pausada.")

    async def skip(self, ctx):
        async with self.locks[ctx.guild.id]:
            if not await self.require_channel(ctx):
                return
            client = self.voice_client(ctx)
            if client and (client.is_playing() or client.is_paused()):
                # stop() invokes after; that callback alone advances the queue.
                client.stop()
                await ctx.send("Cancion saltada.")
            else:
                await ctx.send("No hay una cancion para saltar.")

    async def stop(self, ctx):
        async with self.locks[ctx.guild.id]:
            if not await self.require_channel(ctx):
                return
            self.generations[ctx.guild.id] += 1
            self.queue.clear_queue(ctx.guild.id)
            client = self.voice_client(ctx)
            if client:
                client.stop()
                await client.disconnect()
            await ctx.send("Cola vaciada y bot desconectado.")

    async def show_queue(self, ctx):
        items = self.queue.get_queue(ctx.guild.id)
        if not items:
            await ctx.send("La cola esta vacia.")
            return
        lines = [f"{i}. {discord.utils.escape_markdown(item)[:100]}" for i, item in enumerate(items[:15], 1)]
        if len(items) > 15:
            lines.append(f"... y {len(items) - 15} canciones mas.")
        await ctx.send("Cola:\n" + "\n".join(lines))

    async def clear_queue(self, ctx):
        async with self.locks[ctx.guild.id]:
            if await self.require_channel(ctx):
                self.queue.clear_queue(ctx.guild.id)
                await ctx.send("Cola vaciada.")
