import discord
from discord.ext import commands
from googleapiclient.discovery import build

# type your bot token below
TOKEN = "YOUR_BOT_TOKEN"
#type your youtube api key below
YTAPI = "YOUR_YOUTUBE_API_KEY"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
youtube = build('youtube', 'v3', developerKey=YTAPI)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def help(ctx):
    commands_list = "\n".join(["!help - Lists available commands"])
    await ctx.send(f"Available commands:\n{commands_list}")

@bot.command()
async def yt(ctx, *, searchword: str):
    request = youtube.search().list(
        part="snippet",
        q=searchword,
        type="video",
        maxResults=1
    )
    response = request.execute()

    video_id = response['items'][0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    await ctx.send({video_url})

bot.run(TOKEN)