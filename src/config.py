import os
from dotenv import load_dotenv
import discord

# Load environment variables from a .env file
load_dotenv()

# Retrieve the Discord bot token from the environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


# Configure the bot's intents (permissions required by the bot)
def get_bot_intents():
    """
    Returns a configured discord.Intents object with the necessary permissions.

    - Enables the bot to read messages and interact with them.
    - This configuration can be extended depending on the bot's requirements.

    Returns:
        discord.Intents: Configured intents for the bot.
    """
    intents = discord.Intents.default()
    intents.message_content = True  # Allows the bot to read message content
    return intents
