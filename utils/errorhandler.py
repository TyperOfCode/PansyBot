import discord

from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.DisabledCommand, discord.NotFound, commands.CheckFailure)

        self.errors = {

        }

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, self.ignored):
            return

        elif isinstance(error, commands.MissingPermissions):
            try:
                return await ctx.send(embed=self.Embed("Uh oh.. I seem to be missing some permissions!"))
            except discord.Forbidden:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=self.Embed(f"{ctx.author.mention}, that command is currently cooling down!"))

        elif isinstance(error, discord.Forbidden):
            try:
                return await ctx.send(embed=self.Embed("Uh oh.. I dont have permission to do that"))
            except discord.Forbidden:
                pass

        elif isinstance(error, discord.HTTPException):
           return await ctx.send(embed=self.Embed(f"There was an error with your command, please notify Stig#1337 of this! Here it is: {error}"))

        if ctx.command and error:
            await self.SendHook(str(error), ctx.command)

    @commands.Cog.listener()
    async def on_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, self.ignored):
            return

        if ctx.command and error:
            await self.SendHook(str(error), ctx.command)

    async def SendHook(self, desc, command=None):
        webhook = await self.bot.fetch_webhook(726120911329034332)

        embed = discord.Embed(
            description=desc,
            colour=0xebc634,
        )

        if command:
            embed.set_author(name=f"Source (Command): {command}")

        embeds = []
        embeds.append(embed)
        await webhook.send(embeds=embeds)
        embeds.clear()

    def Embed(self, error):
        embed = discord.Embed(
            description=error,
            colour=0xebc634,
        )

        return embed

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
