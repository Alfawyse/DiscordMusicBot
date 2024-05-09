# Discord Music Bot

This is a Discord bot that allows you to play music in voice channels. It supports searching and playing songs from YouTube, as well as managing a queue, pausing, resuming, and skipping tracks.

## Prerequisites

Before you can run the bot, you need to have the following installed:

- Python 3.x
- Discord.py
- youtube-search-python
- yt-dlp
- python-dotenv

You can install the required packages using pip

## Setup

1. Create a new Discord bot and obtain its token from the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a `.env` file in the same directory as the bot script and add the following line, replacing `YOUR_BOT_TOKEN` with your actual bot token
3. Invite the bot to your Discord server using the OAuth2 URL Generator in the Discord Developer Portal.

## Usage

To start the bot, run the `run_bot()` function in the script. The bot will respond to the following commands:

- `.play <query>`: Searches for and plays the specified song or YouTube link.
- `.pause`: Pauses the currently playing track.
- `.resume`: Resumes the paused track.
- `.stop`: Stops the currently playing track and disconnects the bot from the voice channel.
- `.skip`: Skips the currently playing track and plays the next one in the queue.
- `.clear`: Clears the song queue.
- `.queue`: Displays the current song queue.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
