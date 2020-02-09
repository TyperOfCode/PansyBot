import discord
import random

from utils.essentials import secrets
from datetime import datetime
from discord.utils import get
from discord.ext import tasks, commands

class bkgrnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counting.start()
        self.wordsplay.start()
        self.wyr.start()

    def cog_unload(self):
        self.counting.cancel()
        self.wordsplay.cancel()
        self.wyr.cancel()

    @tasks.loop(minutes=30)
    async def counting(self):
        guild = self.bot.get_guild(540784184470274069)
        if guild:
            counting = self.bot.get_channel(604169947286863882)
            lastNumber = await counting.history(limit=1).flatten()
            if lastNumber[0].author.id == self.bot.user.id:
                return
            previous = lastNumber[0].content
            try:
                number = int(previous)
                await counting.send(number+1)
            except Exception as e:
                print(e)

    @tasks.loop(minutes=30)
    async def wordsplay(self):
        guild = self.bot.get_guild(540784184470274069)
        if guild:
            words = self.bot.get_channel(548017507982901258)
            lastWord = await words.history(limit=1).flatten()
            if lastWord[0].author.id == self.bot.user.id:
                return
            previousW = lastWord[0].content[-1:]
            try:
                nextWord = secrets.whichLetter(previousW)
                await words.send(nextWord)
            except Exception as e:
                print(e)

    @tasks.loop(hours=6)
    async def wyr(self):
        guild = self.bot.get_guild(540784184470274069)
        if guild:
            wyr = self.bot.get_channel(653163640236539905)
            option = await wyr.history(limit=1).flatten()
            if option[0].author.id == self.bot.user.id:
                return
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
