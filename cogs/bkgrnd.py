import discord
import random
import secrets
import datetime
from discord.utils import get
from discord.ext import tasks, commands

class bkgrnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting.start()
        self.wordsplay.start()
        self.wyr.start()
        self.vip.start()
        self.network.start()

    def cog_unload(self):
        self.counting.cancel()
        self.wordsplay.cancel()
        self.wyr.cancel()
        self.vip.cancel()
        self.network.cancel()

    @tasks.loop(seconds=1)
    async def network(self):
        time = datetime.datetime.now().strftime("%I:%M:%S")
        if time == "08:00:00" or time == "02:00:00":
            guild = self.bot.get_guild(540784184470274069)
            netwrk = guild.get_channel(626749195318984704)
            embed = discord.Embed(color=0x00ffff, description="You can buy <@&636574850026176532> with 6k Tomi, and get access to VIP Chat!\nDM <@287343423088885771> to buy it!")
            await netwrk.send(embed=embed)

    @tasks.loop(seconds=1)
    async def vip(self):
        time = datetime.datetime.now().strftime("%I:%M:%S")
        if time == "08:00:00":
            guild = self.bot.get_guild(540784184470274069)
            vipchan = guild.get_channel(635780188021456896)
            emoji = get(guild.emojis, name="malRH")
            embed = discord.Embed(title="Hey cuties!", color=0x00ffff, description=f"Please don't share links for T5 or T6 cards outside this channel!\n\nEnjoy your time. {emoji}")
            await vipchan.send(embed=embed)

    @tasks.loop(seconds=1)
    async def counting(self):
        time = datetime.datetime.now().strftime("%M:%S")
        if time == "00:00":
            guild = self.bot.get_guild(540784184470274069)
            counting = guild.get_channel(604169947286863882)
            lastNumber = await counting.history(limit=1).flatten()
            previous = lastNumber[0].content
            try:
                number = int(previous)
                await counting.send(number+1)
            except Exception as e:
                print(e)

    @tasks.loop(seconds=1)
    async def wordsplay(self):
        time = datetime.datetime.now().strftime("%M:%S")
        if time == "00:00":
            guild = self.bot.get_guild(540784184470274069)
            words = guild.get_channel(548017507982901258)
            lastWord = await words.history(limit=1).flatten()
            previousW = lastWord[0].content[-1:]
            try:
                nextWord = secrets.whichLetter(previousW)
                await words.send(nextWord)
            except Exception as e:
                print(e)

    @tasks.loop(seconds=1)
    async def wyr(self):
        time = datetime.datetime.now().strftime("%I:%M:%S")
        if time == "08:00:00" or time == "02:00:00":
            guild = self.bot.get_guild(540784184470274069)
            wyr = guild.get_channel(653163640236539905)
            try:
                responses = ["First", "Second"]
                embed = discord.Embed(color=0x00ffff, description=f"**{random.choice(responses)} option!**\n\n{random.choice(secrets.wyrQuestions)}")
                first = get(guild.emojis, name="1_mal")
                second = get(guild.emojis, name="2_mal")
                msg = await wyr.send(embed=embed)
                await msg.add_reaction(first)
                await msg.add_reaction(second)
            except Exception as e:
                print(e)

def setup(bot):
    bot.add_cog(bkgrnd(bot))
