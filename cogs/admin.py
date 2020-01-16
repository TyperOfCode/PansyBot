import discord
import asyncio
import datetime
import secrets
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

    def helperPlus(ctx):
        allowed = [652732584299593759, 600837848169578516, 542297369698369546, 611661848961351691, 542298007765516298]
        if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
            return True
        return False

    def modPlus(ctx):
        allowed = [542297369698369546, 611661848961351691, 542298007765516298]
        if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
            return True
        return False

    def adminPlus(ctx):
        allowed = [611661848961351691, 542297369698369546]
        if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
            return True
        return False

    @commands.command(name="gay")
    async def _gay(self, ctx):
        if ctx.author.id == 319395686699499520:
            await ctx.send("No u")

    @commands.command(name="embed")
    async def _embed(self, ctx, channel: discord.TextChannel = None):
        msg = await ctx.channel.fetch_message(663562205534617601)
        embed = discord.Embed(title="**__Donations__**", color=0x00ff00, description="<a:MalStars:612406936435949569>We appreciate your kindness to support us!\n<a:MalStars:612406936435949569>We promise to use your donations for the improvements of the server.\n\n<a:malStar1:614619624268365829> All donors can have:\n<a:MalGift:637197769534078987> **Color roles.**\n<a:MalGift:637197769534078987> **Nickname Change.**\n<a:MalGift:637197769534078987> **VIPs have access to VIP channels.**\n\n<a:malHeartW:608278535613841408> We can't offer you what equals the amount of love and support you provide us, but we would love to hear out your wishes and any perks you'd like to have for donating! <a:malHeartW:608278535613841408>\n\n\n**[Click here to donate!](https://donatebot.io/checkout/540784184470274069)**")
        await msg.edit(embed=embed)

    @commands.command(name="db")
    @commands.is_owner()
    async def _db(self, ctx):
        ids = dbfunctions.dbselectmore("data.db", "SELECT ID FROM shiftReminders", ())
        members = []
        for id in ids:
            print(f"member = ctx.guild.get_member({id})")
            member = ctx.guild.get_member(id)
            print(f"members.append({member})")
            members.append(member)
        for member in members:
            if 652732584299593759 in [y.id for y in member.roles]:
                dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (5, member.id,))
            elif 600837848169578516 in [y.id for y in member.roles]:
                dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (18, member.id,))
            elif 542298007765516298 in [y.id for y in member.roles]:
                dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (12, member.id,))
            print(member)
        await ctx.send("Done", delete_after=3)

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
    @commands.check(modPlus)
    async def _dm(self, ctx, member: discord.Member, *, msg: str):
        await member.send(msg)
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
