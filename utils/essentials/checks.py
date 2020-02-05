import datetime
import discord

from discord.ext import commands
from utils.essentials import sql
from utils.essentials import functions
from utils.essentials.functions import func

config = functions.get("utils/config.json")

class check(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_owner(ctx):
        await ctx.message.delete()
        UID = str(ctx.author.id)
        if sql.Entry_Check(UID, "id", "owners"):
            file = open("./utils/logs/Admin.log","a")
            file.write("[{}]: Owner Access Granted to {} | CMD - {}\n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (System Time)"), ctx.author.id, ctx.message.content))
            file.close()
            return True
        else:
            file = open("./utils/logs/Admin.log","a")
            file.write("[{}]: Owner Access Denied to {} | CMD - {}\n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (System Time)"), ctx.author.id, ctx.message.content))
            file.close()
            return False

    async def is_admin(ctx):
        await ctx.message.delete()
        UID = str(ctx.author.id)
        if sql.Entry_Check(UID, "id", "admins") or sql.Entry_Check(UID, "id", "owners"):
            file = open("./utils/logs/access.log","a")
            file.write("[{}]: Admin Access Granted to {} | CMD - {}\n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (System Time)"), ctx.author.id, ctx.message.content))
            file.close()
            return True
        else:
            file = open("./utils/logs/Admin.log","a")
            file.write("[{}]: Admin Access Denied to {} | CMD - {}\n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (System Time)"), ctx.author.id, ctx.message.content))
            file.close()
            return False


def setup(bot):
    bot.add_cog(Economy(bot))
