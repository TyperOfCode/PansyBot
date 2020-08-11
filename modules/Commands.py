import platform
import datetime
import discord
import aiohttp
import time
import os

from psutil import virtual_memory
from discord.ext import commands
from psutil import cpu_percent
from random import randint

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
{ctx.prefix}channel - Channel of the day
{ctx.prefix}ship [@user] [@user] - Ship people
{ctx.prefix}binfo - Bot info
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
        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

        await ctx.send(embed=func.Embed("**cog load** - Load a cog.\n**cog unload** - Unload a cog.\n**cog reload** - Reload a cog\n**cog list** - Lists all cogs."))

    @cog.group(invoke_without_command=True)
    async def load(self, ctx, cog: str = None):
        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

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
        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

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
        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

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
        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

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

        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

        await ctx.send(embed=func.ErrorEmbed(f"Usage:\n\n{ctx.prefix}access add @user [Type]\n{ctx.prefix}access remove @user\n{ctx.prefix}access list\n\n Access Types: admin & owner"))

    @access.group(invoke_without_command=True)
    async def add(self, ctx, user: discord.User = None, access: str = None):

        types = ['owner', 'admin']

        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

        if not user or not access:
            return await ctx.send(embed=func.ErrorEmbed(f"Mention a user & access rank"))

        if access not in types:
            return await ctx.send(embed=func.ErrorEmbed(f"Please type 'admin' or 'owner'"))

        if access == 'owner':
            type = 2

        elif access == 'admin':
            type = 1

        if not sql.isStaff(user):
            if sql.SetAccess(user, type):
                await ctx.send(embed=func.Embed(f"Gave {user.mention} {access}."))
            else:
                await ctx.send(embed=func.ErrorEmbed("Something went wrong. Please try again"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That user already has access rights"))

    @access.group(invoke_without_command=True)
    async def remove(self, ctx, user: discord.User = None):

        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

        if not user:
            return await ctx.send(embed=func.ErrorEmbed(f"Mention a user"))

        if sql.isStaff(user):
            if sql.DelAccess(user):
                await ctx.send(embed=func.Embed(f"Removed {user.mention}'s rights"))
            else:
                await ctx.send(embed=func.ErrorEmbed("Something went wrong. Please try again"))
        else:
            await ctx.send(embed=func.ErrorEmbed("That user has no access rights"))

    @access.group(invoke_without_command=True)
    async def list(self, ctx):

        if not sql.isOwner(ctx.author.id):
            return await ctx.send(embed=func.NoPerm())

        unformatted = sql.getallAccess()

        formatted = []

        for i in unformatted:
            user = await self.bot.fetch_user(i[0])

            if i[1] == 1:
                type = "Admin Access"

            if i[1] == 2:
                type = "Owner Access"

            formatted.append(f"{user.mention} - {type}")

        await ctx.send(embed=func.Embed("\n".join(formatted)))

    # ---

    # Commands

    @commands.command()
    async def shutdown(self, ctx):

        if not sql.isOwner(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        await ctx.send("Shutting down...")
        await self.bot.logout()

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ship(self, ctx, user:discord.User = None, user1: discord.User =None):
        if not user or not user1:
            return

        if ctx.channel.id == 542291426051096606:
            return

        matchability = randint(0, 100)

        if user.id == 682585660355510275 or user1.id == 682585660355510275:
            if user.id == 439327545557778433 or user1.id == 439327545557778433: # If Stig and Hana
                matchability = 100
            else:
                matchability = 0

        embed = discord.Embed(
            description=f"{user.mention} ❤ {user1.mention}",
            colour=0xcf53ee,
        )
        embed.set_footer(text=f"{matchability}% Match")

        await ctx.send(embed=embed)

    @commands.command(aliases=["binfo", "info"])
    @commands.guild_only()
    async def botinfo(self, ctx):
        activeServers = self.bot.guilds
        sum = 0
        for s in activeServers:
            sum += len(s.members)

        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime = str(datetime.timedelta(seconds=difference))

        dapi = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com/api/'):
                dapi2 = time.time()

        discordlatency = dapi2 - dapi

        connected_desc = f"""```

- Discord API ({int(round(discordlatency, 2) * 100)}ms)
- {len(activeServers)} Guilds
- {sum} Users
- Shards 1 / 1 ({int(round(self.bot.latency, 2) * 100)}ms)
- Cluster 0 / 0 (0ms)```"""

        coding_desc = f"""```
- Language: Python {platform.python_version()}
- Library: Discord.py
- Version: {discord.__version__}```"""

        cluster_desc = f"""```
- OS: {platform.system()}
- CPU Usage: {cpu_percent(interval=None, percpu=False)}%
- RAM Usage: {virtual_memory().percent}%
- Uptime: {uptime}```"""

        embed = discord.Embed(colour=0xcf53ee)

        embed.set_author(name="Bot Information")

        embed.add_field(name="Connected", value=connected_desc, inline=True)
        embed.add_field(name="Coding Stuff", value=coding_desc, inline=True)
        embed.add_field(name="Cluster", value=cluster_desc, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Commands(bot))
