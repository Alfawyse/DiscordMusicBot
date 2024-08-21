import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from src.music.commands import setup_music_commands  # Make sure to adjust the import according to your folder structure

def main():
    """
    Main entry point for the Discord bot.

    This function loads environment variables, configures the bot with necessary intents,
    sets up music commands, and starts the bot.
    """
    # Load environment variables
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    # Configure intents (permissions for the bot)
    intents = discord.Intents.default()
    intents.message_content = True

    # Create the bot instance with a command prefix and intents
    bot = commands.Bot(command_prefix=".", intents=intents)

    # Load extensions/commands
    setup_music_commands(bot)

    # Event triggered when the bot is ready and connected
    @bot.event
    async def on_ready():
        """
        Event handler that is called when the bot has successfully connected to Discord.

        This function prints a message to the console indicating that the bot is online and ready.
        """
        print(f'{bot.user} is now online and ready to jam!')

    # Run the bot
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
