import discord
import traceback

from discord.ext import commands
from utils.essentials.functions import func

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
                return await ctx.send(embed=func.Editable_("Error!", "Uh oh.. I seem to be missing some permissions!", "Error"))
            except discord.Forbidden:
                return

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=func.Editable_("Error!", f"Woah woah {ctx.author.mention} calm down, that command is currently cooling down!", "Error"))

        elif isinstance(error, commands.CheckFailure):
            return

        elif isinstance(error, discord.Forbidden):
            try:
                return await ctx.send(embed=func.Editable_("Error!", "Uh oh.. I seem to be missing some permissions! Use `!help permissions` to see what I require!", "Error"))
            except discord.Forbidden:
                return

        elif isinstance(error, discord.HTTPException):
            return await ctx.send(embed=func.Editable_S("Error!", f"There was an error with your command! Here it is: {error}", "Error"))

        error_logging_channel = self.bot.get_channel(670076495586132000)
        await error_logging_channel.send(f"Command Error Logged\n\n{error}")

        #raise error


    @commands.Cog.listener()
    async def on_error(event_method, *args, **kwargs):
        error_logging_channel = self.bot.get_channel(670076495586132000)

        discord_message = args[0]
        if discord_message:
            await error_logging_channel.send(f'Error caused by: {discord_message}\n' \
                                        f'Error caused in channel: {discord_message.channel.name}')

        await error_logging_channel.send(f'{traceback.format_exc()}')

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
