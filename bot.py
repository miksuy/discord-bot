import discord
from discord.ext import commands

# Set up the bot with a command prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def help(ctx):
    commands_list = "\n".join(["!help - Lists available commands"])
    await ctx.send(f"Available commands:\n{commands_list}")

# Run the bot (replace 'YOUR_BOT_TOKEN' with your actual bot token)
bot.run('YOUR_BOT_TOKEN')
