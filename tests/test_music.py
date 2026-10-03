import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from src.config import Settings, load_settings
from src.music.player import MusicPlayer
from src.music.queue import MusicQueue


class QueueTests(unittest.TestCase):
    def test_order_and_guild_isolation(self):
        queue = MusicQueue()
        queue.add_to_queue(1, "first")
        queue.add_to_queue(1, "second")
        queue.add_to_queue(2, "other")
        self.assertEqual(queue.get_next_song(1), "first")
        snapshot = queue.get_queue(1)
        snapshot.clear()
        self.assertEqual(queue.get_next_song(1), "second")
        queue.clear_queue(1)
        self.assertEqual(queue.get_next_song(2), "other")
        self.assertIsNone(queue.get_next_song(1))

    def test_invalid_volume(self):
        for value in ("bad", "2", "nan"):
            with self.subTest(value=value), patch.dict("os.environ", {"DEFAULT_VOLUME": value}):
                with self.assertRaises(ValueError):
                    load_settings()


class PlayerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = Mock()
        self.client.channel = SimpleNamespace(id=20)
        self.client.is_connected.return_value = True
        self.client.is_playing.return_value = False
        self.client.is_paused.return_value = False
        self.client.disconnect = AsyncMock()
        self.ctx = SimpleNamespace(
            guild=SimpleNamespace(id=1, voice_client=self.client),
            author=SimpleNamespace(voice=SimpleNamespace(channel=self.client.channel)),
            send=AsyncMock(),
        )
        settings = Settings("dummy", ".", "ffmpeg", 0.25, None, "node")
        self.player = MusicPlayer(Mock(), settings)

    async def test_paused_song_queues_without_replacing_audio(self):
        self.client.is_paused.return_value = True
        self.player._play_next = AsyncMock()
        await self.player.play(self.ctx, "next song")
        self.assertEqual(self.player.queue.get_queue(1), ["next song"])
        self.player._play_next.assert_not_awaited()

    async def test_skip_advances_once_via_completion(self):
        self.client.is_playing.return_value = True
        self.player._play_next = AsyncMock()
        await self.player.skip(self.ctx)
        self.client.stop.assert_called_once()
        self.player._play_next.assert_not_awaited()
        await self.player._finished(self.ctx, 0, None)
        self.player._play_next.assert_awaited_once()

    async def test_stop_clears_queue_and_invalidates_old_callback(self):
        self.player.queue.add_to_queue(1, "pending")
        self.player._play_next = AsyncMock()
        await self.player.stop(self.ctx)
        await self.player._finished(self.ctx, 0, None)
        self.assertFalse(self.player.queue.has_queue(1))
        self.client.disconnect.assert_awaited_once()
        self.player._play_next.assert_not_awaited()

    async def test_cannot_control_another_channel(self):
        self.ctx.author.voice.channel = SimpleNamespace(id=99)
        await self.player.stop(self.ctx)
        self.client.stop.assert_not_called()
        self.client.disconnect.assert_not_awaited()

    async def test_failed_track_does_not_block_next_track(self):
        self.player.queue.add_to_queue(1, "bad")
        self.player.queue.add_to_queue(1, "good")
        self.player.extract = Mock(side_effect=[ValueError("unavailable"), {"url": "https://audio", "title": "good"}])
        with patch("src.music.player.discord.FFmpegOpusAudio"):
            with self.assertLogs("src.music.player", level="ERROR"):
                await self.player._play_next(self.ctx)
        self.client.play.assert_called_once()
        self.assertFalse(self.player.queue.has_queue(1))

    async def test_external_disconnect_invalidates_playback(self):
        self.player.queue.add_to_queue(1, "pending")
        self.player._play_next = AsyncMock()
        await self.player.handle_disconnect(1)
        await self.player._finished(self.ctx, 0, None)
        self.assertFalse(self.player.queue.has_queue(1))
        self.player._play_next.assert_not_awaited()

    async def test_simultaneous_play_calls_do_not_replace_current_track(self):
        self.player.extract = Mock(return_value={"url": "https://audio", "title": "first"})
        self.client.play.side_effect = lambda *args, **kwargs: setattr(self.client.is_playing, "return_value", True)
        with patch("src.music.player.discord.FFmpegOpusAudio"):
            await asyncio.gather(self.player.play(self.ctx, "first"), self.player.play(self.ctx, "second"))
        self.client.play.assert_called_once()
        self.assertEqual(self.player.queue.get_queue(1), ["second"])

    def test_rejects_non_youtube_urls(self):
        for query in ("file:///private", "https://example.com/audio", "https://youtube.com.attacker.test"):
            with self.subTest(query=query), self.assertRaises(ValueError):
                self.player.extract(query)


if __name__ == "__main__":
    unittest.main()
