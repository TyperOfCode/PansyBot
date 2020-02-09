import os, traceback
import discord
import json

from utils.essentials import functions
from utils.essentials.functions import func
from discord.ext import commands

config = functions.get("utils/config.json")
bot = commands.Bot(command_prefix = config.prefix)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'\nLogged in as: {bot.user.name}\nAPI Version: {discord.__version__}')
    guild = bot.get_guild(540784184470274069)
    people = format(len(guild.members), ",")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people"))

for file in os.listdir("modules"):
    if file.endswith(".py"):
        name = file[:-3]
        try:
            bot.load_extension(f"modules.{name}")
            print(f"{name} Module Loaded")
        except Exception as error:
            traceback.print_exc()

bot.load_extension("utils.essentials.errorhandler")
bot.run(config.token, reconnect=True)
