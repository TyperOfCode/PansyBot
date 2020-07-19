import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.DisabledCommand, discord.NotFound)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        else:
            print(error)
            return

def setup(bot):
    bot.add_cog(ErrorHandler(bot))