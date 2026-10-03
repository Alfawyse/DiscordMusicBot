# Discord Music Bot

Bot de musica para servidores de Discord, con busqueda en YouTube y colas independientes.

## Preparacion en Windows

Usa Python 3.11 (instalado en este equipo). Desde la raiz del proyecto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si ya existe .env, conservalo. Completa DISCORD_TOKEN localmente, sin compartirlo.
Instala FFmpeg y agregalo a PATH, o usa FFMPEG_PATH con la ruta completa de ffmpeg.exe.
Por ejemplo: winget install --id Gyan.FFmpeg --exact.
YouTube requiere un runtime JavaScript: Node >=22 (ya instalado en este equipo) o Deno >=2.3.
Las dependencias incluyen los scripts EJS de yt-dlp.
Consulta [la guia EJS oficial](https://github.com/yt-dlp/yt-dlp/wiki/EJS).

En [Discord Developer Portal](https://discord.com/developers/applications), selecciona tu aplicacion:

1. Bot: copia o regenera el token y activa **Message Content Intent**.
2. OAuth2: invita el bot con el scope **bot**.
3. Permisos: **Ver canales**, **Enviar mensajes**, **Conectar** y **Hablar**.
4. Comprueba tambien las restricciones del canal de texto y del canal de voz.

No se requiere permiso de administrador. Los comandos usan un prefijo y no requieren applications.commands.

## Variables de entorno

| Variable | Uso | Predeterminado |
| --- | --- | --- |
| DISCORD_TOKEN | Token del bot, obligatorio | Sin valor |
| COMMAND_PREFIX | Prefijo de comandos | . |
| FFMPEG_PATH | Ejecutable FFmpeg en PATH o ruta completa | ffmpeg |
| DEFAULT_VOLUME | Volumen entre 0 y 1 | 0.25 |
| YTDLP_JS_RUNTIME | node, deno o quickjs, instalado en PATH | node |
| YTDLP_COOKIES_FILE | Cookies Netscape opcionales, ruta absoluta o relativa al proyecto | Sin valor |

.env se carga desde la raiz del proyecto; las variables del proceso tienen prioridad.
Los archivos de cookies contienen credenciales: mantenlos locales y fuera de Git.
No necesitas claves de API de YouTube. Algunos videos pueden requerir cookies, estar
bloqueados por region o no permitir extraccion; el bot informa el fallo y avanza la cola.

## Ejecutar y validar

```powershell
.\.venv\Scripts\python.exe -m src.bot --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m src.bot
```

Tambien funciona python src/bot.py. --check valida configuracion local, sin iniciar
sesion ni comprobar el token contra Discord. Para probar el audio real, conecta
el bot, entra a un canal de voz y usa .play, .pause, .resume y .skip.

En PyCharm, selecciona .venv/Scripts/python.exe como interprete y src.bot como
modulo de ejecucion, con la raiz del proyecto como directorio de trabajo.

## Comandos

- .play <nombre o enlace de YouTube>: reproduce o agrega a la cola.
- .pause / .resume: pausa o continua.
- .skip: salta una sola cancion.
- .stop: vacia la cola y desconecta.
- .queue: muestra hasta 15 canciones pendientes.
- .clear: vacia pendientes sin interrumpir la cancion actual.
- .help: muestra ayuda.

Para controlar la musica debes estar en el mismo canal de voz que el bot.
Las colas se mantienen en memoria y se vacian al desconectar o reiniciar.

## Mantenimiento

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

discord.py[voice] >=2.7.1 incluye el soporte actual de voz/DAVE. yt-dlp se actualiza
con frecuencia por cambios en YouTube. requirements.lock.txt registra las versiones
verificadas en este equipo; para reproducirlas usa pip install -r requirements.lock.txt.

En este equipo se instalo FFmpeg portable en .tools/python mediante imageio-ffmpeg.
FFMPEG_PATH en .env apunta a ese ejecutable. Para reinstalarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install --target .tools/python imageio-ffmpeg==0.6.0
```

Configura FFMPEG_PATH con la ruta del ejecutable de .tools/python/imageio_ffmpeg/binaries.
