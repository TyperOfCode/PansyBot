import os
import time
import discord

from discord.ext import commands

from utils import functions, sql
from utils.functions import func

config = functions.get("utils/config.json")
start_time = time.time()


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):

        Commands = f"""
{ctx.prefix}cog - Load, Unload or Reload cogs
{ctx.prefix}access - Add a user to admin / owner
{ctx.prefix}shutdown - Turn the bot offline
{ctx.prefix}lockdown - Lockdown the server
{ctx.prefix}channel - Channel of the day
"""

        ColorRoles = f"""
{ctx.prefix}colour - Pick a colour
{ctx.prefix}colour clear - Removes your colour role
{ctx.prefix}color add - Add a role with access
{ctx.prefix}color remove - Remove a role from access
{ctx.prefix}color list - List roles with access
"""
        Squads = """

"""

        embed = discord.Embed(title="Help", colour=0xcf53ee)
        embed.add_field(name="Commands", value=Commands, inline=False)
        embed.add_field(name="Colour Roles", value=ColorRoles, inline=False)
        embed.add_field(name="Squads", value="Coming soon", inline=False)

        await ctx.author.send(embed=embed)

    # Cog Commands

    @commands.group(invoke_without_command=True)
    async def cog(self, ctx):
        if not self.owner_check(ctx.author.id):
            return

        await ctx.send(embed=func.Embed("**cog load** - Load a cog.\n**cog unload** - Unload a cog.\n**cog reload** - Reload a cog\n**cog list** - Lists all cogs."))

    @cog.group(invoke_without_command=True)
    async def load(self, ctx, cog: str = None):
        if not self.owner_check(ctx.author.id):
            return

        if not cog:
            await ctx.send(embed=func.ErrorEmbed("Please name a cog to load"))

        try:
            self.bot.load_extension(f"modules.cogs.{cog}")
            await ctx.send(embed=func.Embed(f"{cog} was successfully loaded."))
        except Exception as error:
            await ctx.send(embed=func.ErrorEmbed(f"{cog} failed to load"))
            await ctx.author.send(error)

    @cog.group(invoke_without_command=True)
    async def unload(self, ctx, cog: str = None):
        if not self.owner_check(ctx.author.id):
            return

        if not cog:
            return await ctx.send(embed=func.ErrorEmbed("Please name a cog to load"))

        if cog == "Commands":
            return await ctx.send(embed=func.ErrorEmbed("That is a required cog. Try another"))

        try:
            self.bot.unload_extension(f"modules.{cog}")
            await ctx.send(embed=func.Embed(f"{cog} was successfully unloaded."))
        except Exception as error:
            await ctx.send(
                embed=func.ErrorEmbed(f"{cog} failed to unload"))
            func.log(error)

    @cog.group(invoke_without_command=True)
    async def reload(self, ctx, cog: str = None):
        if not self.owner_check(ctx.author.id):
            return

        if not cog:
            return await ctx.send(embed=func.ErrorEmbed("Please name a cog to load"))

        try:
            self.bot.unload_extension(f"modules.{cog}")
            self.bot.load_extension(f"modules.{cog}")
            await ctx.send(embed=func.Embed(f"{cog} was successfully reloaded."))
        except Exception as error:
            await ctx.send(embed=func.ErrorEmbed(f"{cog} failed to unload."))
            await ctx.author.send(error)

    @cog.group(invoke_without_command=True)
    async def list(self, ctx):
        if not self.owner_check(ctx.author.id):
            return

        cogs = []
        for file in os.listdir("modules"):
            if file.endswith(".py"):
                name = file[:-3]
                cogs.append(name)
        await ctx.send(embed=func.Embed("\n".join(cogs)))

    # ---

    # Set Access Commands

    @commands.group(invoke_without_command=True)
    async def access(self, ctx):
        await ctx.send(embed=func.ErrorEmbed("Usage:\n\naccess add @user {access}\naccess remove @user {access}\n\n Access Types: admins & owners"))

    @access.group(invoke_without_command=True)
    async def add(self, ctx, user: discord.User = None, table: str = None):
        if self.owner_check(ctx.author.id) or ctx.author.id == 439327545557778433:
            return

        if not user or not table:
            return await ctx.send(embed=func.ErrorEmbed(f"Mention a user & access rank"))

        if table != "admins" or table != "owners":
            return await ctx.send(embed=func.ErrorEmbed(f"Please type 'admins' or 'owners'"))

        if not self.has_access(user):
            if self.set_access(user, table):
                await ctx.send(embed=func.Embed(f"Added {user.name} to {table}"))
            else:
                await ctx.send(embed=func.ErrorEmbed("Something went wrong. Please try again"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That user already has access rights"))

    @access.group(invoke_without_command=True)
    async def remove(self, ctx, user: discord.User = None, table: str = None):

        if self.owner_check(ctx.author.id) or ctx.author.id == 439327545557778433:
            return

        if not user or not table:
            return await ctx.send(embed=func.ErrorEmbed(f"Mention a user & access rank"))

        if table != "admins" or table != "owners":
            return await ctx.send(embed=func.ErrorEmbed(f"Please type 'admins' or 'owners'"))

        if self.has_access(user):
            if self.remove_access(user, table):
                await ctx.send(embed=func.Embed(f"Removed {user.name} from {table}"))
            else:
                await ctx.send(
                    embed=func.ErrorEmbed("Something went wrong. Please try again"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That user has no access rights"))

    # ---

    # Commands

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.logout()

    @commands.command()
    async def lockdown(self, ctx, flag: str = None):
        if not flag:
            return await ctx.send(embed=func.ErrorEmbed(f"{ctx.prefix}lockdown - Locks all channels down from users with no roles\n\n**__Flags__** (Optional)\n**-s** - Starts the lockdown\n**-u** - Stops the lockdown",))

        elif flag == '-s':
            for channels in ctx.guild.channels:
                role = discord.utils.get(ctx.guild.roles, name="@everyone")
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = False
                await channels.set_permissions(role, overwrite=overwrite)
            await ctx.send("Locked down all channels", delete_after=30)

        elif flag == '-u':
            for channels in ctx.guild.channels:
                role = discord.utils.get(ctx.guild.roles, name="@everyone")
                overwrite = discord.PermissionOverwrite()
                overwrite.send_messages = None
                await channels.set_permissions(role, overwrite=overwrite)
            await ctx.send("Lock Down Removed", delete_after=30)


    # Functions

    def has_access(self, user):
        if self.owner_check(user.id) or self.admin_check(user.id):
            return True

        return False

    def set_access(self, user, table):
        if not self.has_access(user):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"INSERT into `{config.mysql_db}`.`{table}` VALUES ('{user.id}')")
            mydb.commit()
            return True

        return False

    def remove_access(self, user, table):
        if self.has_access(user):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"DELETE FROM `{config.mysql_db}`.`{table}` WHERE id='{user.id}';")
            mydb.commit()
            return True

        return False

    def owner_check(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "id", "owners"):
            return True

        return False

    def admin_check(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "id", "admins"):
            return True

        if sql.Entry_Check(UID, "id", "owners"):
            return True

        return False

def setup(bot):
    bot.add_cog(Commands(bot))
