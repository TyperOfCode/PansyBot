import datetime
import discord
import json

from discord.ext import commands
from collections import namedtuple

def get(file):
    try:
        with open(file, encoding="utf8") as data:
            return json.load(data, object_hook=lambda d: namedtuple("X", d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

class func(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def NoPerm(self):
        embed = discord.Embed(
            title = "Access Denied",
            description = "Insufficient Permission",
            colour = 0xebc634,
            )
        return embed

    def Embed(desc : str):
        embed = discord.Embed(
            description = desc,
            colour = 0xcf53ee,
            )
        return embed

    def ErrorEmbed(Error: str):
        embed = discord.Embed(
            description=Error,
            colour = 0xebc634,
            )
        return embed

def setup(client):
    client.add_cog(func(client))
