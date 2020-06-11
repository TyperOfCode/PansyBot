import discord
import datetime

from discord.ext import commands
from utils.functions import func

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.DisabledCommand, discord.NotFound)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.MissingPermissions):
            try:
                return await ctx.send(embed=func.Editable_E("Error!", "Uh oh.. I seem to be missing some permissions!", "Error"))
            except discord.Forbidden:
                return

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=func.Editable_E("Error!", f"Woah woah {ctx.author.mention} calm down, that command is currently cooling down!", "Error"))

        elif isinstance(error, commands.CheckFailure):
            return

        elif isinstance(error, discord.Forbidden):
            try:
                return await ctx.send(embed=func.Editable_E("Error!", "Uh oh.. I seem to be missing some permissions! Use `!help permissions` to see what I require!", "Error"))
            except discord.Forbidden:
                return

        elif isinstance(error, discord.HTTPException):
            return await ctx.send(embed=func.Editable_E("Error!", f"There was an error with your command! Here it is: {error}", "Error"))

        file = open("./utils/logs/Error.log","a")
        file.write("[{}]: Command Error Logged {}\n".format(datetime.datetime.utcnow().strftime("%d/%m/%Y at %H:%M:%S (System Time)"), error))
        file.close()
        print("An error has been logged")

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
