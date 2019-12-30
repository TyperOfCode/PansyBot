import discord
from datetime import datetime
from discord.ext import commands
import asyncio
import sqlite3
import dbfunctions
import secrets
from discord.utils import get

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apply")
    async def _apply(self, ctx):
        incorrectEmbed = discord.Embed(title="No problem!", colour=0xff0000, description="Thank you for your interest.")
        #-------------------
        timeoutEmbed = discord.Embed(title="Sorry!", colour=0xffff00, description="Request timed out.")
        timeoutEmbed.set_footer(text="60 Seconds had passed.")
        #-------------------
        nextQuestion = discord.Embed(title="Thank you.", color=0x00ff00, description="Next question.")
        #-------------------
        if ctx.message.guild is not None and ctx.channel.id != 660474909339680788:
            await ctx.message.delete()
            dmEmbed = discord.Embed(title="Sorry!", color=0xff0000, description="you can only use the apply command in the \n<#660474909339680788> channel.")
            await ctx.author.send(embed=dmEmbed)
        else:
            if ctx.guild is None:
                ctx.guild = self.bot.get_guild(540784184470274069)
            applyCheck = dbfunctions.dbselect("data.db", "SELECT ID FROM applied WHERE ID=?", (ctx.author.id,))
            if applyCheck is not None:
                await ctx.author.send("It appears you have already applied. If you feel this message was sent in error, notify one of the staff members.")
                return
            secrets.ignore.append(ctx.author.id)
            #Asks if you want to apply? Followed by 2 reactions for Yes, or No.
            embed = discord.Embed(title="Hello!", color=0x00ffff, description="Would you like to apply to be a helper for **My Anime Land** Discord server?")
            start = await ctx.author.send(embed=embed)
            await start.add_reaction(secrets.checkmark)
            await start.add_reaction(secrets.crossmark)
            #this waits to see which reaction they chose. (If any.)
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == secrets.checkmark or user == ctx.message.author and str(reaction.emoji) == secrets.crossmark
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
    #this happens on a timeout. (If there was no response)
            except asyncio.TimeoutError:
                await start.delete()
                await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                return
            else:
    #if the person reacts negatively
                if str(reaction.emoji) == secrets.crossmark:
                    await start.delete()
                    await ctx.author.send(embed=incorrectEmbed, delete_after=5)
                    return
    #if the person reacts positively
                elif str(reaction.emoji) == secrets.checkmark:
                    await start.delete()
                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        ctx.author: discord.PermissionOverwrite(read_messages=True)
                    }
                    channel = await ctx.guild.create_text_channel(name=f"temp-app-{ctx.author.id}", overwrites=overwrites)
                    correctEmbed = discord.Embed(title="Excellent!", colour=0x00ff00, description=f"We'll start the application!\n\nPlease join this channel:\n{channel.mention}")
                    await ctx.author.send(embed=correctEmbed, delete_after=30)
                    ageQuestion = discord.Embed(title="Question #1", color=0x00ffff, description="How old are you?")
                    msg = await channel.send(embed=ageQuestion)
    #This waits to see if there was a message sent
                    def agecheck(message):
                        return message.author == ctx.author
                    try:
                        age = await self.bot.wait_for("message", timeout=60, check=agecheck)
    #If there is no response after 60 seconds on the age question
                    except asyncio.TimeoutError:
                        await channel.delete()
                        await ctx.author.send(embed=timeoutEmbed)
                        return
                    else:
    #if the message received was a number
                        if age.content.isdigit() and int(age.content) > 12 and int(age.content) < 65:
                                pass
                        else:
    #if the message received was not a number
                            wrongAge = discord.Embed(title="Invalid Entry", color=0xff0000, description="Please use numbers only. (17, 19, 21 etc...)")
                            await msg.edit(embed=wrongAge)
                            await deleteNewest(channel)
                            await asyncio.sleep(5)
                            try:
                                await msg.edit(embed=ageQuestion)
                                age = await self.bot.wait_for("message", timeout=60, check=agecheck)
                            except asyncio.TimeoutError:
    #if the message timed out from no response
                                await msg.edit(embed=timeoutEmbed, delete_after=60)
                                await channel.delete()
                                return
                            else:
    #if the number received for a second time was a number
                                if age.content.isdigit() and int(age.content) > 12 and int(age.content) < 65:
                                        pass
    #if it wasn't a number for the second time.
                                else:
                                    quitEmbed = discord.Embed(title="Invalid Entry.", color=0xff0000, description="Please try the application process again.")
                                    await ctx.author.send(embed=quitEmbed, delete_after=30)
                                    await channel.delete()
                                    return
                        await msg.edit(embed=nextQuestion)
                        await deleteNewest(channel)
                        await asyncio.sleep(2)
                        tzEmbed = discord.Embed(title="What timezone are you in?", color=0x00fffff, description="""type N/A if you don't want to reveal that.""")
                        await msg.edit(embed=tzEmbed)
                        try:
                            tz = await self.bot.wait_for("message", timeout=60, check=agecheck)
                        except asyncio.TimeoutError:
                            await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                            await channel.delete()
                            return
                        else:
                            await msg.edit(embed=nextQuestion)
                            await deleteNewest(channel)
                            await asyncio.sleep(2)
                            activityEmbed = discord.Embed(title="How active can you be daily?", color=0x00ffff)
                            activityEmbed.set_footer(text="For example: 30m, 2h, etc...")
                            await msg.edit(embed=activityEmbed)
                            try:
                                active = await self.bot.wait_for("message", timeout=60, check=agecheck)
                            except asyncio.TimeoutError:
                                await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                await channel.delete()
                                return
                            else:
                                await msg.edit(embed=nextQuestion)
                                await deleteNewest(channel)
                                await asyncio.sleep(2)
                                interestEmbed = discord.Embed(title="Why are you interested in this position?", color=0x00ffff)
                                await msg.edit(embed=interestEmbed)
                                try:
                                    interest = await self.bot.wait_for("message", timeout=60, check=agecheck)
                                except asyncio.TimeoutError:
                                    await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                    await channel.delete()
                                    return
                                else:
                                    await msg.edit(embed=nextQuestion)
                                    await deleteNewest(channel)
                                    await asyncio.sleep(2)
                                    expectEmbed = discord.Embed(color=0x00ffff, description="Our system for moderation is to make pairs of mods and helpers. Each helper should be associated to work on a category, and we expect a fixed time of activity daily in that category. We expect you to be interactive and helpful, and to cover up for your teammates when they need you. Is this possible for you?")
                                    await msg.edit(embed=expectEmbed)
                                    await msg.add_reaction(secrets.checkmark)
                                    await msg.add_reaction(secrets.crossmark)
                                    try:
                                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                            #this happens on a timeout. (If there was no response)
                                    except asyncio.TimeoutError:
                                        await msg.clear_reactions()
                                        await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                        await channel.delete()
                                        return
                                    else:
                            #if the person reacts negatively
                                        if str(reaction.emoji) == secrets.crossmark:
                                            await msg.clear_reactions()
                                            await ctx.author.send(embed=incorrectEmbed, delete_after=15)
                                            await channel.delete()
                                            return
                            #if the person reacts positively
                                        elif str(reaction.emoji) == secrets.checkmark:
                                            await msg.clear_reactions()
                                            await msg.edit(embed=nextQuestion)
                                            await asyncio.sleep(2)
                                            emoji1 = get(ctx.guild.emojis, name="1_mal")
                                            emoji2 = get(ctx.guild.emojis, name="2_mal")
                                            emoji3 = get(ctx.guild.emojis, name="3_mal")
                                            emoji4 = get(ctx.guild.emojis, name="4_mal")
                                            emoji5 = get(ctx.guild.emojis, name="5_mal")
                                            emoji6 = get(ctx.guild.emojis, name="6_mal")
                                            emoji7 = get(ctx.guild.emojis, name="7_mal")
                                            emoji8 = get(ctx.guild.emojis, name="8_mal")
                                            categoryEmbed = discord.Embed(title="Which Category would you like to be assigned to?", color=0x00ffff, description=
                                            f"""
                                            {emoji1} Main Chat (Channel)
                                            {emoji2} The Rest of The General Category
                                            {emoji3} Animanga Category
                                            {emoji4} Topic
                                            {emoji5} Fun
                                            {emoji6} Clubs
                                            {emoji7} Bots
                                            {emoji8} Voice Channels
                                            """)
                                            emojis = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8]
                                            await msg.edit(embed=categoryEmbed)
                                            for emoji in emojis:
                                                await msg.add_reaction(emoji)
                                            def reactCheck(reaction, user):
                                                return user == ctx.message.author
                                            try:
                                                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=reactCheck)
                                    #this happens on a timeout. (If there was no response)
                                            except asyncio.TimeoutError:
                                                await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                                await channel.delete()
                                                return
                                            else:
                                                if reaction.emoji.id == emoji1.id:
                                                    cate = "Main Chat (Channel)"
                                                elif reaction.emoji.id == emoji2.id:
                                                    cate = "The Rest of The General Category"
                                                elif reaction.emoji.id == emoji3.id:
                                                    cate = "Animanga Category"
                                                elif reaction.emoji.id == emoji4.id:
                                                    cate = "Topic"
                                                elif reaction.emoji.id == emoji5.id:
                                                    cate = "Fun"
                                                elif reaction.emoji.id == emoji6.id:
                                                    cate = "Clubs"
                                                elif reaction.emoji.id == emoji7.id:
                                                    cate = "Bots"
                                                elif reaction.emoji.id == emoji8.id:
                                                    cate = "Voice Channel"
                                                await msg.clear_reactions()
                                                await msg.edit(embed=nextQuestion)
                                                await asyncio.sleep(2)
                                                helperEmbed = discord.Embed(color=0x00ffff, description="Helpers main task is to keep the activity, revive channels and to clean them. Are you capable of that?")
                                                await msg.edit(embed=helperEmbed)
                                                await msg.add_reaction(secrets.checkmark)
                                                await msg.add_reaction(secrets.crossmark)
                                                def check(reaction, user):
                                                    return user == ctx.message.author and reaction.emoji == secrets.checkmark or user == ctx.message.author and str(reaction.emoji) == secrets.crossmark
                                                try:
                                                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                                        #this happens on a timeout. (If there was no response)
                                                except asyncio.TimeoutError:
                                                    await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                                    await channel.delete()
                                                    return
                                                else:
                                                    if str(reaction.emoji) == secrets.crossmark:
                                                        await ctx.author.send(embed=incorrectEmbed, delete_after=15)
                                                        await channel.delete()
                                                        return
                                        #if the person reacts positively
                                                    elif str(reaction.emoji) == secrets.checkmark:
                                                        await msg.clear_reactions()
                                                        await msg.edit(embed=nextQuestion)
                                                        await asyncio.sleep(2)
                                                        applicationEmbed = discord.Embed(title="Please confirm this application", color=0x00ffff, description=f"Age: {age.content}\nTimezone: {tz.content}\nActivity: {active.content}\nReason for applying: {interest.content}\nCategory: {cate}")
                                                        applicationEmbed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}'s Application", icon_url=ctx.author.avatar_url)
                                                        await msg.edit(embed=applicationEmbed)
                                                        await msg.add_reaction(secrets.checkmark)
                                                        await msg.add_reaction(secrets.crossmark)
                                                        try:
                                                            reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                                                #this happens on a timeout. (If there was no response)
                                                        except asyncio.TimeoutError:
                                                            await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                                            await channel.delete()
                                                            return
                                                        else:
                                                            if str(reaction.emoji) == secrets.crossmark:
                                                                await ctx.author.send(embed=incorrectEmbed, delete_after=5)
                                                                await channel.delete()
                                                                return
                                                #if the person reacts positively
                                                            elif str(reaction.emoji) == secrets.checkmark:
                                                                await msg.clear_reactions()
                                                                confirmEmbed = discord.Embed(title="Thank you for your time.", color=0x00ff00, description="This application will be forwarded to the Moderation team, and someone will reach out to you if you are a good fit.")
                                                                await msg.edit(embed=confirmEmbed, delete_after=30)
                                                                secrets.ignore.remove(ctx.author.id)
                                                                appchan = ctx.guild.get_channel(660474909339680788)
                                                                appl = await appchan.send(embed=applicationEmbed)
                                                                await appl.add_reaction(secrets.checkmark)
                                                                await appl.add_reaction(secrets.crossmark)
                                                                dbfunctions.dbupdate("data.db", "INSERT INTO applied (ID) VALUES (?)", (ctx.author.id,))
                                                                await asyncio.sleep(15)
                                                                await channel.delete()

async def deleteNewest(channel):
    targetMsg = await channel.history(limit=1).flatten()
    await targetMsg[0].delete()

def setup(bot):
    bot.add_cog(Applications(bot))
