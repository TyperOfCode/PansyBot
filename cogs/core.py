import asyncio
import datetime
import string
from random import randint

import discord
from discord import Spotify
from discord.ext import commands
from discord.utils import get

from utils.essentials import functions
from utils.essentials import sql
from utils.essentials.functions import func

config = functions.get("utils/config.json")


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sinfo(self, ctx):
        embed = discord.Embed(
            colour=0xeb8034,
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Creation Date", value=ctx.guild.created_at.strftime("%d/%m/%Y at %H:%M:%S"), inline=False)
        embed.add_field(name="Owner", value=ctx.guild.owner.name, inline=True)
        embed.add_field(name="Region", value=ctx.guild.region, inline=True)
        embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Users", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="AFK Channel", value=ctx.guild.afk_channel, inline=True)
        embed.set_author(name=f"Pansy", icon_url="https://img.no1irishstig.co.uk/5ei3h.png")
        embed.set_footer(icon_url=ctx.guild.icon_url, text=f"{ctx.guild.name} - {ctx.guild.id}")
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def info(self, ctx):
        activeServers = self.bot.guilds
        sum = 0
        for s in activeServers:
            sum += len(s.members)
        embed = discord.Embed(
            title=f"Info about {self.bot.user.name}",
            description="Multifunctional Bot, constantly recieving updates.",
            colour=0xeb8034
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.icon_url)
        embed.add_field(name="Github", value="[Github](https://github.com/TyperOfCode/PansyBot)", inline=True)
        embed.add_field(name="Need help?", value="PM Me <@!439327545557778433>", inline=True)
        embed.add_field(name="Currently Serving", value=f"{sum} Members", inline=True)
        embed.set_footer(text="{} - Providing Discord since {}".format(self.bot.user.name,
                                                                       self.bot.user.created_at.strftime("%d/%m/%Y")))
        await ctx.send(embed=embed, delete_after=30)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def uinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

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
            title=title,
            colour=0xeb8034,
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_author(name=f"Devolution", icon_url="https://i.imgur.com/BS6YRcT.jpg")
        embed.set_footer(text=f"{user.name}'s User Info", icon_url=user.avatar_url)
        embed.add_field(name="Joined At", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Status", value=user.status, inline=True)
        embed.add_field(name="Role Count", value=len(user.roles), inline=True)
        embed.add_field(name="Nickname", value=user.nick, inline=True)
        embed.add_field(name="Voice", value=channel, inline=True)
        await ctx.send(embed=embed, delete_after=30)

    # Events ------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(540784184470274069)
        people = format(len(guild.members), ",")
        watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
        await self.bot.change_presence(activity=watch)

        emojilist = '<a:yayhyper:658788790432956427> <:malyuSip:649269848047747092> <a:malYesss:613541344182272020> <a:malYayHyper:608280367744548880> <a:malYay:608280367580971017> <a:malWoop:610632031600115778> <:malwow:614525816360927233> <a:malWoahh:609048816963944448> <:malWoah:607837460470300683> <:malWoa:642018486654074922> <:malWinku:607838396349677568> <:malWinku:642018488344510464> <:malWelcome:665073482576691220> <a:malWH:629149080198578186> <a:malWaveDesu:610430770565087242> <a:malWave:658382330829996032> <:maluwuHeart:593137542904283145> <:MalUwU:658389108967604296> <a:maluwu:610632031696584724> <a:malThumbsUp:608280367312404481> <:malthonkblush:658035176424603678> <a:MalStars:612406936435949569> <a:malStar1:614619624268365829> <:malSparklyHeart:653605730452111361> <a:malSoHappy:618125323048976434> <a:malSnuggles:608278538554179584> <:malRaphiThumbsup:597527997838393353> <a:malpotatoeshuggle:608280365987135501> <a:malPikaDance:608688666528841728> <:malPeek:608687928087937024> <:malPatu:607838010125320192> <a:malPatu:608278537623044097> <a:malNya:608280365718831124> <a:malnya:608688667078295557> <a:malNods:608278535705985044> <a:malNekoPeek:608280368961028096> <a:malNekoDance:608280366066958346> <:malmegucomfy:599753428054573059> <:malmitsurilaugh:639656343577559040> <a:malJoins:609864729015353344> <a:malLoves:608278539128537088> <:malLoveDesu:613538787024437249> <a:malMaruFly:610632033710112788> <:malKokoroYay:640425181638164534> <a:malKittyYayR:640479986695929866> <a:malKittyYayL:640479984573743115>'.split(
            ' ')
        randemg = emojilist[randint(0, len(emojilist) - 1)]
        if ':' not in randemg:
            randemg = '<a:yayhyper:658788790432956427>'
        # print(f'Welcome = {not (len(guild.members) % 2) == 0}')
        if not (len(guild.members) % 2) == 0:
            channel = discord.utils.get(guild.text_channels, id=542291426051096606)
            # embed = discord.Embed(title=f'Welcome to My Anime Land, {member.mention}.',color=0xff00e1,description=f'Read <#607634761586049075> and introduce yourself <#661259788759597076> {randemg}')
            await channel.send(f'**We are pleased to have you join us {member.mention}, Enjoy your stay! {randemg}**')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = self.bot.get_guild(540784184470274069)
        people = format(len(guild.members), ",")
        watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
        await self.bot.change_presence(activity=watch)

    @commands.Cog.listener(name="on_message")
    async def on_message_pingcheck(self, message):
        if 439327545557778433 in message.raw_mentions or 636808158521589770 in message.raw_mentions: 
            await message.add_reaction("<a:malwdym:605144102857867294>")

    @commands.Cog.listener(name="on_message")
    async def on_message_tournament(self, message):
        if message.channel.id == 671674088682684416:  # Tournaments
            emotes = ["malWow", "malHeart"]
            for x in emotes:
                await message.add_reaction(get(message.guild.emojis, name=x))

    @commands.Cog.listener(name="on_message")
    async def on_message_prefix(self, message):
        if message.content == "<@!669724238252474387> prefix":
            await message.channel.send(f"My current prefix is set to: p^")
        if message.channel.id == 542291426051096606 or message.channel.id == 622449628083912705:
            if "bye" in message.content.lower() or "bai" in message.content.lower():
                emote = discord.utils.get(message.guild.emojis, name="malWaveDesu")
                await message.add_reaction(emote)
            try:
                if message.channel.id == 660474909339680788:  # Applications
                    bypass = [231463189487943690, 655481681741873152]
                if message.author.id not in bypass:
                    await message.delete()
            except Exception as e:
                pass
            else:
                if message.channel.id == 604169947286863882:
                    if len(message.content) > 7:
                        await message.delete()
                    else:
                        try:
                            number = int(message.content)
                            target = await message.channel.history(limit=2).flatten()
                            previous = target[1].content
                            if "0000" in previous:
                                await message.pin()
                            new = int(previous) + 1
                            if number != new:
                                await message.delete()
                        except:
                            return
                if message.channel.id == 548017507982901258 and message.author.id != self.bot.user.id:
                    if len(message.content) <= 20:
                        for letter in message.content:
                            if letter.lower() not in string.ascii_letters:
                                await message.delete()
                        targetLetter = message.content[-1:]
                        if targetLetter.lower() in string.ascii_letters:
                            target = await message.channel.history(limit=2).flatten()
                            if target[1].content[-1:].lower() == target[0].content[:1].lower():
                                pass
                            else:
                                await message.delete()
                    else:
                        await message.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 656491562682810386 and str(
                payload.emoji) == "\U00002705" and payload.user_id != 655481681741873152:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if message.author.id != 231463189487943690:
                await message.delete()

    # --------------------------------- Requests Start Here ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Colour Roles

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        access_log = discord.utils.get(ctx.guild.text_channels, name="access-log")

        if isinstance(error, commands.MissingAnyRole):
            await access_log.send(
                embed=func.AccessLog(f"Supporter access **Denied** for {ctx.author.id} (**{ctx.author.name}**)",
                                     ctx.message.content))
            return await ctx.send(embed=func.SupportErr(), delete_after=config.deltimer)
        else:
            raise error

    @commands.group(invoke_without_command=True, aliases=["colour"])
    @commands.has_any_role("ᴹᴬᴸ Donator💎", "ᴹᴬᴸ Nitro Booster 🌺", "ᴹᴬᴸ Giveaway Donator 🌻", "ᴹᴬᴸ Supporter 🌹")
    async def color(self, ctx, number: int = None):
        await self.is_supporter(ctx)
        await ctx.message.delete()
        user = ctx.author
        rolelist = [655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775,
                    659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740,
                    669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237]
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
                embed = discord.Embed(title=f"**{ctx.author.name}** obtained color {number}!", colour=colorembed,
                                      timestamp=datetime.datetime.utcfromtimestamp(1579828506))
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed = discord.Embed(title="Type !color <number> with the number you want",
                                      colour=discord.Colour(0xd42c2c),
                                      timestamp=datetime.datetime.utcfromtimestamp(1579828506))
                embed.set_image(url="https://i.imgur.com/H8Wk8wG.png")
                await ctx.send(embed=embed, delete_after=30)
        else:
            await channel1.send(f"{ctx.author.mention} Retry your command here", delete_after=30)
            await channel2.send(f"{ctx.author.mention} Or here", delete_after=30)

    @color.group(invoke_without_command=True)
    @commands.has_any_role("ᴹᴬᴸ Donator💎", "ᴹᴬᴸ Nitro Booster 🌺", "ᴹᴬᴸ Giveaway Donator 🌻", "ᴹᴬᴸ Supporter 🌹")
    async def clear(self, ctx):
        await self.is_supporter(ctx)
        await ctx.message.delete()
        user = ctx.author
        rolelist = [655070657612218370, 659133244205301781, 659133240237359135, 659133249284603956, 659133242204618775,
                    659146257360748574, 659133242930364445, 659133246000594967, 659133249662091275, 659146251941576740,
                    669241392459022401, 659146254382792718, 659146284606947366, 659146285236092948, 668858038714761237]
        channel1 = discord.utils.get(ctx.guild.text_channels, id=548932204672319499)
        channel2 = discord.utils.get(ctx.guild.text_channels, id=622906588562456576)
        if ctx.channel is channel1 or ctx.channel is channel2:
            for roles in ctx.author.roles:
                if roles.id in rolelist:
                    role = discord.utils.get(ctx.guild.roles, id=roles.id)
                    await user.remove_roles(role)
                    embed = discord.Embed(title=f"**{ctx.author.name}** Cleared their color roles!", colour=colorembed,
                                          timestamp=datetime.datetime.utcfromtimestamp(1579828506))
            await ctx.send(embed=embed, delete_after=10)
        else:
            await channel1.send(f"{ctx.author.mention} Retry your command here", delete_after=30)
            await channel2.send(f"{ctx.author.mention} Or here", delete_after=30)

    async def is_supporter(self, ctx):
        access_log = discord.utils.get(ctx.guild.text_channels, name="access-log")
        await access_log.send(
            embed=func.AccessLog(f"Supporter access **Granted** for {ctx.author.id} (**{ctx.author.name}**)",
                                 ctx.message.content))


    # Applications

    def has_applied(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "userid", "applications"):
            return True

    def add_id(self, user):
        UID = (user.id)
        if not self.has_applied(UID):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"INSERT into `applications` VALUES ('{UID}')")
            mydb.commit()
            return True
        else:
            return False

    @commands.command()
    async def apply(self, ctx):
        emojis = ["✖️", "✔️"]
        UID = str(ctx.author.id)
        category_emojis = []
        if ctx.message.guild.id == 540784184470274069 and ctx.channel.id == 660474909339680788:
            if not self.has_applied(UID):
                user = ctx.message.author
                guild = ctx.guild
                await ctx.message.delete()
                double_check = await user.send(embed=func.ENoFooter("Hey!",
                                                                    "Just to double check, you wish to apply for Helper in **My Anime Land**?"))
                await double_check.add_reaction(emojis[0])
                await double_check.add_reaction(emojis[1])

                def EmojisCheck(reaction, user):
                    return ctx.author == user and str(reaction.emoji) == emojis[0] or ctx.author == user and str(
                        reaction.emoji) == emojis[1]

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=EmojisCheck)
                except asyncio.TimeoutError:
                    await start.delete()
                    await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                else:
                    if str(reaction.emoji) == emojis[0]:
                        await double_check.delete()
                        await user.send(embed=func.Editable_E("Application Cancelled", "Thanks for your participation",
                                                              "Cancelled"))
                    elif str(reaction.emoji) == emojis[1]:
                        await double_check.delete()
                        await user.send("Ok perfect, you should get a notification about your application shortly.")
                        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                      ctx.author: discord.PermissionOverwrite(read_messages=True)}
                        channel = await guild.create_text_channel(name=f"application-{user.id}", overwrites=overwrites)
                        mention = await channel.send(user.mention)
                        await mention.delete()
                        main = await channel.send(embed=func.ENoFooter("Alright Cool. Lets begin with some questions",
                                                                       f"{user.mention} How old are you?"))
                        try:
                            age = await self.bot.wait_for("message", timeout=300,
                                                          check=lambda message: message.author == user)
                            await age.delete()
                        except asyncio.TimeoutError:
                            await msg.edit(embed=timeoutEmbed, delete_after=60)
                            await channel.delete()
                        else:
                            if age.content.isdigit() and int(age.content) > 12:
                                pass
                            else:
                                await main.edit(embed=discord.Embed(title="Invalid Age", color=0xff0000,
                                                                    description="Age must be a number, and above 12."))
                    await main.edit(embed=func.ENoFooter("Which timezone are you in?",
                                                         "This question is optional. Type 'N/A' if you do not wish to answer"))
                    try:
                        timezone = await self.bot.wait_for("message", timeout=500,
                                                           check=lambda message: message.author == user)
                        await timezone.delete()
                    except asyncio.TimeoutError:
                        await msg.edit(embed=timeoutEmbed, delete_after=60)
                        await channel.delete()
                    else:
                        await main.edit(embed=func.ENoFooter("Why do you want to become Helper?",
                                                             "Please give detail in your answer. You'll have a better chance, I promise."))
                        try:
                            reason = await self.bot.wait_for("message", timeout=300,
                                                             check=lambda message: message.author == user)
                            await reason.delete()
                        except asyncio.TimeoutError:
                            await msg.edit(embed=timeoutEmbed, delete_after=60)
                            await channel.delete()
                        else:
                            await main.edit(embed=func.ENoFooter("Can you work as a team?",
                                                                 "You may be required to cover for another helper during their downtime.\n\nGive us a few reasons behind your answer"))
                            try:
                                teamwork = await self.bot.wait_for("message", timeout=300,
                                                                   check=lambda message: message.author == user)
                                await teamwork.delete()
                            except asyncio.TimeoutError:
                                await msg.edit(embed=timeoutEmbed, delete_after=60)
                                await channel.delete()
                            else:
                                await main.edit(embed=func.ENoFooter("Activity",
                                                                     "We take activity seriously. How active can you be throughout the week on average?"))
                                try:
                                    activity = await self.bot.wait_for("message", timeout=300,
                                                                       check=lambda message: message.author == user)
                                    await activity.delete()
                                except asyncio.TimeoutError:
                                    await msg.edit(embed=timeoutEmbed, delete_after=60)
                                    await channel.delete()
                                else:
                                    await main.edit(embed=func.ENoFooter("Your Tasks",
                                                                         "Helpers main task is to keep the activity, revive channels and to clean them. Are you capable of that?"))
                                    await main.add_reaction(emojis[0])
                                    await main.add_reaction(emojis[1])
                                    try:
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0,
                                                                                 check=EmojisCheck)
                                    except asyncio.TimeoutError:
                                        await start.delete()
                                        await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                    else:
                                        if str(reaction.emoji) == emojis[0]:
                                            await channel.delete()
                                            await user.send(embed=func.Editable_E("Application Cancelled",
                                                                                  "Thanks for your participation",
                                                                                  "Cancelled"))
                                        elif str(reaction.emoji) == emojis[1]:
                                            capable = "Yes"
                                            await main.clear_reactions()

                                            final = discord.Embed(
                                                title=f"{user.name}'s Helper Application ({age.content})",
                                                colour=0xf7d17,
                                            )
                                            final.add_field(name="Your Timezone", value=timezone.content, inline=True)
                                            final.add_field(name="Activity", value=activity.content, inline=True)
                                            final.add_field(name="Manage Tasks", value=capable, inline=True)
                                            final.add_field(name="Reasoning", value=reason.content, inline=False)
                                            final.add_field(name="Teamwork", value=teamwork.content, inline=False)
                                            await main.edit(embed=final)
                                            await channel.send(
                                                f"Congratulations {user.mention} you're one step closer to becoming a helper here at **My Anime Land**\n\nPlease leave us upto 7 days to review your application, please refrain from pinging staff.\n\nThis channel will be deleted in 60 seconds")
                                            self.add_id(user)
                                            await asyncio.sleep(60)
                                            await channel.delete()
                                            applog = self.bot.get_channel(657965850057506827)
                                            await applog.send(embed=final)
            else:
                await ctx.message.delete()
                user = ctx.author
                await user.send(embed=func.ENoFooter("Hey!",
                                                     "You've already created an application in **My Anime Land**, so you cannot create another until that one has been completed."))


def setup(bot):
    bot.add_cog(Main(bot))
