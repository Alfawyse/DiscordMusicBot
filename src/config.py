"""Configuration loaded from the project root, regardless of working directory."""
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import discord
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    token: str
    prefix: str
    ffmpeg: str
    volume: float
    cookies: str | None
    js_runtime: str


def load_settings():
    token = os.getenv("DISCORD_TOKEN", "").strip()
    prefix = os.getenv("COMMAND_PREFIX", ".").strip()
    ffmpeg = os.getenv("FFMPEG_PATH", "ffmpeg").strip()
    runtime = os.getenv("YTDLP_JS_RUNTIME", "node").strip()
    try:
        volume = float(os.getenv("DEFAULT_VOLUME", "0.25"))
    except ValueError:
        raise ValueError("DEFAULT_VOLUME debe ser un numero entre 0 y 1.") from None
    if not 0 <= volume <= 1:
        raise ValueError("DEFAULT_VOLUME debe estar entre 0 y 1.")
    if not prefix:
        raise ValueError("COMMAND_PREFIX no puede estar vacio.")
    if runtime not in {"node", "deno", "quickjs"}:
        raise ValueError("YTDLP_JS_RUNTIME debe ser node, deno o quickjs.")
    cookie_value = os.getenv("YTDLP_COOKIES_FILE", "").strip()
    cookies = str((ROOT / cookie_value).resolve()) if cookie_value else None
    return Settings(token, prefix, ffmpeg, volume, cookies, runtime)


def check_settings(settings):
    errors = []
    if not settings.token or settings.token in {"YOUR_BOT_TOKEN", "TU_TOKEN_AQUI"}:
        errors.append("Falta DISCORD_TOKEN: agrega el token del bot al archivo .env.")
    if not shutil.which(settings.ffmpeg):
        errors.append("No se encontro FFmpeg. Instala FFmpeg o configura FFMPEG_PATH.")
    if not shutil.which(settings.js_runtime):
        errors.append(f"No se encontro el runtime JavaScript: {settings.js_runtime}.")
    if settings.cookies and not Path(settings.cookies).is_file():
        errors.append("YTDLP_COOKIES_FILE no corresponde a un archivo existente.")
    return errors


def get_bot_intents():
    intents = discord.Intents.default()
    intents.message_content = True
    return intents
