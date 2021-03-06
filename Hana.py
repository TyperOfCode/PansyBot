import os
import discord

from discord.ext import commands

from utils import functions

config = functions.get("utils/config.json")
bot = commands.Bot(command_prefix = config.prefix, case_insensitive=True)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\nAPI Version: {discord.__version__}\n\n')
    try:
        guild = bot.get_guild(540784184470274069)
        people = format(len(guild.members), ",")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{people} people"))
    except Exception:
        return

for file in os.listdir(f"modules"):
    if file.endswith(".py"):
        bot.load_extension(f"modules.{file[:-3]}")

bot.load_extension("utils.errorhandler")
bot.run(config.token, reconnect=True)