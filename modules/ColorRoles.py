import datetime
import discord

from discord.ext import commands, tasks

from utils import sql
from utils.functions import func

class Colour_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.spam_id = 622906588562456576 # Spam Channel
        self.spam = None

        self.color_roles = [
            655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775,
            659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740,
            669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237
            ]

        self.removeRoles.start()


    @tasks.loop(hours=1)
    async def removeRoles(self):
        users = []

        guild = self.bot.get_guild(540784184470274069)
        supporter_roles = self.get_roles()

        for color in self.color_roles:
            role = discord.utils.get(guild.roles, id=color)

            for member in role.members:
                users.append(member.id)

        for id in users:
            usern = guild.get_member(id)

            for i in supporter_roles:
                if i[0] in usern.roles:
                    users.remove(usern)

            for roleid in self.color_roles:
                role = discord.utils.get(guild.roles, id=roleid)
                if role in usern.roles:
                    await usern.remove_roles(role)


    @commands.group(invoke_without_command=True, aliases=["colour"])
    async def color(self, ctx, number:int=None):

        if not self.spam:
            self.SetVals(ctx.guild)

        if not await self.is_supporter(ctx.author):
            return await func.NoPerm()

        if ctx.channel.id != self.spam_id:
            return await self.spam.send(f"{ctx.author.mention} Try here", delete_after=30)

        if not number or number < 1 or number > 15:
            embed = discord.Embed(title=f"Type {ctx.prefix}color <number> with the number you want",
                                  colour=discord.Colour(0xd42c2c),
                                  timestamp=datetime.datetime.utcfromtimestamp(1579828506))
            embed.set_image(url="https://i.imgur.com/H8Wk8wG.png")
            return await ctx.send(embed=embed)

        for roles in ctx.author.roles:
            if roles.id in self.color_roles:
                role = discord.utils.get(ctx.guild.roles, id=roles.id)
                await ctx.author.remove_roles(role)

        roleid = self.color_roles[number - 1]
        role = discord.utils.get(ctx.guild.roles, id=roleid)
        await ctx.author.add_roles(role)

        embed = discord.Embed(title=f"Role Added",
                              description=f"**{ctx.author.name}** obtained color {number}!",
                              colour=discord.Colour(0xcf53ee))
        embed.set_footer(text=f"Use `{ctx.prefix}colour clear` to remove your colour")
        await ctx.send(embed=embed)

    @color.group(invoke_without_command=True)
    async def clear(self, ctx):

        if not self.spam:
            self.SetVals(ctx.guild)

        if not await self.is_supporter(ctx.author):
            return

        if ctx.channel.id != self.spam_id:
            return await self.spam.send(f"{ctx.author.mention} Try here", delete_after=30)

        for roles in ctx.author.roles:
            if roles.id in self.color_roles:
                role = discord.utils.get(ctx.guild.roles, id=roles.id)
                await ctx.author.remove_roles(role)

        embed = func.Embed(f"**{ctx.author.name}** Cleared their color roles!")
        await ctx.send(embed=embed)

    # Adding Supporter Roles

    @color.group(invoke_without_command=True)
    async def add(self, ctx, roleid : int = None):
        if not roleid:
            return await ctx.send(embed=func.ErrorEmbed(f"Please provide me with a role ID"))

        role = discord.utils.get(ctx.guild.roles, id=roleid)

        if not role:
            return await ctx.send(embed=func.ErrorEmbed("I couldnt find that role"))

        if self.add_support_role(roleid):
            await ctx.send(embed=func.Embed(f"Added {role.name} to the database"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That role is already in the database"))


    @color.group(invoke_without_command=True)
    async def remove(self, ctx, roleid : int = None):
        if not roleid:
            return await ctx.send(embed=func.ErrorEmbed(f"Please provide me with a role ID"))

        role = discord.utils.get(ctx.guild.roles, id=roleid)

        if not role:
            return await ctx.send(embed=func.ErrorEmbed("I couldnt find that role"))

        if self.remove_support_role(roleid):
            await ctx.send(embed=func.Embed(f"Removed {role.name} from the database"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That role is not in the database"))


    @color.group(invoke_without_command=True)
    async def list(self, ctx):
        supporter_roles = self.get_roles()

        roless = []

        for i in supporter_roles:
            role = discord.utils.get(ctx.guild.roles, id=int(i))

            roless.append(role.name)


        await ctx.send(embed=func.Embed("\n".join(roless)))

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
            cur.execute(f"INSERT into `colour_roles` (roleid) VALUES ({roleid})")
            mydb.commit()
            return True
        else:
            return False

    def already_support_role(self, roleid):
        if sql.Entry_Check(str(roleid), "roleid", "colour_roles"):
            return True

    async def is_owner(self, user):
        UID = str(user.id)
        if sql.Entry_Check(UID, "id", "owners"):
            return True
        else:
            return False

    async def is_admin(self, user):
        UID = str(user.id)
        if sql.Entry_Check(UID, "id", "admins") or sql.Entry_Check(UID, "id", "owners"):
            return True
        else:
            return False

    async def is_supporter(self, user):
        for roles in user.roles:
            if sql.Entry_Check(str(roles.id), "roleid", "colour_roles"):
                return True

    def get_roles(self):
        list = []
        mydb = sql.createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT roleid from colour_roles")
        for Row in cur:
            list.append(Row[0])

        return list

    def SetVals(self, guild):
        self.spam = discord.utils.get(guild.text_channels, id=self.spam_id)

        return


def setup(bot):
    bot.add_cog(Colour_Roles(bot))
