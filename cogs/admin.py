import os
import time
import psutil
import discord
import asyncio
import datetime
import mysql.connector

from discord.ext import commands
from utils.essentials import sql
from utils.essentials import functions
from utils.essentials.checks import check
from utils.essentials.functions import func

config = functions.get("utils/config.json")
start_time = time.time()

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.check(check.is_owner)
    async def cog(self, ctx):
        await ctx.send(embed=func.eErr("Choose one", "**cog load** - Load a cog.\n**cog unload** - Unload a cog.\n**cog reload** - Reload a cog\n**cog list** - Lists all cogs.", "Cogs"), delete_after=config.deltimer)

    @cog.group(invoke_without_command=True)
    @commands.check(check.is_owner)
    async def load(self, ctx, cog : str=None):
        if cog:
            try:
                self.bot.load_extension(f"cogs.{cog}")
                await ctx.send(embed=func.Editable("Done", f"{cog} was successfully loaded.", "Cogs"), delete_after=config.deltimer)
            except Exception as error:
                await ctx.send(embed=func.Editable_E(f"An unexpected error occurred", f"{cog} failed to load", "Error"), delete_after=config.deltimer)
                func.log(error)
        else:
            await ctx.send(embed=func.Editable_E("You missed something", "Please name a cog to load", "Error"), delete_after=config.deltimer)

    @cog.group(invoke_without_command=True)
    @commands.check(check.is_owner)
    async def unload(self, ctx, cog : str=None):
        if cog:
            if cog != "admin":
                try:
                    self.bot.unload_extension(f"cogs.{cog}")
                    await ctx.send(embed=func.Editable("Done", f"{cog} was successfully unloaded.", "Cogs"), delete_after=config.deltimer)
                except Exception as error:
                    await ctx.send(embed=func.Editable_E(f"An unexpected error occurred", f"{cog} failed to unload", "Error"), delete_after=config.deltimer)
                    func.log(error)
            else:
                await ctx.send(embed=func.Editable_E(f"Access Denied", "That is a required cog. Try another", "Cogs"), delete_after=config.deltimer)
        else:
            await ctx.send(embed=func.Editable_E("You missed something", "Please name a cog to unload", "Error"), delete_after=config.deltimer)

    @cog.group(invoke_without_command=True)
    @commands.check(check.is_owner)
    async def reload(self, ctx, cog : str=None):
        if cog:
            try:
                self.bot.unload_extension(f"cogs.{cog}")
                self.bot.load_extension(f"cogs.{cog}")
                await ctx.send(embed=func.Editable("Done", f"{cog} was successfully reloaded.", "Cogs"), delete_after=config.deltimer)
            except Exception as error:
                await ctx.send(embed=func.Editable_E(f"An unexpected error occurred", f"{cog} failed to unload.", "Error"), delete_after=config.deltimer)
                func.log(error)
        else:
            await ctx.send(embed=func.Editable_E("You missed something", "Please name a cog to reload.", "Error"), delete_after=config.deltimer)

    @cog.group(invoke_without_command=True)
    @commands.check(check.is_owner)
    async def list(self, ctx):
        cogs = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                cogs.append(name)
        await ctx.send(embed=func.Editable("All Cogs", ", ".join(cogs), "Cogs"), delete_after=config.deltimer)

    @commands.command()
    @commands.check(check.is_owner)
    async def restart(self, ctx):
        await ctx.send("Restarting...")
        os.system("cls")
        os.system("py -3 ./bot.py")
        await self.bot.logout()

    @commands.command()
    @commands.check(check.is_owner)
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.logout()

    @commands.command()
    @commands.check(check.is_admin)
    async def ram(self, ctx):
        process = psutil.Process(os.getpid())
        ramBytes = process.memory_info().rss
        ramKilo = round(ramBytes/1024, 2)
        ramMega = round(ramKilo/1024, 2)
        ramGiga = round(ramMega/1024, 2)
        await ctx.send(embed=func.ENoFooter("RAM Usage", f"{ramMega}MB of RAM in use."))

    @commands.command()
    @commands.check(check.is_admin)
    async def pm(self, ctx, user : discord.User=None, *args):
        message = ' '.join(args)
        if message != "" and user:
            try:
                embed = discord.Embed(
                    title = f"You've recieved a message from {ctx.author}",
                    colour = 0x9bf442,
                    )
                embed.set_author(name=f"Message from {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
                embed.add_field(name="Message:", value=message, inline=True)
                embed.set_footer(text=f"UserID: {ctx.author.id}")
                await user.send(embed=embed)
            except Exception as error:
                await ctx.send(embed=func.Editable_E("An unexpected error occurred", "Message failed to send.", "Error"), delete_after=config.deltimer)
        else:
            await ctx.send(embed=func.Editable_E("You forgot something", "Please @someone and message to DM", "Error"), delete_after=config.deltimer)

    @commands.command()
    @commands.check(check.is_admin)
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        await ctx.send(embed=func.ENoFooter("Uptime", text))

    @commands.command()
    @commands.check(check.is_admin)
    async def checkroles(self, ctx):
        user = ctx.author
        rolelist = [655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775, 659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740, 669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237]
        for roles in ctx.author.roles:
            if roles.id in rolelist:
                for roles.id in rolelist:
                    print(f"Yes! Found a role in that list, id = {roles.id}")
                    role = discord.utils.get(ctx.guild.roles, id=roles.id)
                    await user.remove_roles(role)
            else:
                print(f"Nope - {roles.id}")

    @commands.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def access(self, ctx):
        await ctx.send(embed=func.Editable_E("Available Options", "Usage:\n\naccess add @user {access}\naccess remove @user {access}\n\n Access Types: admins & owners", "Access"))

    @access.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def add(self, ctx, user: discord.User=None, table:str=None):
        if user and table:
            if table == "admins" or table == "owners":
                if self.owner_check(ctx.author.id) or ctx.author.id == 439327545557778433:
                    if not self.has_access(user):
                        if self.set_access(user, table):
                            await ctx.send(embed=func.Editable(f"Added {user.name} to {table}", "", "Access"))
                        else:
                            await ctx.send(embed=func.Editable_E("Something went wrong. Please try again", "", "Access"))
                    else:
                        await ctx.send(embed=func.Editable_E("That user already has access rights", "", "Access"))
                else:
                    await ctx.send(embed=func.NoPerm())
            else:
                await ctx.send(embed=func.Editable_E(f"Please type 'admins' or 'owners'", "", "Access"))
        else:
            await ctx.send(embed=func.Editable_E(f"Mention a user & access rank", "", "Access"))

    @access.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    async def remove(self, ctx, user: discord.User=None, table:str=None):
        if user and table:
            if table == "admins" or table == "owners":
                if self.owner_check(ctx.author.id) or ctx.author.id == 439327545557778433:
                    if self.has_access(user):
                        if self.remove_access(user, table):
                            await ctx.send(embed=func.Editable(f"Removed {user.name} from {table}", "", "Access"))
                        else:
                            await ctx.send(embed=func.Editable_E("Something went wrong. Please try again", "", "Access"))
                    else:
                        await ctx.send(embed=func.Editable_E("That user has no access rights", "", "Access"))
                else:
                    await ctx.send(embed=func.NoPerm())
            else:
                await ctx.send(embed=func.Editable_E(f"Please type 'admins' or 'owners'", "", "Access"))
        else:
            await ctx.send(embed=func.Editable_E(f"Mention a user & access rank", "", "Access"))

    def has_access(self, user):
        if self.owner_check(user.id) or self.admin_check(user.id):
            return True
        else:
            return False

    def set_access(self, user, table):
        UID = (user.id)
        if not self.has_access(user):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"INSERT into `{config.mysql_db}`.`{table}` VALUES ('{user.name}', '{user.id}')")
            mydb.commit()
            return True
        else:
            return False

    def remove_access(self, user, table):
        UID = (user.id)
        if self.has_access(user):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"DELETE FROM `{config.mysql_db}`.`{table}` WHERE id='{UID}';")
            mydb.commit()
            return True
        else:
            return False

    def owner_check(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "id", "owners"):
            return True

    def admin_check(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "id", "admins"):
            return True

def setup(bot):
    bot.add_cog(Admin(bot))
