from dotenv import load_dotenv
import random
import discord
import requests
from discord.ext import commands
from googleapiclient.discovery import build
import os
import urllib.parse
import aiohttp

load_dotenv()

# Retrieve sensitive data from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
YTAPI = os.getenv("YT_API_KEY")
IMGAPI = os.getenv("IMG_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CX_KEY")
TENORAPI = os.getenv("TENOR_API_KEY")

CLIENT_KEY = "discordbot"

UPDATE_MESSAGE = "NONI botti on päivitetty"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', help_command=None, intents=intents)
youtube = build('youtube', 'v3', developerKey=YTAPI)

yt_search_history = {}  # History for YouTube searches
img_search_history = {}  # History for image searches

@bot.event
async def on_ready():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send(UPDATE_MESSAGE)
            except discord.Forbidden:  
                print(f"Cannot send message in {channel.name} ({guild.name})")
            except discord.HTTPException as e:
                print(f"Failed to send message in {channel.name} ({guild.name}): {e}")

    print("Message sent to all channels.")

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
        user_id = ctx.author.id
        
        if user_id not in yt_search_history or yt_search_history[user_id]["query"] != searchword:
            request = youtube.search().list(
                part="snippet",
                q=searchword,
                type="video",
                maxResults=5
            )
            response = request.execute()
            yt_search_history[user_id] = {
                "query": searchword,
                "results": response["items"],
                "index": 0,
                "count": 1  # Start count from 1
            }

        index = yt_search_history[user_id]["index"]
        videos = yt_search_history[user_id]["results"]
        count = yt_search_history[user_id]["count"]

        if index >= len(videos):
            await ctx.send("No more results available.")
            return

        video = videos[index]
        video_id = video["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # Update the count and index
        yt_search_history[user_id]["index"] += 1
        yt_search_history[user_id]["count"] = count + 1  # Increment count by 1

        if yt_search_history[user_id]["count"] >= 5:
            del yt_search_history[user_id]  # Reset history after 5 searches

        await ctx.send(video_url)
    except Exception as e:
        await ctx.send(f"Error occurred: {str(e)}")

@bot.command()
async def img(ctx, *, searchword: str):
    try:
        user_id = ctx.author.id

        if user_id not in img_search_history or img_search_history[user_id]["query"] != searchword:
            # Make a request to Google Custom Search API to fetch images
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": searchword,
                "cx": GOOGLE_CSE_ID,
                "key": IMGAPI,
                "searchType": "image",
                "num": 5  # Fetch up to 5 images
            }
            response = requests.get(url, params=params)
            data = response.json()

            images = data.get("items", [])
            if not images:
                await ctx.send("No images found.")
                return

            img_search_history[user_id] = {
                "query": searchword,
                "results": images,
                "index": 0,
                "count": 1  # Start count from 1
            }

        index = img_search_history[user_id]["index"]
        images = img_search_history[user_id]["results"]
        count = img_search_history[user_id]["count"]

        if index >= len(images):
            await ctx.send("No more results available.")
            return

        image_url = images[index]["link"]

        # Update history
        img_search_history[user_id]["index"] += 1
        img_search_history[user_id]["count"] = count + 1

        if img_search_history[user_id]["count"] >= 5:
            del img_search_history[user_id]  # Reset after 5 searches

        await ctx.send(image_url)
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
            maxResults=3
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
    searchword_encoded = urllib.parse.quote(searchword)
    url = f"https://tenor.googleapis.com/v2/search?q={searchword_encoded}&key={TENORAPI}&client_key={CLIENT_KEY}&limit=5"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()

                if response.status == 200 and 'results' in data and len(data['results']) > 0:
                    random_gif = random.choice(data['results'])

                    if 'media_formats' in random_gif and 'gif' in random_gif['media_formats']:
                        gif_url = random_gif['media_formats']['gif']['url']
                        await ctx.send(gif_url)
                    else:
                        await ctx.send("Sorry, I couldn't find a valid GIF for this search.")
                else:
                    await ctx.send(f"Sorry, I couldn't find any GIFs for '{searchword}'.")
    
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "siel" in message.content.lower():
        await message.channel.send("siel")

    await bot.process_commands(message)

bot.run(TOKEN)
