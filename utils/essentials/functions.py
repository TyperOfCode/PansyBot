import os, traceback
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

    def AccessLog(title, desc):
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = 0xe1eb34,
            timestamp=datetime.datetime.utcnow()
            )
        return embed

    def SupportErr():
        embed = discord.Embed(
            title = "Access Denied",
            description = "You must be one of the following to gain access to this command\n\nDonater\nNitro Booster\nGiveaway Donator\nSupporter",
            colour = 0xe1eb34,
            timestamp=datetime.datetime.utcnow()
            )
        return embed

    def NoPerm():
        embed = discord.Embed(
            title = "Access Denied",
            description = "Insufficient Permission",
            colour = 0xd42c2c,
            timestamp=datetime.datetime.utcnow()
            )

        return embed

    def Editable(title, desc, footer):
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = 0xeb8034,
            timestamp=datetime.datetime.utcnow()
            )
        embed.set_footer(text=footer)

        return embed

    def ENoFooter(title, desc):
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = 0xeb8034
            )

        return embed

    def Editable_E(title, desc, footer):
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = 0xd42c2c,
            timestamp=datetime.datetime.utcnow()
            )
        embed.set_footer(text=footer)

        return embed

    def Editable_S(title, desc, footer):
        embed = discord.Embed(
            title = title,
            description = desc,
            colour = 0x37e666,
            timestamp=datetime.datetime.utcnow()
            )
        embed.set_footer(text=footer)

    def eErr(title, description, footer):
        embed = discord.Embed(
            title = title,
            description=description,
            colour = 0xff2424,
            timestamp=datetime.datetime.utcnow()
            )
        embed.set_footer(text=footer)
        return embed

    def log(error):
        file = open("./utils/logs/Pansy.log","a")
        file.write("[{}]: {} \n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (GMT)"), error))
        file.close()

def setup(client):
    client.add_cog(func(client))
