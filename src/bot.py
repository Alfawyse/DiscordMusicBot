from discord.ext import commands
from config import DISCORD_TOKEN, get_bot_intents
from src.music.commands import setup_music_commands  # Ajusta la importación según tu estructura de carpetas

def main():
    """
    Main entry point for the Discord bot.

    This function configures the bot with necessary intents, sets up music commands, and starts the bot.
    """
    # Create the bot instance with a command prefix and configured intents
    bot = commands.Bot(command_prefix=".", intents=get_bot_intents())

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

    # Run the bot with the loaded token
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
