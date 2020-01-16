import discord
import random
import secrets
import gspread
from datetime import datetime
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

    def cog_unload(self):
        self.sheetcolor.cancel()
        self.counting.cancel()
        self.wordsplay.cancel()
        self.wyr.cancel()

    @tasks.loop(minutes=1)
    async def sheetcolor(self):
        if datetime.now().strftime("%M") == "00":
            # CONNECTING TO SHEET
            sheet = connectSheet("test")
            # CONNECTING TO SHEET

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
            hourCell1 = rowcol_to_a1(row, column) # [2 Cells beside each other.
            hourCell2 = rowcol_to_a1(row, column+1) # To accomodate for the hour.]
            colorRange = f"{hourCell1}:{hourCell2}"
            format_cell_ranges(sheet, [(f'A1:AW10', fmt), (day, fmt2), (colorRange, fmt2)])
            # GOOGLE SHEET OPERATIONS

            iterableHours = []

            # SCANNING FOR UPCOMING SHIFTS
            for i in range(0, 6):
                dateToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%A, %b %d")
                hourToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%H:00")
                dateCell = sheet.find(dateToSearch).row
                hourCell = sheet.find(hourToSearch).col
                iterableHours.append([dateCell, hourCell], [dateCell, hourCell+1])
            await ctx.send(iterableHours)
            # SCANNING FOR UPCOMING SHIFTS

            # INSERTING NEW DAY FOR THE SCHEDULE
            if datetime.utcnow().strftime("%H:%M") == "00:00":
                insertedDay = (datetime.utcnow()+timedelta(days=6)).strftime("%A, %b %d")
                sheet.insert_row(values=[insertedDay], index=2, value_input_option="RAW")
            else:
                pass
            # INSERTING NEW DAY FOR THE SCHEDULE

    @tasks.loop(hours=1)
    async def counting(self):
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

    @tasks.loop(hours=1)
    async def wordsplay(self):
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

    @tasks.loop(hours=6)
    async def wyr(self):
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
