import discord
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    async def cog_check(self, ctx):
        if len(set([y.id for y in ctx.author.roles]).intersection([542297369698369546, 611661848961351691, 542298007765516298])) > 0:
            return True
        else:
            await ctx.send("I'm sorry, you don't have permissions for that.", delete_after=5)
            return False

    @commands.group(name="rule")
    async def _rule(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Which rule would you like?\n\nEx: **p^rule** <number>", delete_after=10)

    @_rule.command(name="1")
    async def _one(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Language", color=0xfd96ff, description="The only language you're allowed to use is English, alongside common Romaji terms/phrases.\n\nE.g. Konichiwa")
        embed.set_author(name="Rule 1")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="2")
    async def _two(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Profile", color=0xe1897f, description="Don't use inappropriate nicknames, this includes blank, sexually explicit, offensive or nicknames with unusual or unreadable unicode. Same goes to profile pictures and custom status.")
        embed.set_author(name="Rule 2")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="3")
    async def _three(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Advertisement", color=0xef5efa, description="Don't Advertise for any server or any community which isn't related to MAL")
        embed.set_author(name="Rule 3")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="4")
    async def _four(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Channels", color=0x8b3e31, description="Make sure to check the pinned messages for each channel before sending messages. Don't send spoilers anywhere except for Anime, Manga and LightNovel Channels. Use bots properly.")
        embed.set_author(name="Rule 4")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="5")
    async def _five(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Spam", color=0xf1bebd, description="Don't Spam. This includes Characters, Emotes, Images, and Message spam. Don't overuse reactions, as well as any other form of spamming.")
        embed.set_author(name="Rule 5")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="6")
    async def _six(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Mentions", color=0xdb9c7e, description="Don't mention random people/roles unless you have a proper reason. You can mention Mods for support.")
        embed.set_author(name="Rule 6")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="7")
    async def _seven(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="NSFW", color=0xd3ca46, description="Any NSFW, Disturbing, Graphical, Suggestive, Hentai and Ecchi content is prohibited. As well as Lewds in all possible forms. (Speech, Images or links of any sort.)")
        embed.set_author(name="Rule 7")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="8")
    async def _eight(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Behavior", color=0xe1897f, description="Any harrassing, bullying, cursing, racism, flaming, personal attacks, hate speech or otherwise provoking acts are prohibited.")
        embed.set_author(name="Rule 8")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

    @_rule.command(name="9")
    async def _nine(self, ctx, member: discord.Member = None):
        embed = discord.Embed(title="Sensitive Topics", color=0xce90e7, description="Any discussions about Religion, politics, feminism, homosexuality and rape are prohibited. Keep topics relatable and peaceful.")
        embed.set_author(name="Rule 9")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.message.delete()
        if member is None:
            pass
        else:
            await ctx.send(member.mention, delete_after=30)
        await ctx.send(embed=embed, delete_after=30)

def setup(bot):
    bot.add_cog(Rules(bot))
