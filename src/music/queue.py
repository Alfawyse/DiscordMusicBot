class MusicQueue:
    def __init__(self):
        """
        Initializes a new instance of MusicQueue.
        """
        self.queues = {}

    def add_to_queue(self, guild_id, link):
        """
        Adds a song to the queue for a specific guild.

        Args:
            guild_id (int): The ID of the guild (server) where the song is being added.
            link (str): The URL or identifier of the song to be added.
        """
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        self.queues[guild_id].append(link)

    def get_next_song(self, guild_id):
        """
        Retrieves and removes the next song from the queue for a specific guild.

        Args:
            guild_id (int): The ID of the guild (server) where the song is being retrieved.

        Returns:
            str: The URL or identifier of the next song in the queue, or None if the queue is empty.
        """
        if guild_id in self.queues and self.queues[guild_id]:
            return self.queues[guild_id].pop(0)
        return None

    def clear_queue(self, guild_id):
        """
        Clears the queue for a specific guild.

        Args:
            guild_id (int): The ID of the guild (server) where the queue is being cleared.
        """
        if guild_id in self.queues:
            self.queues[guild_id].clear()

    def get_queue(self, guild_id):
        """
        Retrieves the current queue for a specific guild.

        Args:
            guild_id (int): The ID of the guild (server) where the queue is being retrieved.

        Returns:
            list: A list of URLs or identifiers representing the current queue.
        """
        return self.queues.get(guild_id, [])

    def has_queue(self, guild_id):
        """
        Checks if there is an active queue for a specific guild.

        Args:
            guild_id (int): The ID of the guild (server) being checked.

        Returns:
            bool: True if the guild has an active queue, False otherwise.
        """
        return guild_id in self.queues and len(self.queues[guild_id]) > 0
