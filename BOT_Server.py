import discord
from discord.ext import commands
import os
import random
import string
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

TOKEN = "MTQ5Nzc4MTM1Nzk0NDc2NjU0NA.G25KNV.BrZFKR2Yl2SFRNGRh4hCll3hU1PvZtH10RrLJI"
YOUTUBE_API_KEY = "AIzaSyCkN-Cut-ROKZ-THO41jMq_wO6GG8ZOhEs"
VIDEO_ID = "hCdHlscTNTA"
CARGO_ID = 1497787371050111117

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # necessário pros comandos funcionarem

bot = commands.Bot(command_prefix="!", intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# canal permitido
CANAL_VERIFICACAO = 1497790654351409192

# armazenar códigos temporários
codigos = {}

def gerar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


@bot.event
async def on_ready():
    print("Logado como " + bot.user.name)


@bot.command()
async def verificar(ctx):
    if ctx.channel.id != CANAL_VERIFICACAO:
        return

    codigo = gerar_codigo()
    codigos[ctx.author.id] = codigo

    await ctx.send(
        ctx.author.mention + " comenta isso no vídeo:\n\n"
        "`" + codigo + "`\n\n"
        "Link: https://www.youtube.com/watch?v=" + VIDEO_ID + "\n\n"
        "Depois digita !confirmar"
    )


@bot.command()
async def confirmar(ctx):
    if ctx.channel.id != CANAL_VERIFICACAO:
        return

    if ctx.author.id not in codigos:
        await ctx.send("Você não iniciou verificação. Use !verificar")
        return

    codigo = codigos[ctx.author.id]

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=VIDEO_ID,
        maxResults=100
    )

    response = request.execute()

    achou = False

    for item in response["items"]:
        comentario = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        if codigo in comentario:
            achou = True
            break

    if achou:
        cargo = ctx.guild.get_role(CARGO_ID)
        await ctx.author.add_roles(cargo)

        await ctx.send("✅ Verificado! Cargo entregue.")

        del codigos[ctx.author.id]
    else:
        await ctx.send("❌ Não achei seu comentário ainda. Tenta de novo.")
        

bot.run(TOKEN)