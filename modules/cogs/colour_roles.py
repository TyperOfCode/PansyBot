import datetime
import discord
import mysql.connector

from discord.ext import commands

from utils.essentials.checks import check

class Colour_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=["colour"])
    @commands.check(check.is_supporter)
    async def color(self, ctx, number:int=None):
        user = ctx.author
        rolelist = [655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775, 659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740, 669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237]
        channel1 = discord.utils.get(ctx.guild.text_channels, id=548932204672319499)
        channel2 = discord.utils.get(ctx.guild.text_channels, id=622906588562456576)
        if ctx.channel is channel1 or ctx.channel is channel2:
            if number is not None and number >= 1 and number <= 15:
                for roles in ctx.author.roles:
                    if roles.id in rolelist:
                        role = discord.utils.get(ctx.guild.roles, id=roles.id)
                        await user.remove_roles(role)
                roleid = rolelist[number - 1]
                role = discord.utils.get(ctx.guild.roles, id=roleid)
                await user.add_roles(role)
                color = str(role.color)
                colorembed = int(color[1:], 16)
                embed = discord.Embed(title=f"**{ctx.author.name}** obtained color {number}!", colour=colorembed, timestamp=datetime.datetime.utcfromtimestamp(1579828506))
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed = discord.Embed(title="Type !color <number> with the number you want", colour=discord.Colour(0xd42c2c), timestamp=datetime.datetime.utcfromtimestamp(1579828506))
                embed.set_image(url="https://i.imgur.com/H8Wk8wG.png")
                await ctx.send(embed=embed, delete_after=30)
        else:
            await channel1.send(f"{ctx.author.mention} Retry your command here", delete_after=30)
            await channel2.send(f"{ctx.author.mention} Or here", delete_after=30)

    @color.group(invoke_without_command=True)
    @commands.check(check.is_supporter)
    async def clear(self, ctx):
        user = ctx.author
        rolelist = [655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775, 659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740, 669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237]
        channel1 = discord.utils.get(ctx.guild.text_channels, id=548932204672319499)
        channel2 = discord.utils.get(ctx.guild.text_channels, id=622906588562456576)
        if ctx.channel is channel1 or ctx.channel is channel2:
            for roles in ctx.author.roles:
                if roles.id in rolelist:
                    role = discord.utils.get(ctx.guild.roles, id=roles.id)
                    await user.remove_roles(role)
                    embed = discord.Embed(title=f"**{ctx.author.name}** Cleared their color roles!", colour=colorembed, timestamp=datetime.datetime.utcfromtimestamp(1579828506))
            await ctx.send(embed=embed, delete_after=10)
        else:
            await channel1.send(f"{ctx.author.mention} Retry your command here", delete_after=30)
            await channel2.send(f"{ctx.author.mention} Or here", delete_after=30)

    @color.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def add(self, ctx, roleid : int = None):
        if roleid:
            role = discord.utils.get(ctx.guild.roles, id=roleid)
            if role:
                if self.add_support_role(roleid):
                    await ctx.send(embed=func.Editable(f"Added {roleid} to the Database", "", "Colour Roles"), delete_after=config.deltimer)
                else:
                    await ctx.send(embed=func.Editable_E("That role is not in the database", "", "Colour Roles"), delete_after=config.deltimer)
            else:
                await ctx.send(embed=func.Editable_E("I couldnt find that role", "", "Colour Roles"), delete_after=config.deltimer)
        else:
            await ctx.send(embed=func.Editable_E(f"Please provide me with a role name", "", "Colour Roles"), delete_after=config.deltimer)

    @color.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def remove(self, ctx, roleid : int = None):
        if roleid:
            role = discord.utils.get(ctx.guild.roles, id=roleid)
            if role:
                if self.remove_support_role(roleid):
                    await ctx.send(embed=func.Editable(f"Removed {roleid} from the Database", "", "Colour Roles"), delete_after=config.deltimer)
                else:
                    await ctx.send(embed=func.Editable_E("That user already has access rights", "", "Colour Roles"), delete_after=config.deltimer)
            else:
                await ctx.send(embed=func.Editable_E("I couldnt find that role", "", "Colour Roles"), delete_after=config.deltimer)
        else:
            await ctx.send(embed=func.Editable_E(f"Please provide me with a role name", "", "Colour Roles"), delete_after=config.deltimer)

    @color.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def list(self, ctx):
        roles = self.get_roles()
        await ctx.send(roles)

    def remove_support_role(self, roleid):
        if self.already_support_role(roleid):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"DELETE from `colour_roles` WHERE roleid = '{roleid}'")
            mydb.commit()
            return True
        else:
            return False

    def add_support_role(self, roleid):
        if not self.already_support_role(roleid):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"INSERT into `colour_roles` VALUES ('{roleid}')")
            mydb.commit()
            return True
        else:
            return False

    def already_support_role(self, roleid):
        if sql.Entry_Check(str(roleid), "roleid", "colour_roles"):
            return True

    def get_roles(self):
        list = []
        mydb = sql.createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT roleid from colour_roles")
        for Row in cur:
            list.append(Row)

        return list


def setup(bot):
    bot.add_cog(Colour_Roles(bot))
