import datetime
import discord

from discord.ext import commands
from utils.essentials import functions
from utils.essentials.functions import func

config = functions.get("utils/config.json")

class check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_owner(ctx):
        access_log = discord.utils.get(ctx.guild.text_channels, name="access-log")
        if ctx.author.id in config.owners:
            await ctx.message.delete()
            await access_log.send(embed=func.AccessLog(f"Owner access **Granted** for {ctx.author.id} (**{ctx.author.name}**)", ctx.message.content))
            return True
        else:
            await access_log.send(embed=func.AccessLog(f"Owner access **Denied** for {ctx.author.id} (**{ctx.author.name}**)", ctx.message.content))
            await ctx.send(embed=func.NoPerm(), delete_after=config.deltimer)
            return False

    async def is_admin(ctx):
        access_log = discord.utils.get(ctx.guild.text_channels, name="access-log")
        if ctx.author.id in config.owners or config.admins:
            await ctx.message.delete()
            await access_log.send(embed=func.AccessLog(f"Admin access **Granted** for {ctx.author.id} (**{ctx.author.name}**)", ctx.message.content))
            return True
        else:
            await access_log.send(embed=func.AccessLog(f"Admin access **Denied** for {ctx.author.id} (**{ctx.author.name}**)", ctx.message.content))
            await ctx.send(embed=func.NoPerm(), delete_after=config.deltimer)
            return False


def setup(bot):
    bot.add_cog(Economy(bot))
