import datetime
import discord
import aiohttp
import json

from discord.ext import commands

class Anime_Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hug(self, ctx, user : discord.User = None):
        link = await self.api_call("/img/hug")
        if ctx.channel.id != 542291426051096606:
            if user:
                if user.id != 669724238252474387:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} hugged {user.name}")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} hugged me")
                    await ctx.send(embed=embed)
                    await ctx.send(f"{ctx.author.mention} <a:malpotatoeshuggle:608280365987135501>")
            else:
                embed = discord.Embed(colour = 0xff7af8)
                embed.set_image(url=link)
                embed.set_author(name=f"{ctx.author.name} hugged themself")
                await ctx.send(embed=embed)

    @commands.command()
    async def kiss(self, ctx, user : discord.User = None):
        link = await self.api_call("/img/kiss")
        if ctx.channel != 542291426051096606:
            if user and user != ctx.author:
                if user.id != 669724238252474387:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} kissed {user.name}")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} kissed me")
                    await ctx.send(embed=embed)
                    await ctx.send(f"{ctx.author.mention} <:Kiss:674302945990410306>")
            else:
                embed = discord.Embed(colour = 0xff7af8)
                embed.set_author(name=f"{ctx.author.name} You cannot kiss yourself, silly.")
                await ctx.send(embed=embed)

    @commands.command()
    async def cuddle(self, ctx, user : discord.User = None):
        link = await self.api_call("/img/cuddle")
        if ctx.channel.id != 542291426051096606:
            if user:
                if user.id != 669724238252474387:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} cuddled {user.name}")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} cuddled me")
                    await ctx.send(embed=embed)
                    await ctx.send(f"{ctx.author.mention} <a:malCuddle:608280367451078667>")
            else:
                embed = discord.Embed(colour = 0xff7af8)
                embed.set_image(url=link)
                embed.set_author(name=f"{ctx.author.name} cuddled themself")
                await ctx.send(embed=embed)

    @commands.command()
    async def whack(self, ctx, user : discord.User = None):
        link = await self.api_call("/img/slap")
        if ctx.channel.id != 542291426051096606:
            if user:
                if user.id != 669724238252474387:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} whacked {user.name}")
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(colour = 0xff7af8)
                    embed.set_image(url=link)
                    embed.set_author(name=f"{ctx.author.name} whacked me")
                    await ctx.send(embed=embed)
                    await ctx.send(f"{ctx.author.mention} <:malkanoncry:644320461135806464>")
            else:
                embed = discord.Embed(colour = 0xff7af8)
                embed.set_image(url=link)
                embed.set_author(name=f"{ctx.author.name} whacked themself")
                await ctx.send(embed=embed)

    async def api_call(self, extension):
        search = (f"https://nekos.life/api/v2{extension}")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(search) as r:
                result = await r.json()
                link = result["url"]
                return link


def setup(bot):
    bot.add_cog(Anime_Fun(bot))
