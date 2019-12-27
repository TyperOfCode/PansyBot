import discord
from datetime import datetime
from discord.ext import commands

class Development(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def _test(self, ctx):
        await ctx.send("tested")

    @commands.command(name="summon")
    async def _summon(self, ctx):
        channel = ctx.member.voice.channel
        await channel.connect()

    @commands.command(name="leave")
    async def _leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(name="help")
    async def _help(self, ctx):
        await ctx.send("Test.")

    @commands.command(name="ping")
    async def _ping(self, ctx):
        ping = str(self.bot.latency)[:5]
        msg = await ctx.send(f":ping_pong: Pong. ({ping} seconds)")

    @commands.command(name="clear")
    @commands.is_owner()
    async def _clear(self, ctx, number: int = None, member: discord.Member = None):
        if number is None:
            number = 10
        if member is None:
            check = None
        elif member is not None:
            def is_member(m):
                return m.author == member
            check = is_member
        await ctx.channel.purge(limit=number, check=check)

def setup(bot):
    bot.add_cog(Development(bot))
