import discord
import gspread
import asyncio
import secrets
import dbfunctions
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

class Shifts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sheetcolor.start()

    async def cog_check(self, ctx):
        allowed = [542297369698369546, 542298007765516298, 600837848169578516, 600616093677125632, 652732584299593759, 611661848961351691]
        if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
            return True
        await ctx.send("I'm sorry. You don't have access to these commands. If you think this was a mistake, please contact an admin. or <@144051124272365569>")
        return False

    async def cog_command_error(self, ctx, error):
        await ctx.send(error, delete_after=10)

    def cog_unload(self):
        self.sheetcolor.cancel()

    def modperms(ctx):
        if 542297369698369546 in [y.id for y in ctx.author.roles]:
            return True
        elif 611661848961351691 in [y.id for y in ctx.author.roles]:
            return True
        elif 542298007765516298 in [y.id for y in ctx.author.roles]:
            return True
        else:
            return False

    @tasks.loop(minutes=1)
    async def sheetcolor(self):
        errorReport = ""
        statusColor = 0x00ff00
        guild = self.bot.get_guild(540784184470274069)
        statusLog = await guild.get_channel(663823411369476136).fetch_message(663824763747041290)
        statusEmbed = discord.Embed(title="Shifts Loop Status.", color=statusColor, description=errorReport)
        statusGoodEmbed.set_footer(text=f"Last updated: {timePrint()}")
        await statusLog.edit(embed=statusEmbed)
        print(datetime.now().strftime("%M"))
        try:
            if datetime.now().strftime("%M") == "55":
                # CONNECTING TO SHEET
                sheet = connectSheet("test")
                sheetNames = connectSheet("testNames")
                # CONNECTING TO SHEET

                # COLOR FORMAT DECLARATION
                fmt = cellFormat(backgroundColor=color(0.64, 0.76, 0.96))
                fmt2 = cellFormat(backgroundColor=color(0.71, 0.84, 0.66))
                # COLOR FORMAT DECLARATION

                # DATETIME OBJECT COLLECTION
                hour = (datetime.utcnow()+timedelta(hours=1)).strftime("%H:00")
                day = (datetime.utcnow()+timedelta(hours=1)).strftime("%A")
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
                format_cell_ranges(sheetNames, [(f'A1:AW10', fmt), (day, fmt2), (colorRange, fmt2)])
                # GOOGLE SHEET OPERATIONS

                iterableHours = []

                # SCANNING FOR UPCOMING SHIFTS
                for i in range(0, 7):
                    dateToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%A")
                    hourToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%H:00")
                    dateCell = sheet.find(dateToSearch).row
                    hourCell = sheet.find(hourToSearch).col
                    iterableHours.append([[dateCell, hourCell], [dateCell, hourCell+1]])
                guild = self.bot.get_guild(540784184470274069)
                index = 0
                firstShiftStaff = []
                shiftChannel = guild.get_channel(663591196089909263)
                shiftLogs = guild.get_channel(663590687840796710)
                for shift in iterableHours:
                    for cellCoords in shift:
                        try:
                            id = sheet.cell(cellCoords[0], cellCoords[1]).value
                            time = dbfunctions.dbselect("data.db", "SELECT time FROM shiftReminders WHERE ID=?", (id,))
                            member = guild.get_member(int(id))
                            if int(time) == index:
                                await member.send(f"You have a shift upcoming in {index} hours!")
                            if index == 0:
                                firstShiftStaff.append(member)
                        except Exception as e:
                            print(e)
                    if index == 0:
                        shiftMsg = await shiftChannel.send(f"{firstShiftStaff[0]} and {firstShiftStaff[1]}, Your shift is starting!")
                        await shiftMsg.add_reaction(secrets.checkmark)
                        await shiftMsg.add_reaction(secrets.crossmark)
                        def check1(reaction, user):
                            return user == firstShiftStaff[0] and str(reaction.emoji) == secrets.checkmark or user == firstShiftStaff[0] and str(reaction.emoji) == secrets.crossmark
                        def check2(reaction, user):
                            return user == firstShiftStaff[1] and str(reaction.emoji) == secrets.checkmark or user == firstShiftStaff[1] and str(reaction.emoji) == secrets.crossmark
                        incorrectEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0xff0000, description="Thank you for your response.")
                        #-------------------
                        timeoutEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0xffff00, description="No response received.")
                        timeoutEmbed.set_footer(text="20 Minutes had passed.")
                        #-------------------
                        correctEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0x00ff00, description="Glad to hear it. Enjoy your shift.")
                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=1200, check=check1)
                        except asyncio.TimeoutError:
                            await user.send(embed=timeoutEmbed, delete_after=60)
                            await shiftLogs.send(embed=timeoutEmbed)
                            return
                        else:
                #if the person reacts negatively
                            if str(reaction.emoji) == secrets.crossmark:
                                await user.send(embed=incorrectEmbed)
                                await shiftLogs.send(embed=incorrectEmbed)
                                return
                #if the person reacts positively
                            elif str(reaction.emoji) == secrets.checkmark:
                                await user.send(embed=correctEmbed)
                                await shiftLogs.send(embed=correctEmbed)
                                return
                        try:
                            reaction, user = await self.bot.wait_for("reaction_add", timeout=1200, check=check2)
                        except asyncio.TimeoutError:
                            await user.send(embed=timeoutEmbed, delete_after=300)
                            await shiftLogs.send(embed=timeoutEmbed)
                            return
                        else:
                #if the person reacts negatively
                            if str(reaction.emoji) == secrets.crossmark:
                                await user.send(embed=incorrectEmbed)
                                await shiftLogs.send(embed=incorrectEmbed)
                                return
                #if the person reacts positively
                            elif str(reaction.emoji) == secrets.checkmark:
                                await user.send(embed=correctEmbed)
                                await shiftLogs.send(embed=correctEmbed)
                                return
                    index += 1
                # SCANNING FOR UPCOMING SHIFTS
            elif datetime.now().strftime("%M") == "00":
                sheet = connectSheet("test")
                dateToSearch = (datetime.utcnow()-timedelta(hours=1)).strftime("%A")
                hourToSearch = (datetime.utcnow()-timedelta(hours=1)).strftime("%H:00")
                dateCell = sheet.find(dateToSearch).row
                hourCell = sheet.find(hourToSearch).col
                yesterHour = []
                lastShiftStaff = []
                yesterHour.append([[dateCell, hourCell], [dateCell, hourCell+1]])
                for shift in yesterHour:
                    for cellCoords in shift:
                        id = sheet.cell(cellCoords[0], cellCoords[1]).value
                        member = guild.get_member(int(id))
                        lastShiftStaff.append(member)
                confirmShiftMsg = await shiftChannel.send(f"{lastShiftStaff[0]} and {lastShiftStaff[1]} your shift is done!")
                await confirmShiftMsg.add_reaction(secrets.checkmark)
                await confirmShiftMsg.add_reaction(secrest.crossmark)
                def check1(reaction, user):
                    return user == firstShiftStaff[0] and str(reaction.emoji) == secrets.checkmark or user == firstShiftStaff[0] and str(reaction.emoji) == secrets.crossmark
                def check2(reaction, user):
                    return user == firstShiftStaff[1] and str(reaction.emoji) == secrets.checkmark or user == firstShiftStaff[1] and str(reaction.emoji) == secrets.crossmark
                incorrectEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0xff0000, description="Thank you for your response.")
                #-------------------
                timeoutEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0xffff00, description="No response received.")
                timeoutEmbed.set_footer(text="20 Minutes had passed.")
                #-------------------
                correctEmbed = discord.Embed(title=f"{user.name}#{user.discriminator}", colour=0x00ff00, description="Glad to hear it. Enjoy your shift.")
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=1200, check=check1)
                except asyncio.TimeoutError:
                    await user.send(embed=timeoutEmbed, delete_after=60)
                    await shiftLogs.send(embed=timeoutEmbed)
                    return
                else:
        #if the person reacts negatively
                    if str(reaction.emoji) == secrets.crossmark:
                        await user.send(embed=incorrectEmbed)
                        await shiftLogs.send(embed=incorrectEmbed)
                        return
        #if the person reacts positively
                    elif str(reaction.emoji) == secrets.checkmark:
                        await user.send(embed=correctEmbed)
                        await shiftLogs.send(embed=correctEmbed)
                        return
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=1200, check=check2)
                except asyncio.TimeoutError:
                    await user.send(embed=timeoutEmbed, delete_after=300)
                    await shiftLogs.send(embed=timeoutEmbed)
                    return
                else:
        #if the person reacts negatively
                    if str(reaction.emoji) == secrets.crossmark:
                        await user.send(embed=incorrectEmbed)
                        await shiftLogs.send(embed=incorrectEmbed)
                        return
        #if the person reacts positively
                    elif str(reaction.emoji) == secrets.checkmark:
                        await user.send(embed=correctEmbed)
                        await shiftLogs.send(embed=correctEmbed)
                        return
        except:
            statusBadEmbed = discord.Embed(title="Shifts Loop Status", color=0xff0000, description="There was a problem.")
            statusBadEmbed.set_footer(text=f"Last Updated: {timePrint()}")
            await statusLog.edit(embed=statusBadEmbed)
            print(Exception)

    @commands.group(name="shifts", usage="p^shifts", help="__ex: p^shifts__\n\nThis will show you your upcoming shifts")
    async def _shifts(self, ctx):
        if ctx.invoked_subcommand is None:
            maxShifts = dbfunctions.dbselect("data.db", "SELECT maxShifts FROM shiftReminders WHERE ID=?", (ctx.author.id,))
            halfShifts = int(maxShifts)/2
            member = ctx.author
            sheet = connectSheet("test")
            week = sheet.get_all_values()
            hours = 0
            days = []
            times = []
            hours24 = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23]
            for day in week:
                hourTime = 0
                for hour in day:
                    hourTime += 1
                    if str(member.id) in hour:
                        hours += 1
                        days.append(day[0])
                        input = hours24[hourTime]
                        times.append(input)
            layout = ""
            for newDay, newHour in zip(days, times):
                layout = layout + f"__{newDay}__: **{newHour}:00-{newHour+1}:00**\n"
            if hours <= halfShifts:
                color = 0xff0000
            elif hours < maxShifts:
                color = 0xffff00
            elif hours == maxShifts:
                color = 0x00ff00
            else:
                color = 0x00ffff
            embed = discord.Embed(title=f"Weekly Shifts.", color=color, description=f"{hours}/{maxShifts} hours accumulated.\n\n{layout}")
            embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
            await ctx.send(embed=embed)

    @_shifts.command(name="max", usage="p^shifts max <@member> <hours>", help="__ex: p^shifts max @BManRL#0001__\n\nThis will modify the maximum shifts someone can take.")
    async def _max(self, ctx, member: discord.Member, hours: int):
        dbfunctions.dbupdate("data.db", "UPDATE shiftReminders SET maxShifts=? WHERE ID=?", (hours, member.id,))
        embed = discord.Embed(title="Maximum Shifts Updated.", color=0x00ffff, description=f"Maximum shifts for {member.mention} have been updated to {hours}")
        await ctx.send(embed=embed)

    @_shifts.command(name="for", usage="p^shifts for <@member>", help="__ex: p^shifts for @BManRL#0001__\n\nThis will show you the mentioned members upcoming shifts")
    async def _for(self, ctx, member: discord.Member):
        sheet = connectSheet("test")
        week = sheet.get_all_values()
        hours = 0
        days = []
        times = []
        hours24 = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 23]
        for day in week:
            hourTime = 0
            for hour in day:
                hourTime += 1
                if str(member.id) in hour:
                    hours += 1
                    days.append(day[0])
                    input = hours24[hourTime]
                    times.append(input)
        layout = ""
        for newDay, newHour in zip(days, times):
            layout = layout + f"__{newDay}__: **{newHour}:00-{newHour+1}:00**\n"
        embed = discord.Embed(title=f"Weekly Shifts.", color=0x00ffff, description=f"{hours} hours accumulated.\n\n{layout}")
        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @_for.error
    async def _for_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(title="Permissions Failure.", color=0xff0000, description="I'm sorry, you don't have access for that. Shifts can be viewed on the [spreadsheet.](https://docs.google.com/spreadsheets/d/1Z6oE9pryOFxwQXkmmIedGng13nTSYo_ubUa4z6Rf5Dg/edit#gid=0)")
            await ctx.send(embed=embed, delete_after=30)
            await ctx.message.delete()

    @_shifts.command(name="upcoming", usage="p^shifts upcoming <hours>", help="__ex: p^shifts upcoming 5__\n\nThis will show the upcoming shifts (limited to 11 hours ahead and defaults to 2 hours.)")
    async def _upcoming(self, ctx, number: int = None):
        if number is None:
            number = 2
        elif number > 11:
            await ctx.message.delete()
            await ctx.send("Sorry! 11 is the maximum we can view at once!", delete_after=10)
            return
        await ctx.message.add_reaction("\U000023F3")
        msg = await ctx.send("Calculating...")
        sheet = connectSheet("test")
        iterableHours = []

        # GETS CELL NOTATION FOR UPCOMING SHIFTS
        for i in range(0, number+1):
            dateToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%A")
            hourToSearch = (datetime.utcnow()+timedelta(hours=i)).strftime("%H:00")
            dateCell = sheet.find(dateToSearch).row
            hourCell = sheet.find(hourToSearch).col
            iterableHours.append([[dateCell, hourCell], [dateCell, hourCell+1]])
        shiftGroups = []
        hourCount = 0
        for hours in iterableHours:
            shift1 = sheet.cell(hours[0][0], hours[0][1]).value
            shift2 = sheet.cell(hours[1][0], hours[1][1]).value
            shiftGroups.append([shift1, shift2])
            hourCount += 1
            await msg.edit(content=f"Calculating... Shift #{hourCount}")
        embed = discord.Embed(title="Upcoming Shifts", color=0x00ffff, description=f"This shows the shifts for the next {i} hours.")
        index = 1
        for shift in shiftGroups:
            if index < 2:
                title = "Now"
            else:
                title = f"{index-1} Hours away."
            shiftPop = []
            for person in shift:
                try:
                    member = ctx.guild.get_member(int(person))
                    shiftPop.append(member.mention)
                except:
                    shiftPop.append("-")
                if shiftPop == ["-", "-"]:
                    shiftPop = ["-\n-"]
            embed.add_field(name=title, value=' &\n'.join(shiftPop))
            index += 1
        await msg.delete()
        await ctx.message.clear_reactions()
        await ctx.send(embed=embed)
        # GETS CELL NOTATION FOR UPCOMING SHIFTS

    @_shifts.command(name="remove", usage="p^shifts remove <day> <hour>", help="__ex: p^shifts remove Monday 06:00__\n\nRemoves a shift.")
    async def _remove(self, ctx, day, hour):
        sheet = connectSheet("test")
        sheetNames = connectSheet("testNames")
        column = sheet.find(hour).col
        row = sheet.find(day.title()).row
        value = sheet.cell(row, column).value
        if value == str(ctx.author.id):
            sheet.update_cell(row, column, "")
            sheetNames.update_cell(row, column, "")
            await ctx.send("Your shift was removed.", delete_after=10)
        else:
            value2 = sheet.cell(row, column+1).value
            if value2 == str(ctx.author.id):
                sheet.update_cell(row, column+1, "")
                sheetNames.update_cell(row, column+1, "")
                await ctx.send("Your shift was removed.", delete_after=10)
            else:
                await ctx.send("You don't appear to be working at that time.", delete_after=10)

    @_shifts.command(name="add", usage="p^shifts add <day> <hour>", help="__ex: p^shifts add Monday 06:00__\n\nAdds a shift.")
    async def _add(self, ctx, day, hour):
        maxShifts = dbfunctions.dbselect("data.db", "SELECT maxShifts FROM shiftReminders WHERE ID=?", (ctx.author.id,))
        sheet = connectSheet("test")
        sheetNames = connectSheet("testNames")
        totalShifts = sheet.findall(ctx.author.id)
        if len(totalShifts) == maxShifts:
            await ctx.send("I'm sorry, but it appears you have already reached your maximum alotted shifts.")
            return
        if hour is None:
            row = sheet.find(day.title()).row
            shifts = sheet.row_values(row)[1:-1]
            shifts = ["<@{0}>".format(shift) for shift in shifts]
            mods, helpers = shifts[::2], shifts[1::2]
            layout = ""
            hours = ["0:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
            for hour, mod, helper in zip(hours, mods, helpers):
                layout = layout + f"**{hour}:** {mod} - {helper}\n"
            embed = discord.Embed(title=f"{day.title()}'s Schedule", color=0x00ffff, description=layout)
            await ctx.send(embed=embed)
            await ctx.send(f"{col1}\n{col2}")
        else:
            column = sheet.find(hour).col
            row = sheet.find(day.title()).row
            value = sheet.cell(row, column).value
            #EMBEDS
            incorrectEmbed = discord.Embed(title="No problem!", colour=0xff0000, description="Thank you for your interest.")
            #-------------------
            timeoutEmbed = discord.Embed(title="Sorry!", colour=0xffff00, description="Request timed out.")
            timeoutEmbed.set_footer(text="60 Seconds had passed.")
            #-------------------
            processing = discord.Embed(color=0xffff00, description="Adding your shift now...")
            #-------------------
            processDone = discord.Embed(color=0x00ff00, description="Your shift has been added.")
            processDone.set_footer(text="Thank you.")
            await ctx.message.delete()
            #-------------------
            if value is None or value == "":
                msg = await ctx.send(embed=processing)
                await msg.add_reaction("\U000023F3")
                sheet.update_cell(row, column, str(ctx.author.id))
                sheetNames.update_cell(row, column, str(ctx.author.name))
                await msg.clear_reactions()
                await msg.edit(embed=processDone, delete_after=15)
                await msg.add_reaction("\U00002705")
            else:
                if int(value) == ctx.author.id:
                    await ctx.send("You are already scheduled for this shift.", delete_after=5)
                    return
                value2 = sheet.cell(row, column+1).value
                addreact = False
                if value2 is None or value2 == "":
                    addreact = True
                    stringAdd = ", but they're alone. Would you like to take the shift with them?"
                else:
                    stringAdd = f" and <@{value2}>"
                askEmbed = discord.Embed(title="Shift conflict.", color=0xff0000, description=f"Shift already taken by <@{value}>{stringAdd}")
                msg = await ctx.send(embed=askEmbed)
                if addreact:
                    await msg.add_reaction("\U00002705")
                    await msg.add_reaction("\U0000274C")
                    #this waits to see which reaction they chose. (If any.)
                    def check(reaction, user):
                        return user == ctx.message.author and str(reaction.emoji) == secrets.checkmark or user == ctx.message.author and str(reaction.emoji) == secrets.crossmark
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
            #this happens on a timeout. (If there was no response)
                    except asyncio.TimeoutError:
                        await msg.edit(embed=timeoutEmbed, delete_after=15)
                        await msg.clear_reactions()
                        return
                    else:
            #if the person reacts negatively
                        if str(reaction.emoji) == secrets.crossmark:
                            await msg.edit(embed=incorrectEmbed, delete_after=5)
                            await msg.clear_reactions()
                            return
            #if the person reacts positively
                        elif str(reaction.emoji) == secrets.checkmark:
                            await msg.edit(embed=processing)
                            await msg.clear_reactions()
                            await msg.add_reaction("\U000023F3")
                            sheet.update_cell(row, column+1, str(ctx.author.id))
                            sheetNames.update_cell(row, column+1, str(ctx.author.name))
                            await msg.clear_reactions()
                            await msg.edit(embed=processDone, delete_after=15)
                            await msg.add_reaction("\U00002705")

    @_shifts.command(name="help")
    async def shifts_help(self, ctx, topic = None):
        allowed = [611661848961351691, 542297369698369546]
        helpEmbed = discord.Embed(title="**__p^shifts__**", color=0x00ffff, description="")
        if topic is None:
            if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
                helpEmbed.add_field(name="Commands", value="- **p^shifts**\n- **p^shifts for <@member>**\n- **p^shifts upcoming <hours>**\n- **p^shifts add <day> <hour>**\n- **p^shifts remove <day> <hour>**")
            else:
                helpEmbed.add_field(name="Commands", value="- **p^shifts**\n- **p^shifts upcoming <hours>**\n- **p^shifts add <day> <hour>**\n- **p^shifts remove <day> <hour>**", inline=False)
            helpEmbed.add_field(name="p^shifts", value="Shows you your shifts for the week.", inline=False)
            if len(set(allowed).intersection(set([y.id for y in ctx.author.roles]))) > 0:
                helpEmbed.add_field(name="p^shifts for <@member>", value="This will show you that persons shifts for the week.", inline=False)
            helpEmbed.add_field(name="p^shifts upcoming <hours>", value="Allows you to see ahead a few hours on the schedule. Limited to 11 hours ahead. (Shows 12 total)", inline=False)
            helpEmbed.add_field(name="p^shifts add <day> <hour>", value="Adds a shift to the weekly schedule.", inline=False)
            helpEmbed.add_field(name="p^shifts remove <day> <hour>", value="Removes a shift from the weekly schedule.", inline=False)
            await ctx.send(embed=helpEmbed)
        else:
            if topic.lower == "help":
                pass
            command = self.bot.get_command(f"shifts {topic}")
            helpEmbed.add_field(name=command.name, value=f"{command.usage}\n\n{command.help}")
            await ctx.send(embed=helpEmbed)

def connectSheet(name):
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("My Anime Land Activity").worksheet(name)
    return sheet

def timePrint(dtobject = None):
    if dtobject is None:
        dtobject = datetime.utcnow()
    return dtobject.strftime("%B %d, %Y | %I:%M%p")

def setup(bot):
    bot.add_cog(Shifts(bot))
