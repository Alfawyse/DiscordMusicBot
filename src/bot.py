"""Run with python -m src.bot or python src/bot.py."""
import argparse
import logging
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import discord
from discord.ext import commands
from src.config import check_settings, get_bot_intents, load_settings
from src.music.commands import setup_music_commands
from src.help import SpanishHelpCommand

log = logging.getLogger(__name__)


def create_bot(settings):
    bot = commands.Bot(
        command_prefix=settings.prefix,
        help_command=SpanishHelpCommand(),
        intents=get_bot_intents(),
        allowed_mentions=discord.AllowedMentions.none(),
    )
    setup_music_commands(bot, settings)

    @bot.event
    async def on_ready():
        log.info("Bot conectado: %s", bot.user)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("Usa este comando dentro de un servidor.")
        elif isinstance(error, commands.UserInputError):
            await ctx.send(f"Revisa el comando. Usa {settings.prefix}help.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("No puedes usar este comando aqui.")
        else:
            original = getattr(error, "original", error)
            log.error("Error en comando", exc_info=(type(original), original, original.__traceback__))
            await ctx.send("Ocurrio un error. Revisa el registro del bot.")
    return bot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Valida configuracion sin conectar a Discord.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        settings = load_settings()
    except ValueError as error:
        log.error("%s", error)
        return 1
    errors = check_settings(settings)
    for error in errors:
        log.error("%s", error)
    if errors:
        return 1
    if args.check:
        print("Configuracion local valida. Token y permisos se verifican al conectar.")
        return 0
    try:
        create_bot(settings).run(settings.token)
    except discord.LoginFailure:
        log.error("Discord rechazo el token. Actualiza DISCORD_TOKEN en .env.")
        return 1
    except discord.PrivilegedIntentsRequired:
        log.error("Activa Message Content Intent en Discord Developer Portal > Bot.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
