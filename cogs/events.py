import discord
from discord.ext import commands
import dbfunctions
import secrets
import string
from datetime import datetime
from discord.utils import get
from random import randint

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            ids = dbfunctions.dbselectmore("data.db", "SELECT ID FROM shiftReminders", ())
            members = []
            for id in ids:
                #print(f"member = ctx.guild.get_member({id})")
                member = before.guild.get_member(id)
                #print(f"members.append({member})")
                members.append(member)
            for member in members:
                if 652732584299593759 in [y.id for y in member.roles]:
                    dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (5, after.id,))
                elif 600837848169578516 in [y.id for y in member.roles]:
                    dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (18, after.id,))
                elif 542298007765516298 in [y.id for y in member.roles]:
                    dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (12, after.id,))

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if before.premium_subscription_count < after.premium_subscription_count:
            boosters1 = before.premium_subscribers
            boosters2 = after.premium_subscribers
            boosters3 = set(boosters1).symmetric_difference(set(boosters2))
            bman = after.get_member(144051124272365569)
            await bman.send(f"{boosters3} boosted {after.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == 656491562682810386:
            if str(payload.emoji) == "\U00002705":
                if payload.user_id != 655481681741873152:
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    if message.author.id != 231463189487943690:
                        await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = self.bot.get_guild(540784184470274069)
        people = format(len(guild.members), ",")
        watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
        await self.bot.change_presence(activity=watch)

        emojilist = '<a:yayhyper:658788790432956427> <:malyuSip:649269848047747092> <a:malYesss:613541344182272020> <a:malYayHyper:608280367744548880> <a:malYay:608280367580971017> <a:malWoop:610632031600115778> <:malwow:614525816360927233> <a:malWoahh:609048816963944448> <:malWoah:607837460470300683> <:malWoa:642018486654074922> <:malWinku:607838396349677568> <:malWinku:642018488344510464> <:malWelcome:665073482576691220> <a:malWH:629149080198578186> <a:malWaveDesu:610430770565087242> <a:malWave:658382330829996032> <:maluwuHeart:593137542904283145> <:MalUwU:658389108967604296> <a:maluwu:610632031696584724> <a:malThumbsUp:608280367312404481> <:malthonkblush:658035176424603678> <a:MalStars:612406936435949569> <a:malStar1:614619624268365829> <:malSparklyHeart:653605730452111361> <a:malSoHappy:618125323048976434> <a:malSnuggles:608278538554179584> <:malRaphiThumbsup:597527997838393353> <a:malpotatoeshuggle:608280365987135501> <a:malPikaDance:608688666528841728> <:malPeek:608687928087937024> <:malPatu:607838010125320192> <a:malPatu:608278537623044097> <a:malNya:608280365718831124> <a:malnya:608688667078295557> <a:malNods:608278535705985044> <a:malNekoPeek:608280368961028096> <a:malNekoDance:608280366066958346> <:malmegucomfy:599753428054573059> <:malmitsurilaugh:639656343577559040> <a:malJoins:609864729015353344> <a:malLoves:608278539128537088> <:malLoveDesu:613538787024437249> <a:malMaruFly:610632033710112788> <:malKokoroYay:640425181638164534> <a:malKittyYayR:640479986695929866> <a:malKittyYayL:640479984573743115>'.split(' ')
        randemg = emojilist[randint(0,len(emojilist)-1)]
        if ':' not in randemg:
            randemg = '<a:yayhyper:658788790432956427>'
        print(f'Welcome = {not (len(guild.members) % 2) == 0}')
        if not (len(guild.members) % 2) == 0:
            channel = get(guild.text_channels,id=542291426051096606)
            #embed = discord.Embed(title=f'Welcome to My Anime Land, {member.mention}.',color=0xff00e1,description=f'Read <#607634761586049075> and introduce yourself <#661259788759597076> {randemg}')
            await channel.send(f'**Welcome to My Anime Land {member.mention}!**\n> Read <#607634761586049075> and introduce yourself <#661259788759597076> {randemg}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = self.bot.get_guild(540784184470274069)
        people = format(len(guild.members), ",")
        watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
        await self.bot.change_presence(activity=watch)


    

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            if message.content.startswith("p^apply"):
                secrets.ignore.append(message.author.id)
            ignore = secrets.ignore
            if message.author.id not in ignore:
                guild = self.bot.get_guild(540784184470274069)
                modmail = guild.get_channel(656491562682810386)
                member = guild.get_member(message.author.id)
                embed = discord.Embed(title=f"DM Received", color=0x00ffff, description=f"ID: {member.id} | {member.mention}")
                embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
                embed.add_field(name="Account Created:", value=printTime(member.created_at))
                embed.add_field(name="Joined MAL:", value=printTime(member.joined_at))
                if message.content != "" and message.attachments != []:
                    embed.add_field(name="Message Content:", value=message.content, inline=False)
                    embed.add_field(name="Image Sent:", value="⠀")
                    embed.set_image(url=message.attachments[0].url)
                elif message.content == "" and message.attachments != []:
                    embed.add_field(name="Image Sent:", value="⠀")
                    embed.set_image(url=message.attachments[0].url)
                elif message.attachments == [] and message.content != "":
                    embed.add_field(name="Message Content:", value=message.content, inline=False)
                msg = await modmail.send(embed=embed)
                await msg.add_reaction("\U00002705")
            else:
                pass
        else:
            if len(message.mentions) > 0:
                dmEmbed = discord.Embed(title="You were mentioned.", color=0xff0000, description=f"Server: {message.guild.name}\nCategory: {message.channel.category.name}\nChannel: {message.channel.name}")
                dmEmbed.add_field(name="Jump Link", value=f"[Click Here]({message.jump_url})", inline=False)
                dmEmbed.add_field(name="Message:", value=message.content)
                dmEmbed.set_footer(text=printTime())
                bman = message.guild.get_member(144051124272365569)
                nanami = message.guild.get_member(231463189487943690)
                kely = message.guild.get_member(583421490024808457)
                if bman in message.mentions:
                    if secrets.afkBMan:
                        await message.channel.send("Sorry. BMan is currently afk... I sent them a DM for you, they'll get back to you as soon as possible!")
                    emote = get(message.guild.emojis, name="malwow")
                    await message.add_reaction(emote)
                    await bman.send(embed=dmEmbed)
                if kely in message.mentions:
                    emote = get(message.guild.emojis, name="malkokoroWahaha")
                    await message.add_reaction(emote)
                if nanami in message.mentions:
                    if secrets.afkNanami:
                        await message.channel.send("Sorry. Nanami is currently afk... I sent them a DM for you, they'll get back to you as soon as possible!")
                    await nanami.send(embed=dmEmbed)
                else:
                    pass
        if message.content == "<@!655481681741873152> prefix":
            if "developer" in [y.name.lower() for y in message.author.roles] or message.author.id == 144051124272365569:
                prefix = dbfunctions.dbselect("data.db", "SELECT prefix FROM information", ())
                await message.channel.send(f"My current prefix is set to: `{prefix}`")
        elif message.content.startswith("<@!655481681741873152> prefix "):
            if "developer" in [y.name.lower() for y in message.author.roles] or message.author.id == 144051124272365569:
                newprefix = message.content[30:]
                dbfunctions.dbupdate("data.db", "UPDATE information SET prefix=?", (newprefix,))
                #print("Updated prefix")
                await message.channel.send(f"My prefix has been updated to: `{newprefix}`")
        if message.channel.id == 542291426051096606 or message.channel.id == 622449628083912705:
            if "bye" in message.content.lower() or "bai" in message.content.lower():
                emote = get(message.guild.emojis, name="malWaveDesu")
                await message.add_reaction(emote)
        if message.channel.id == 660474909339680788: #Applications
            bypass = [231463189487943690, 655481681741873152]
            if message.author.id not in bypass:
                await message.delete()
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
                    new = int(previous)+1
                    if number != new:
                        await message.delete()
                except:
                    await message.delete()
        if message.channel.id == 548017507982901258:
            if message.author.id != self.bot.user.id:
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

def printTime(stamp = None):
    if stamp is None:
        stamp = datetime.now()
    return stamp.strftime("%B %d, %Y | %I:%M:%S%p GMT")

def setup(bot):
    bot.add_cog(Events(bot))
