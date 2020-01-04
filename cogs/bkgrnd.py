import discord
import random
import secrets
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
from discord.utils import get
from discord.ext import tasks, commands

class bkgrnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sheetcolor.start()
        self.counting.start()
        self.wordsplay.start()
        self.wyr.start()
        self.vip.start()
        self.network.start()

    def cog_unload(self):
        self.sheetcolor.cancel()
        self.counting.cancel()
        self.wordsplay.cancel()
        self.wyr.cancel()
        self.vip.cancel()
        self.network.cancel()

    @tasks.loop(minutes=1)
    async def sheetcolor(self):
        sheet = connectSheet("test")
        # COLOR FORMAT DECLARATION
        fmt = cellFormat(backgroundColor=color(0.64, 0.76, 0.96))
        fmt2 = cellFormat(backgroundColor=color(0.71, 0.84, 0.66))
        # COLOR FORMAT DECLARATION

        # DATETIME OBJECT COLLECTION
        hour = datetime.utcnow().strftime("%H:00")
        day = datetime.utcnow().strftime("%A, %b %d")
        # DATETIME OBJECT COLLECTION

        # GOOGLE SHEET OPERATIONS
        daycell = sheet.find(day) # Finds day cell
        cell = sheet.find(hour) # Finds hour cell
        row = daycell.row # Row for day cell
        column = cell.col # Column for hour cell
        day = rowcol_to_a1(row, 1) # Day cell still (This is for formatting)
        hourCell1 = rowcol_to_a1(row, column) # 2 Cells beside each other.
        hourCell2 = rowcol_to_a1(row, column+1) # To accomodate for the hour.
        colorRange = f"{hourCell1}:{hourCell2}"
        format_cell_ranges(sheet, [(f'A1:AW10', fmt), (day, fmt2), (colorRange, fmt2)])
        # GOOGLE SHEET OPERATIONS

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
            if lastNumber[0].author.id == self.bot.user.id:
                return
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
            if lastWord[0].author.id == self.bot.user.id:
                return
            previousW = lastWord[0].content[-1:]
            try:
                nextWord = secrets.whichLetter(previousW)
                await words.send(nextWord)
            except Exception as e:
                print(e)

    @tasks.loop(seconds=1)
    async def wyr(self):
        time = datetime.datetime.now().strftime("%I:%M")
        if time == "08:00" or time == "02:00":
            guild = self.bot.get_guild(540784184470274069)
            wyr = guild.get_channel(653163640236539905)
            option = wyr.history(limit=1).flatten()
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

def connectSheet(name):
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("My Anime Land Activity").worksheet(name)
    return sheet

def setup(bot):
    bot.add_cog(bkgrnd(bot))
