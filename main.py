import discord
import asyncio
from discord.ext import commands
import secrets
import random
import datetime
import sqlite3
import dbfunctions

def get_prefix(bot, message):
    return dbfunctions.dbselect("data.db", "SELECT prefix FROM information WHERE server=?", (601673823921635336,))

bot = commands.Bot(command_prefix=get_prefix, owner_id=144051124272365569)
bot.remove_command("help")
startup_extensions = ["cogs.admin", "cogs.bkgrnd", "cogs.events", "dbfunctions"]

for extension in startup_extensions:
    try:
        bot.load_extension(extension)
    except Exception as e:
        exc = f"{type(e).__name__}: {e}"
        print(f"Failed to load extension {extension}\n{exc}")

@bot.event
async def on_ready():
    print("Username: {0.name}#{0.discriminator}\nID: {0.id}".format(bot.user))
    print(f"Using discord.py v{discord.__version__}")
    guild = bot.get_guild(540784184470274069)
    people = format(len(guild.members), ",")
    watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
    await bot.change_presence(activity=watch)

@bot.command(name="load")
@commands.is_owner()
async def _load(ctx, extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send(f"```py\n{type(e).__name__}: {str(e)}\n```")
        return
    msg = await ctx.send(f"`{extension_name}` loaded.", delete_after=2)
    if ctx.guild is None:
        pass
    else:
        await ctx.message.delete()

@bot.command(name="unload")
@commands.is_owner()
async def _unload(ctx, extension_name: str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    msg = await ctx.send(f"`{extension_name}` unloaded.", delete_after=2)
    if ctx.guild is None:
        pass
    else:
        await ctx.message.delete()

@bot.command(name="reload")
@commands.is_owner()
async def _reload(ctx, extension_name: str):
    """Reloads an extension."""
    bot.unload_extension(extension_name)
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send(f"```py\n{type(e).__name__}: {str(e)}```")
        return
    msg = await ctx.send(f"`{extension_name}` reloaded.", delete_after=2)
    if ctx.guild is None:
        pass
    else:
        await ctx.message.delete()

bot.run(secrets.token)
