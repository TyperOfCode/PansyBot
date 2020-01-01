import discord
import asyncio
import datetime
from datetime import datetime
from discord.ext import commands
from discord.utils import get
import sqlite3
import dbfunctions

import os
import psutil

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def modperms(ctx):
        if "mod" in [y.name.lower() for y in ctx.author.roles]:
            return True
        elif "developer" in [y.name.lower() for y in ctx.author.roles]:
            return True
        elif "admin" in [y.name.lower() for y in ctx.author.roles]:
            return True
        else:
            return False

    @commands.group(name="rule")
    async def _rule(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.author.send("Which rule would you like?\n\nEx: **p^rule** <number>")

    @_rule.command(name="1")
    async def _one(self, ctx):
        embed = discord.Embed(title="Language", color=0xff00ff, description="The only language you're allowed to use is English, alongside common Romaji terms/phrases.\n\nE.g. Konichiwa")
        embed.set_author(name="Rule 1")
        enbed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

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

    @commands.command(name="apps")
    async def _apps(self, ctx):
        numApps = dbfunctions.dbselect("data.db", "SELECT count(*) FROM applied", ())
        await ctx.send(f"We have received {format(numApps, ',')} applications")

    @commands.command(name="test")
    @commands.is_owner()
    async def _test(self, ctx):
        await ctx.send(dbfunctions.dbselect("data.db", "SELECT prefix FROM information", ()))

    @commands.command(name="ram")
    @commands.is_owner()
    async def _ram(self, ctx):
        process = psutil.Process(os.getpid())
        ramBytes = process.memory_info().rss
        ramKilo = round(ramBytes/1024, 2)
        ramMega = round(ramKilo/1024, 2)
        ramGiga = round(ramMega/1024, 2)
        embed = discord.Embed(title=f"RAM Usage | {self.bot.user.name}#{self.bot.user.discriminator}", color=0x00ffff, description=f"Bytes: {ramBytes}\nKilobytes: {ramKilo}\nMegabytes: {ramMega}\nGigabytes: {ramGiga}")
        await ctx.send(embed=embed)

    @commands.command(name="server-info")
    @commands.check(modperms)
    async def _sinfo(self, ctx):
        bots = 0
        humans = 0
        online = 0
        for member in ctx.guild.members:
            if member.bot == True:
                bots+=1
            elif member.bot == False:
                humans+=1
            if member.status == "online":
                online+=1
        embed = discord.Embed()
        embed.add_field(name="Owner", value=f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}")
        #embed.add_field(name="VIP Perks", value="???")
        embed.add_field(name="Server Created", value=printTime(ctx.guild.created_at))
        embed.add_field(name="Total Channels", value=f"{len(ctx.guild.channels)} total channels:\n{len(ctx.guild.categories)} categories\n{len(ctx.guild.text_channels)} text, {len(ctx.guild.voice_channels)} voice")
        embed.add_field(name="Total Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Boost Level", value=ctx.guild.premium_tier)
        embed.add_field(name="Members Boosting", value=ctx.guild.premium_subscription_count)
        embed.add_field(name="Members", value=f"{format(len(ctx.guild.members), ',')} total,\n{online} online\n{bots} bots, {humans} humans")
        embed.set_footer(text=f"Server Name: {ctx.guild.name} | Server ID: {ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command(name="members")
    @commands.check(modperms)
    async def _members(self, ctx):
        malstaff = self.bot.get_guild(601673823921635336)
        malserver = self.bot.get_guild(540784184470274069)
        staffmembers = format(len(malstaff.members), ',')
        malmembers = format(len(malserver.members), ',')
        embed = discord.Embed(color=0x00ffff)
        embed.add_field(name=malserver, value=malmembers)
        embed.add_field(name=malstaff, value=staffmembers, inline=False)
        embed.add_field(name="Total Members:", value=format(len(malstaff.members)+len(malserver.members), ","), inline=False)
        embed.set_footer(text=f"As of: {timestamp()} GMT")
        embed.set_thumbnail(url=str(malserver.icon_url))
        await ctx.send(embed=embed)

    @commands.command(name="dm")
    @commands.check(modperms)
    async def _dm(self, ctx, id, *, msg: str):
        if id.startswith("<@"):
            id = id[3:-1]
        id = int(id)
        guild = ctx.guild
        user = guild.get_member(id)
        await user.send(msg)
        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="echo")
    @commands.is_owner()
    async def _echo(self, ctx, guild: int, channel: int, *, msg: str):
        server = self.bot.get_guild(guild)
        text = server.get_channel(channel)
        await text.send(msg)

    @commands.group(name="bot-edit")
    async def _botedit(self, ctx):
        """| Commands that are related to editing the bot user."""

    @_botedit.command(name="avatar")
    async def _avatar(self, ctx):
        """| Changes the bot's avatar."""
        msg = await ctx.send("Trying to change avatar...")
        with open("C:\\Users\\BMan12321\\Desktop\\DISCORDBOTS\\Pansy-Chan\\cogs\\avatar.png", "rb") as image:
          f = image.read()
        await self.bot.user.edit(avatar=f)
        await asyncio.sleep(1)
        await msg.edit(content="Finished!", delete_after=3)

    @_botedit.command(name="username")
    async def _username(self, ctx, *, username: str):
        """| Changes the bot's username."""
        await self.bot.user.edit(username=username)

def printTime(datetime):
    return datetime.strftime("%B %d, %Y | %I:%M:%S%p")

def timestamp():
    now = datetime.now()
    current_time = now.strftime("%B %d, %Y | %I:%M:%S%p")
    return current_time

def setup(bot):
    bot.add_cog(Admin(bot))
