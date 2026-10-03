"""Spanish help messages for the bot's existing prefix commands."""
import discord
from discord.ext import commands


class SpanishHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            "help": "Muestra los comandos o la ayuda de un comando.",
            "usage": "[comando]",
        })

    async def send_bot_help(self, mapping):
        available = await self.filter_commands(
            [command for group in mapping.values() for command in group], sort=True
        )
        prefix = self.context.clean_prefix
        embed = discord.Embed(
            title="Ayuda del bot de música",
            description="Entra a un canal de voz y reproduce una canción con "
                        f"{prefix}play <nombre o enlace de YouTube>.",
            colour=discord.Colour.blurple(),
        )
        music = [command for command in available if command.name != "help"]
        if music:
            embed.add_field(name="Música", value="\n".join(
                f"**{prefix}{command.name}** - {command.short_doc}"
                for command in music
            ), inline=False)
        embed.add_field(name="Ayuda", value=f"**{prefix}help [comando]** - Muestra ayuda detallada.", inline=False)
        embed.set_footer(text=f"Ejemplo: {prefix}help play | Para controlar la música, entra al mismo canal de voz que el bot.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        prefix = self.context.clean_prefix
        usage = command.usage or command.signature
        invocation = f"{prefix}{command.qualified_name}" + (f" {usage}" if usage else "")
        embed = discord.Embed(
            title=f"Ayuda: {prefix}{command.qualified_name}",
            description=command.help or "Sin descripción disponible.",
            colour=discord.Colour.blurple(),
        )
        embed.add_field(name="Uso", value=f"`{invocation}`", inline=False)
        if command.name == "play":
            embed.add_field(name="Ejemplos", value=(
                f"`{prefix}play Daft Punk One More Time`\n"
                f"`{prefix}play https://www.youtube.com/watch?v=dQw4w9WgXcQ`"
            ), inline=False)
        embed.set_footer(text=f"Usa {prefix}help para ver todos los comandos.")
        await self.get_destination().send(embed=embed)

    def command_not_found(self, string):
        return f"Ese comando no existe. Usa {self.context.clean_prefix}help para ver los disponibles."

    def subcommand_not_found(self, command, string):
        return f"Ese subcomando no existe. Usa {self.context.clean_prefix}help {command.qualified_name}."
