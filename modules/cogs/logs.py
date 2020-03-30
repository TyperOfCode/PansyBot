import datetime
import discord
import json

from discord.ext import commands

from utils.essentials import functions
from utils.essentials.checks import check
from utils.essentials.functions import func

config = functions.get("utils/config.json")

logs_settings = {"Channel_Logs": {"Enabled": False, "Channel": None}, "Edit_Logs": {"Enabled": False, "Channel": None}, "Delete_Logs": {"Enabled": False, "Channel": None}, "Server_Logs": {"Enabled": False, "Channel": None}, "Channel_Logs": {"Enabled": False, "Channel": None}, "Role_Logs": {"Enabled": False, "Channel": None}}

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./modules/cogs/data/logs/logs.json") as f:
            self.logs = json.load(f)


    @commands.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def logs(self, ctx):
        if ctx.guild:
            GID = str(ctx.guild.id)
            if GID in self.logs:
                await ctx.send(embed=func.Editable_E("Invalid Arguments", f"{ctx.prefix}logs set flag\n{ctx.prefix}logs toggle", "Logs"), delete_after=config.deltimer)
            else:
                self.logs[GID] = logs_settings
                with open("./modules/cogs/data/logs/logs.json", "w") as f:
                    json.dump(self.logs, f, indent=4)
                    await ctx.reinvoke()

    @logs.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def set(self, ctx, flag = None):
        if ctx.guild:
            GID = str(ctx.guild.id)
            if flag:
                if flag == "-s":
                    self.logs[GID]["Server_Logs"]["Enabled"] = True
                    self.logs[GID]["Server_Logs"]["Channel"] = ctx.channel.id
                    with open("./modules/cogs/data/logs/logs.json", "w") as f:
                        json.dump(self.logs, f, indent=4)
                        await ctx.send(embed=func.Editable_S(f"Server Logs Enabled and set to **{ctx.channel.name}**", "", "Logs"), delete_after=config.deltimer)
                elif flag == "-e":
                    self.logs[GID]["Edit_Logs"]["Enabled"] = True
                    self.logs[GID]["Edit_Logs"]["Channel"] = ctx.channel.id
                    with open("./modules/cogs/data/logs/logs.json", "w") as f:
                        json.dump(self.logs, f, indent=4)
                        await ctx.send(embed=func.Editable_S(f"Message Edit Logs Enabled and set to **{ctx.channel.name}**", "", "Logs"), delete_after=config.deltimer)
                elif flag == "-d":
                    self.logs[GID]["Delete_Logs"]["Enabled"] = True
                    self.logs[GID]["Delete_Logs"]["Channel"] = ctx.channel.id
                    with open("./modules/cogs/data/logs/logs.json", "w") as f:
                        json.dump(self.logs, f, indent=4)
                        await ctx.send(embed=func.Editable_S(f"Delete logs Enabled and set to **{ctx.channel.name}**", "", "Logs"), delete_after=config.deltimer)
                elif flag == "-c":
                    self.logs[GID]["Channel_Logs"]["Enabled"] = True
                    self.logs[GID]["Channel_Logs"]["Channel"] = ctx.channel.id
                    with open("./modules/cogs/data/logs/logs.json", "w") as f:
                        json.dump(self.logs, f, indent=4)
                        await ctx.send(embed=func.Editable_S(f"Channel Edit logs Enabled and set to **{ctx.channel.name}**", "", "Logs"), delete_after=config.deltimer)
                elif flag == "-r":
                    self.logs[GID]["Role_Logs"]["Enabled"] = True
                    self.logs[GID]["Role_Logs"]["Channel"] = ctx.channel.id
                    with open("./modules/cogs/data/logs/logs.json", "w") as f:
                        json.dump(self.logs, f, indent=4)
                        await ctx.send(embed=func.Editable_S(f"Channel Edit logs Enabled and set to **{ctx.channel.name}**", "", "Logs"), delete_after=config.deltimer)
            else:
                await ctx.send(embed=func.Editable_E("Invalid Arguments", f"{ctx.prefix}logs set flag - Sets the logging channel for the flag\n**-s** - Server Edit Logs\n**-e** - Message Edit logs\n**-d** - Message delete logs\n**-c** - Channel Logs\n**-r** - Role logs", "Logs"), delete_after=config.deltimer)

    @logs.group(invoke_without_command=True)
    @commands.check(check.is_admin)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toggle(self, ctx, log = None):
        if ctx.guild:
            GID = str(ctx.guild.id)
            if log:
                if log == "Delete" or log == "delete":
                    if self.logs[GID]["Delete_Logs"]["Enabled"] == False:
                        self.logs[GID]["Delete_Logs"]["Enabled"] = True
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Delete** Logs Enabled", "", "Logs"), delete_after=config.deltimer)
                    else:
                        self.logs[GID]["Delete_Logs"]["Enabled"] = False
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Delete** Logs Disabled", "", "Logs"), delete_after=config.deltimer)

                elif log == "Edit" or log == "edit":
                    if self.logs[GID]["Edit_Logs"]["Enabled"] == False:
                        self.logs[GID]["Edit_Logs"]["Enabled"] = True
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Edit** Logs Enabled", "", "Logs"), delete_after=config.deltimer)
                    else:
                        self.logs[GID]["Edit_Logs"]["Enabled"] = False
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Edit** Logs Disabled", "", "Logs"), delete_after=config.deltimer)

                elif log == "Server" or log == "server":
                    if self.logs[GID]["Server_Logs"]["Enabled"] == False:
                        self.logs[GID]["Server_Logs"]["Enabled"] = True
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Server** Logs Enabled", "", "Logs"), delete_after=config.deltimer)
                    else:
                        self.logs[GID]["Server_Logs"]["Enabled"] = False
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Server** Logs Disabled", "", "Logs"), delete_after=config.deltimer)

                elif log == "channel" or log == "channel":
                    if self.logs[GID]["Channel_Logs"]["Enabled"] == False:
                        self.logs[GID]["Channel_Logs"]["Enabled"] = True
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Channel** Logs Enabled", "", "Logs"), delete_after=config.deltimer)
                    else:
                        self.logs[GID]["Channel_Logs"]["Enabled"] = False
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Channel** Logs Disabled", "", "Logs"), delete_after=config.deltimer)

                elif log == "Roles" or log == "roles":
                    if self.logs[GID]["Role_Logs"]["Enabled"] == False:
                        self.logs[GID]["Role_Logs"]["Enabled"] = True
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Role** Logs Enabled", "", "Logs"), delete_after=config.deltimer)
                    else:
                        self.logs[GID]["Role_Logs"]["Enabled"] = False
                        with open("./modules/cogs/data/logs/logs.json", "w") as f:
                            json.dump(self.logs, f, indent=4)
                            await ctx.send(embed=func.Editable_S(f"**Role** Logs Disabled", "", "Logs"), delete_after=config.deltimer)
            else:
                e = discord.Embed(title = f"Log Settings for {ctx.guild.name}", colour = 0x9bf442)
                e.add_field(name="Delete", value=str(self.logs[GID]['Delete_Logs']["Enabled"]))
                e.add_field(name="Edit", value=str(self.logs[GID]['Edit_Logs']["Enabled"]))
                e.add_field(name="Server", value=str(self.logs[GID]['Server_Logs']["Enabled"]))
                e.add_field(name="Channel", value=str(self.logs[GID]['Channel_Logs']["Enabled"]))
                e.add_field(name="Roles", value=str(self.logs[GID]['Role_Logs']["Enabled"]))
                e.set_thumbnail(url=ctx.guild.icon_url)
                await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild:
            guild = message.guild
            GID = str(message.guild.id)
            if GID in self.logs:
                if self.logs[GID]['Delete_Logs']["Enabled"] == True:
                    if not message.author is message.author.bot:
                        channel = await self.bot.fetch_channel(self.logs[GID]["Delete_Logs"]["Channel"])
                        time = datetime.datetime.utcnow()
                        cleanmsg = message.content
                        for i in message.mentions:
                            cleanmsg = cleanmsg.replace(i.mention, str(i))
                        fmt = '%H:%M:%S'
                        name = message.author
                        name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
                        try:
                            delmessage = discord.Embed(colour=0x9bf442, timestamp=datetime.datetime.utcnow())
                            infomessage = "A message by __{}__, was deleted in {}".format(message.author.nick if message.author.nick else message.author.name, message.channel.mention)
                            delmessage.add_field(name="Info:", value=infomessage, inline=False)
                            delmessage.add_field(name="Message:", value=cleanmsg)
                            delmessage.set_footer(text="User ID: {}".format(message.author.id))
                            delmessage.set_author(name="Deleted Message")
                            delmessage.set_thumbnail(url="http://i.imgur.com/fJpAFgN.png")
                            await channel.send(embed=delmessage)
                        except Exception as e:
                            return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.guild:
            guild = before.guild
            GID = str(guild.id)
            if GID in self.logs:
                if self.logs[GID]['Edit_Logs']["Enabled"] == True:
                    cleanbefore = before.content
                    for i in before.mentions:
                        cleanbefore = cleanbefore.replace(i.mention, str(i))
                    cleanafter = after.content
                    for i in after.mentions:
                        cleanafter = cleanafter.replace(i.mention, str(i))
                    channel = await self.bot.fetch_channel(self.logs[GID]["Edit_Logs"]["Channel"])
                    time = datetime.datetime.utcnow()
                    fmt = '%H:%M:%S'
                    name = before.author
                    name = " ~ ".join((name.name, name.nick)) if name.nick else name.name
                    edit = discord.Embed(colour=0x9bf442, timestamp=datetime.datetime.utcnow())
                    infomessage = "A message by __{}__, was edited in {}".format(before.author.nick if before.author.nick else before.author.name, before.channel.mention)
                    try:
                        edit.add_field(name="Info:", value=infomessage, inline=False)
                        edit.add_field(name="Before Message:", value=cleanbefore, inline=False)
                        edit.add_field(name="After Message:", value=cleanafter)
                        edit.set_footer(text=f"User ID: {before.author.id}")
                        edit.set_author(name="Edited Message")
                        edit.set_thumbnail(url="http://i.imgur.com/Q8SzUdG.png")
                        await channel.send(embed=edit)
                    except Exception as e:
                        return

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if after.guild:
            guild = before.guild
            GID = str(guild.id)
            if GID in self.logs:
                if self.logs[GID]['Channel_Logs']["Enabled"] == True:
                    channel = await self.bot.fetch_channel(self.logs[GID]["Channel_Logs"]["Channel"])
                    time = datetime.datetime.now()
                    fmt = "%H:%M:%S"
                    msg = ""

                    if before.name != after.name:
                        if before.type == discord.ChannelType.voice:
                            voice1 = discord.Embed(colour=0x9bf442)
                            infomessage = ":loud_sound: Voice channel name update. Before: **{}** After: **{}**.".format(before.name, after.name)
                            voice1.add_field(name="Info:", value=infomessage, inline=False)
                            voice1.set_author(name=time.strftime(fmt) + " - Voice Channel Update",icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            voice1.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            await channel.send(embed=voice1)

                        if before.type == discord.ChannelType.text:
                            text1 = discord.Embed(colour=0x9bf442)
                            infomessage = ":page_facing_up: Text channel name update. Before: **{}** After: **{}**.".format(before.name, after.name)
                            text1.add_field(name="Info:", value=infomessage, inline=False)
                            text1.set_author(name=time.strftime(fmt) + " - Voice Channel Update", icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            text1.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            await channel.send(embed=text1)

                    if before.topic != after.topic:
                        topic = discord.Embed(colour=0x9bf442)
                        infomessage = ":page_facing_up: `{}` Channel topic has been updated.\n**Before:** {}\n**After:** {}".format(time.strftime(fmt), before.topic, after.topic)
                        topic.add_field(name="Info:", value=infomessage, inline=False)
                        topic.add_field(name="Channel:", value=after.name, inline=False)
                        topic.set_author(name=time.strftime(fmt) + " - Channel Topic Update", icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                        topic.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                        await channel.send(embed=topic)

                    if before.position != after.position:
                        if before.type == discord.ChannelType.voice:
                            voice2 = discord.Embed(colour=0x9bf442)
                            voice2.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            voice2.set_author(name=time.strftime(fmt) + " Voice Channel Position Update",icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            infomsg = ":loud_sound: Voice channel position update. Channel: **{}** Before: **{}** After: **{}**.".format(before.name, before.position, after.position)
                            voice2.add_field(name="Info:", value=infomsg, inline=False)
                            voice2.add_field(name="Channel:", value=after.name, inline=False)
                            await channel.send(embed=voice2)

                        if before.type == discord.ChannelType.text:
                            text2 = discord.Embed(colour=0x9bf442)
                            text2.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            text2.set_author(name=time.strftime(fmt) + " Text Channel Position Update",icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            infomsg = ":page_facing_up: Text channel position update. Before: **{}** After: **{}**.".format(before.position, after.position)
                            text2.add_field(name="Info:", value=infomsg, inline=False)
                            text2.add_field(name="Channel:", value=after.name, inline=False)
                            await channel.send(embed=text2)

                    if before.type == discord.ChannelType.voice:
                        if before.bitrate != after.bitrate:
                            bitrate = discord.Embed(colour=0x9bf442)
                            bitrate.set_author(name=time.strftime(fmt) + " Bitrate Update", icon_url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            bitrate.set_thumbnail(url="http://www.hey.fr/fun/emoji/twitter/en/icon/twitter/565-emoji_twitter_speaker_with_three_sound_waves.png")
                            infomsg = ":loud_sound: Voice Channel bitrate update. Before: **{}** After: **{}**.".format(before.bitrate, after.bitrate)
                            bitrate.add_field(name="Info:", value=infosg, inline=False)
                            bitrate.add_field(name="Channel:", value=after.name, inline=False)
                            await channel.send(embed=bitrate)

                    if before.type == discord.ChannelType.text:
                        if before.slowmode_delay != after.slowmode_delay:
                            slowmode = discord.Embed(colour=0x9bf442)
                            slowmode.set_author(name=time.strftime(fmt) + " Slow Mode Update", icon_url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            slowmode.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            infomsg = ":page_facing_up: Slow Mode Update update. Before: **{}** After: **{}**.".format(before.slowmode_delay, after.slowmode_delay)
                            slowmode.add_field(name="Info:", value=infomsg, inline=False)
                            slowmode.add_field(name="Channel:", value=after.name, inline=False)
                            await channel.send(embed=slowmode)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if after:
            GID = str(after.id)
            if GID in self.logs:
                if self.logs[GID]['Server_Logs']["Enabled"] == True:
                    channel = await self.bot.fetch_channel(self.logs[GID]["Server_Logs"]["Channel"])
                    if before.name != after.name:
                        sname = discord.Embed(colour=0x9bf442,timestamp=datetime.datetime.utcnow())
                        sname.add_field(name="Before:", value=f"**{before.name}**", inline=False)
                        sname.add_field(name="After:", value=f"**{after.name}**", inline=False)
                        sname.set_footer(text=f"Guild ID: {GID}")
                        sname.set_author(name="Guild Name Changed")
                        await send_to.send(embed=sname)

                    if before.region != after.region:
                        rname = discord.Embed(colour=0x9bf442, timestamp=datetime.datetime.utcnow())
                        rname.add_field(name="Before:", value=f"**{before.region}**", inline=False)
                        rname.add_field(name="After:", value=f"**{after.region}**", inline=False)
                        rname.set_footer(text=f"Guild ID: {GID}")
                        rname.set_author(name="Guild Region Changed")
                        await channel.send(embed=rname)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild:
            before_roles = []
            after_roles = []
            GID = str(after.guild.id)
            if GID in self.logs:
                if self.logs[GID]['Role_Logs']["Enabled"] == True:
                    try:
                        channel = await self.bot.fetch_channel(self.logs[GID]["Role_Logs"]["Channel"])
                        time = datetime.datetime.now()
                        fmt = '%H:%M:%S'
                        if before.roles != after.roles:
                            for roles in before.roles:
                                before_roles.append(roles.name)
                            before_roles.remove("@everyone")
                            for roles in after.roles:
                                after_roles.append(roles.name)
                            after_roles.remove("@everyone")
                            role = discord.Embed(colour=0xf59542, timestamp=datetime.datetime.utcnow())
                            infomessage = f"__{before.name}__'s roles were updated"
                            role.add_field(name="Info:", value=infomessage, inline=False)
                            role.add_field(name="Before:", value=", ".join(before_roles), inline=False)
                            role.add_field(name="After:", value=", ".join(after_roles), inline=False)
                            role.set_footer(text=f"User ID: {before.id}")
                            role.set_author(name=time.strftime(fmt) + " - Role Update")
                            role.set_thumbnail(url="https://s-media-cache-ak0.pinimg.com/originals/27/18/77/27187782801d15f756a27156105d1233.png")
                            await channel.send(embed=role)
                    except Execption as e:
                        return


def setup(bot):
    bot.add_cog(Logs(bot))
