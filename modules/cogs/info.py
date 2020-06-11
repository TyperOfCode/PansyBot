import datetime
import discord

from discord import Spotify
from discord.ext import commands

from utils.essentials.functions import func

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sinfo(self, ctx):
        embed = discord.Embed(
            colour = 0xeb8034,
            timestamp=datetime.datetime.utcnow()
            )
        embed.add_field(name="Creation Date", value=ctx.guild.created_at.strftime("%d/%m/%Y at %H:%M:%S"), inline=False)
        embed.add_field(name="Owner", value=ctx.guild.owner.name, inline=True)
        embed.add_field(name="Region", value=ctx.guild.region, inline=True)
        embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Users", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="AFK Channel", value=ctx.guild.afk_channel, inline=True)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(icon_url=ctx.guild.icon_url, text=f"{ctx.guild.name} - {ctx.guild.id}")
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def info(self, ctx):
        activeServers = self.bot.guilds
        sum = 0
        for s in activeServers:
            sum += len(s.members)
        embed=discord.Embed(
            title=f"Info about {self.bot.user.name}",
            description="Multifunctional Bot, constantly recieving updates.",
            colour = 0xeb8034
            )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Github", value="[Github](https://github.com/TyperOfCode/PansyBot)", inline=True)
        embed.add_field(name="Need help?", value="PM Me <@!439327545557778433>", inline=True)
        embed.add_field(name="Currently Serving", value=f"{sum} Members", inline=True)
        embed.set_footer(text="{} - Providing Discord since {}".format(self.bot.user.name, self.bot.user.created_at.strftime("%d/%m/%Y")))
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
            pass
        if user.voice is None:
            channel = "Not in a voice channel"
        else:
            channel = user.voice.channel.name
        if user.activities:
            for activity in user.activities:
                if isinstance(activity, Spotify):
                    title = f"Listening to {activity.title} by {activity.artist}"
                else:
                    title = f"Playing {activity.name}"
        else:
            title = "Doing Nothing"
        embed = discord.Embed(
            title = title,
            colour = 0xeb8034,
            timestamp = datetime.datetime.utcnow()
            )
        embed.set_author(name = self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text=f"{user.name}'s User Info", icon_url=user.avatar_url)
        embed.add_field(name="Joined At", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Status", value=user.status, inline=True)
        embed.add_field(name="Role Count", value=len(user.roles), inline=True)
        embed.add_field(name="Nickname", value=user.nick, inline=True)
        embed.add_field(name="Voice", value=channel, inline=True)
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def spotify(self, ctx, user : discord.Member=None):
        await ctx.message.delete()
        if user == None:
            user = ctx.author
            pass
        if user.activities:
            for activity in user.activities:
                if isinstance(activity, Spotify):
                    embed = discord.Embed(
                        description = f"Listening to {activity.title}",
                        colour = 0xeb8034,
                        )
                    embed.set_thumbnail(url=activity.album_cover_url)
                    embed.add_field(name="Artist", value=activity.artist)
                    embed.add_field(name="Album", value=activity.album)

                    embed.set_footer(text="Song Started at {}".format(activity.created_at.strftime("%H:%M:%S")))
                    await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(Info(bot))
