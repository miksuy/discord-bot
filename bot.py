from dotenv import load_dotenv
import random
import discord
import requests
from discord.ext import commands
from googleapiclient.discovery import build
import os

load_dotenv()

# Retrieve sensitive data from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
YTAPI = os.getenv("YT_API_KEY")
IMGAPI = os.getenv("IMG_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CX_KEY")
TENORAPI = os.getenv("TENOR_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', help_command=None, intents=intents)
youtube = build('youtube', 'v3', developerKey=YTAPI)

@bot.command()
async def help(ctx):
    commands_list = "\n".join([
        "\n"
        ".img <searchword> - Search Google Images with a searchword\n"
        "\n"
        ".yt <searchword> - Search Youtube with a searchword\n"
        "\n"
        ".short <searchword> - Search a YT short with a searchword\n"
        "\n"
        ".tenor <searchword> - Search a GIF\n"
        "\n"
        ".about"
        ])
    await ctx.send(f"Available commands:\n{commands_list}")

@bot.command()
async def yt(ctx, *, searchword: str):
    try:
        request = youtube.search().list(
            part="snippet",
            q=searchword,
            type="video",
            maxResults=10
        )
        response = request.execute()

        video = random.choice(response["items"])
        video_id = video["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        await ctx.send(video_url)
    except Exception as e:
        await ctx.send(f"Error occurred: {str(e)}")

@bot.command()
async def img(ctx, *, searchword: str):
    try:
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": IMGAPI,
            "cx": GOOGLE_CSE_ID,
            "q": searchword,
            "searchType": "image",
            "num": 10
        }

        response = requests.get(search_url, params=params)
        data = response.json()

        if "items" in data:
            image = random.choice(data["items"])
            image_url = image["link"]

            embed = discord.Embed(
                title=f"Google Image Search: {searchword}",
                color=discord.Color.blue()
            )
            embed.set_image(url=image_url)

            await ctx.send(embed=embed)
        else:
            await ctx.send("⚠️ No images found! Try a different search.")
    except Exception as e:
        await ctx.send(f"Error occurred: {str(e)}")

@bot.command()
async def short(ctx, *, searchword: str):
    try:
        request = youtube.search().list(
            part="snippet",
            q=searchword + " short",
            type="video",
            videoDuration="short",
            maxResults=10
        )
        response = request.execute()

        video = random.choice(response["items"])
        video_id = video["id"]["videoId"]
        video_url = f"https://www.youtube.com/shorts/{video_id}"

        await ctx.send(video_url)
    except Exception as e:
        await ctx.send(f"Error occurred: {str(e)}")

@bot.command()
async def about(ctx):
    await ctx.send(f"https://github.com/miksuy/discord-bot")
    
@bot.command()
async def tenor(ctx, *, searchword: str):
    url = f"https://api.tenor.com/v1/search?q={searchword}&key={TENORAPI}&limit=5"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        if 'results' in data and len(data['results']) > 0:
            gifs = data['results']
            
            random_gif = random.choice(gifs)
            
            gif_url = random_gif['media'][0]['gif']['url']
            
            await ctx.send(gif_url)
        else:
            await ctx.send(f"Sorry, I couldn't find any GIFs for '{searchword}'.")
    else:
        await ctx.send(f"Failed to fetch data from Tenor. Status code: {response.status_code}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "siel" in message.content.lower():
        await message.channel.send("siel")

    await bot.process_commands(message)

bot.run(TOKEN)
