from collections import deque


class MusicQueue:
    def __init__(self):
        self.queues = {}

    def add_to_queue(self, guild_id, query):
        self.queues.setdefault(guild_id, deque()).append(query)

    def get_next_song(self, guild_id):
        queue = self.queues.get(guild_id)
        return queue.popleft() if queue else None

    def clear_queue(self, guild_id):
        self.queues.pop(guild_id, None)

    def get_queue(self, guild_id):
        return list(self.queues.get(guild_id, ()))

    def has_queue(self, guild_id):
        return bool(self.queues.get(guild_id))
