import discord
import json
from collections import namedtuple

from datetime import datetime

def get(file):
    try:
        with open(file, encoding="utf8") as data:
            return json.load(data, object_hook=lambda d: namedtuple("X", d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")

class EmbedFuncs():
    def ErrorEM(title, description, footer='Error'):
        embed = discord.Embed(
            title = title,
            description=description,
            color = 0xff1900,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=footer)
        return embed
    
    def SuccessEM(title, description, footer='Success'):
        embed = discord.Embed(
            title = title,
            description=description,
            color = 0x8cff00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=footer)
        return embed

    def noFooter(title, description, color):
        embed = discord.Embed(
            title = title,
            description=description,
            color = color,
        )
        return embed

    def NoPerm():
        embed = discord.Embed(
            title = "Access Denied",
            description = "You do not have the Authority to run this command",
            color = 0xff5900,
            timestamp=datetime.utcnow()
        )

        return embed

    def cEm(title, description, color, footer):

        embed = discord.Embed(
            title = title,
            description = description,
            color = color,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=footer)
        return embed

