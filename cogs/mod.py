import os
import time
import discord
import asyncio
from datetime import datetime, timedelta
import sqlite3

from discord.ext import commands, tasks
from utils.essentials import functions
from utils.essentials.functions import func


config = functions.get("utils/config.json")
start_time = time.time()

"""SQL data format: dbname = mod.db tablename= users sqlformat = userid bigint, main varchar(19), vc varchar(19), globe varchar(19), mute varchar(19), blacklist varchar(19)"""

class Mod(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.connect = sqlite3.connect('mod.db',isolation_level=None)
        self.cursor = self.connect.cursor()
        self.serverid = 540784184470274069

        self.mainrole = 574073241124208660
        self.vcrole = 590194178877685762
        self.globalrole = 574073241124208660
        self.muterole = 542728404693286912
        self.blacklistrole = 571926055817052190
        self.logchannel = 674977758794743843

        self.unpunish.start()

        
    async def sendlog(self, title, description, footer, color):
        channel = await self.bot.fetch_channel(self.logchannel)
        embed = discord.Embed(
            title = title,
            description= description,
            colour = color,
            timestamp=datetime.utcnow()
            )
        
        embed.set_footer(text=footer)

        try:
            await channel.send(embed=embed)
            return True
        except:
            return False

    def timeformat(self, st):
        """Formats time to seconds, eg: 1d = 3600 and 3d = 10800"""

        available_times = ['m','h','d','f','s']
        multiplier = [60,3600,86400,1]
        time = ''

        forever = False

        try:
            for i in st:
                try:
                    time += str(int(i))
                except:
                    if i == 'f':
                        forever = True
                    if i in available_times:
                        time += i
                        break
        except:
            return False
        
        if time == '':
            return False
        if forever:
            return 10**100

        for i, v in enumerate(available_times):
            if v in time:
                return int(time[:-1]) * multiplier[i]
            
        
            
        try:
            return int(time)
        except:
            pass

        
        return False

    def RegisterMember(self,member):
        """Adds the user to the DB if not already"""

        self.cursor.execute(f'SELECT * FROM users WHERE userid = {member.id}')
        if self.cursor.fetchone() == None:
            self.cursor.execute(f'''INSERT INTO users (userid)
            VALUES ({member.id})''')

            self.connect.commit()
            return False

        return True

    @commands.command(name='main')
    async def main(self, ctx, member : discord.Member = None, time = None, flag = None):
        
        """ p^Main command """

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return


        role = get(get(self.bot.guilds,id=self.serverid).roles,id=self.mainrole)

        if member  == None and time == None:
            await ctx.send(embed=func.eErr('Help Page','Usage: `p^main <@User> <time> (flags)`\n**__Flags__** ( Optional )\n**-undo** | removes the user\'s punishment\n**-minus** | Instead of adding the time, it minuses it\n**-replace** | replaces the current punishment time with the new time.\n\n**__time__**\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) ','main'))
            return

        if member == None:
            await ctx.send(embed=func.eErr('Invalid User','The member argument is not valid; Please mention a user\nEg: `p^main <@User> <time> (flags)`','Main'))
            return

        if time == '-undo' or time == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET main = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now has no (Main) Punishment!','Main'))

            await self.sendlog('User unpunished (main)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','Main',0x00FF00)
            return


        timeInSeconds = self.timeformat(time)
        if timeInSeconds == False:
            await ctx.send(embed=func.eErr('Invalid Time','The time argument is not valid.\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever)','Main'))
            return

    
        self.RegisterMember(member)

        if flag == '-undo' or flag == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET main = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed= func.sSc('Success!' ,f'The member {member.mention} now has no (Main) Punishment!','Main'))
            await self.sendlog('User unpunished (main)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','Main',0x00FF00)
            return

        if flag == '-minus' or flag == '-m':

            timeInSeconds = timeInSeconds * -1

        replace = False
        if flag == '-replace' or flag == '-r':
            replace = True

        if replace:
            self.cursor.execute(f'''
            UPDATE users
            SET main = '{datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

            date = datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (Main)','Main'))
            await self.sendlog('User punished (main)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','Main',0xff2424)
            return

        self.cursor.execute(f'SELECT main FROM users where userid = {member.id}')


        time = str(self.cursor.fetchone()[0])

        if time == 'None':
            date = datetime.utcnow()
        else:
            try:
                date = datetime.strptime(time,'%d/%m/%Y %H:%M:%S')
            except:
                date = datetime.utcnow()

        self.cursor.execute(f'''
        UPDATE users
        SET main = '{datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
        WHERE userid = {member.id}
        ''')

        self.connect.commit()

        await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

        date = datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
        await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (Main)','Main'))
        await self.sendlog('User punished (main)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','Main',0xff2424)
        
        return

    @commands.command(name='vc')
    async def vc(self, ctx, member : discord.Member = None, time = None, flag = None):
        
        """ p^vc command """

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return


        role = get(get(self.bot.guilds,id=self.serverid).roles,id=self.vcrole)

        if member  == None and time == None:
            await ctx.send(embed=func.eErr('Help Page','Usage: `p^vc <@User> <time> (flags)`\n**__Flags__** ( Optional )\n**-undo** | removes the user\'s punishment\n**-minus** | Instead of adding the time, it minuses it\n**-replace** | replaces the current punishment time with the new time.\n\n**__time__**\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) ','vc'))
            return

        if member == None:
            await ctx.send(embed=func.eErr('Invalid User','The member argument is not valid; Please mention a user\nEg: `p^vc <@User> <time> (flags)`','vc'))
            return

        if time == '-undo' or time == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET vc = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now has no (vc) Punishment!','vc'))

            await self.sendlog('User unpunished (vc)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','vc',0x00FF00)
            return


        timeInSeconds = self.timeformat(time)
        if timeInSeconds == False:
            await ctx.send(embed=func.eErr('Invalid Time','The time argument is not valid.\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever)','vc'))
            return

    
        self.RegisterMember(member)

        if flag == '-undo' or flag == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET vc = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed= func.sSc('Success!' ,f'The member {member.mention} now has no (vc) Punishment!','vc'))
            await self.sendlog('User unpunished (vc)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','vc',0x00FF00)
            return

        if flag == '-minus' or flag == '-m':

            timeInSeconds = timeInSeconds * -1

        replace = False
        if flag == '-replace' or flag == '-r':
            replace = True

        if replace:
            self.cursor.execute(f'''
            UPDATE users
            SET vc = '{datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

            date = datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (vc)','vc'))
            await self.sendlog('User punished (vc)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','vc',0xff2424)
            return

        self.cursor.execute(f'SELECT vc FROM users where userid = {member.id}')


        time = str(self.cursor.fetchone()[0])

        if time == 'None':
            date = datetime.utcnow()
        else:
            try:
                date = datetime.strptime(time,'%d/%m/%Y %H:%M:%S')
            except:
                date = datetime.utcnow()

        self.cursor.execute(f'''
        UPDATE users
        SET vc = '{datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
        WHERE userid = {member.id}
        ''')

        self.connect.commit()

        await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

        date = datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
        await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (vc)','vc'))
        await self.sendlog('User punished (vc)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','vc',0xff2424)
        
        return
    
    @commands.command(name='globe')
    async def globe(self, ctx, member : discord.Member = None, time = None, flag = None):
        
        """ p^globe command """

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return


        role = get(get(self.bot.guilds,id=self.serverid).roles,id=self.globerole)

        if member  == None and time == None:
            await ctx.send(embed=func.eErr('Help Page','Usage: `p^globe <@User> <time> (flags)`\n**__Flags__** ( Optional )\n**-undo** | removes the user\'s punishment\n**-minus** | Instead of adding the time, it minuses it\n**-replace** | replaces the current punishment time with the new time.\n\n**__time__**\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) ','globe'))
            return

        if member == None:
            await ctx.send(embed=func.eErr('Invalid User','The member argument is not valid; Please mention a user\nEg: `p^globe <@User> <time> (flags)`','globe'))
            return

        if time == '-undo' or time == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET globe = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now has no (globe) Punishment!','globe'))

            await self.sendlog('User unpunished (globe)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','globe',0x00FF00)
            return


        timeInSeconds = self.timeformat(time)
        if timeInSeconds == False:
            await ctx.send(embed=func.eErr('Invalid Time','The time argument is not valid.\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever)','globe'))
            return

    
        self.RegisterMember(member)

        if flag == '-undo' or flag == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET globe = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed= func.sSc('Success!' ,f'The member {member.mention} now has no (globe) Punishment!','globe'))
            await self.sendlog('User unpunished (globe)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','globe',0x00FF00)
            return

        if flag == '-minus' or flag == '-m':

            timeInSeconds = timeInSeconds * -1

        replace = False
        if flag == '-replace' or flag == '-r':
            replace = True

        if replace:
            self.cursor.execute(f'''
            UPDATE users
            SET globe = '{datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

            date = datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (globe)','globe'))
            await self.sendlog('User punished (globe)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','globe',0xff2424)
            return

        self.cursor.execute(f'SELECT globe FROM users where userid = {member.id}')


        time = str(self.cursor.fetchone()[0])

        if time == 'None':
            date = datetime.utcnow()
        else:
            try:
                date = datetime.strptime(time,'%d/%m/%Y %H:%M:%S')
            except:
                date = datetime.utcnow()

        self.cursor.execute(f'''
        UPDATE users
        SET globe = '{datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
        WHERE userid = {member.id}
        ''')

        self.connect.commit()

        await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

        date = datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
        await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (globe)','globe'))
        await self.sendlog('User punished (globe)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','globe',0xff2424)
        
        return

    @commands.command(name='mute')
    async def mute(self, ctx, member : discord.Member = None, time = None, flag = None):
        
        """ p^mute command """

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return


        role = get(get(self.bot.guilds,id=self.serverid).roles,id=self.muterole)

        if member  == None and time == None:
            await ctx.send(embed=func.eErr('Help Page','Usage: `p^mute <@User> <time> (flags)`\n**__Flags__** ( Optional )\n**-undo** | removes the user\'s punishment\n**-minus** | Instead of adding the time, it minuses it\n**-replace** | replaces the current punishment time with the new time.\n\n**__time__**\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) ','mute'))
            return

        if member == None:
            await ctx.send(embed=func.eErr('Invalid User','The member argument is not valid; Please mention a user\nEg: `p^mute <@User> <time> (flags)`','mute'))
            return

        if time == '-undo' or time == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET mute = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now has no (mute) Punishment!','mute'))

            await self.sendlog('User unpunished (mute)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','mute',0x00FF00)
            return


        timeInSeconds = self.timeformat(time)
        if timeInSeconds == False:
            await ctx.send(embed=func.eErr('Invalid Time','The time argument is not valid.\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever)','mute'))
            return

    
        self.RegisterMember(member)

        if flag == '-undo' or flag == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET mute = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed= func.sSc('Success!' ,f'The member {member.mention} now has no (mute) Punishment!','mute'))
            await self.sendlog('User unpunished (mute)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','mute',0x00FF00)
            return

        if flag == '-minus' or flag == '-m':

            timeInSeconds = timeInSeconds * -1

        replace = False
        if flag == '-replace' or flag == '-r':
            replace = True

        if replace:
            self.cursor.execute(f'''
            UPDATE users
            SET mute = '{datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

            date = datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (mute)','mute'))
            await self.sendlog('User punished (mute)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','mute',0xff2424)
            return

        self.cursor.execute(f'SELECT mute FROM users where userid = {member.id}')


        time = str(self.cursor.fetchone()[0])

        if time == 'None':
            date = datetime.utcnow()
        else:
            try:
                date = datetime.strptime(time,'%d/%m/%Y %H:%M:%S')
            except:
                date = datetime.utcnow()

        self.cursor.execute(f'''
        UPDATE users
        SET mute = '{datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
        WHERE userid = {member.id}
        ''')

        self.connect.commit()

        await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

        date = datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
        await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (mute)','mute'))
        await self.sendlog('User punished (mute)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','mute',0xff2424)
        
        return

    @commands.command(name='blacklist')
    async def blacklist(self, ctx, member : discord.Member = None, time = None, flag = None):
        
        """ p^blacklist command """

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return


        role = get(get(self.bot.guilds,id=self.serverid).roles,id=self.blacklistrole)

        if member  == None and time == None:
            await ctx.send(embed=func.eErr('Help Page','Usage: `p^blacklist <@User> <time> (flags)`\n**__Flags__** ( Optional )\n**-undo** | removes the user\'s punishment\n**-minus** | Instead of adding the time, it minuses it\n**-replace** | replaces the current punishment time with the new time.\n\n**__time__**\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) ','blacklist'))
            return

        if member == None:
            await ctx.send(embed=func.eErr('Invalid User','The member argument is not valid; Please mention a user\nEg: `p^blacklist <@User> <time> (flags)`','blacklist'))
            return

        if time == '-undo' or time == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET blacklist = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now has no (blacklist) Punishment!','blacklist'))

            await self.sendlog('User unpunished (blacklist)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','blacklist',0x00FF00)
            return


        timeInSeconds = self.timeformat(time)
        if timeInSeconds == False:
            await ctx.send(embed=func.eErr('Invalid Time','The time argument is not valid.\nEg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever)','blacklist'))
            return

    
        self.RegisterMember(member)

        if flag == '-undo' or flag == '-u':
            self.cursor.execute(f'''
            UPDATE users
            SET blacklist = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason=f'User Responsible: {ctx.author}')

            await ctx.send(embed= func.sSc('Success!' ,f'The member {member.mention} now has no (blacklist) Punishment!','blacklist'))
            await self.sendlog('User unpunished (blacklist)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','blacklist',0x00FF00)
            return

        if flag == '-minus' or flag == '-m':

            timeInSeconds = timeInSeconds * -1

        replace = False
        if flag == '-replace' or flag == '-r':
            replace = True

        if replace:
            self.cursor.execute(f'''
            UPDATE users
            SET blacklist = '{datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

            date = datetime.strftime(datetime.utcnow() + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
            await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (blacklist)','blacklist'))
            await self.sendlog('User punished (blacklist)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','blacklist',0xff2424)
            return

        self.cursor.execute(f'SELECT blacklist FROM users where userid = {member.id}')


        time = str(self.cursor.fetchone()[0])

        if time == 'None':
            date = datetime.utcnow()
        else:
            try:
                date = datetime.strptime(time,'%d/%m/%Y %H:%M:%S')
            except:
                date = datetime.utcnow()

        self.cursor.execute(f'''
        UPDATE users
        SET blacklist = '{datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')}'
        WHERE userid = {member.id}
        ''')

        self.connect.commit()

        await member.add_roles(role,reason=f'User Responsible: {ctx.author}')

        date = datetime.strftime(date + timedelta(seconds=timeInSeconds),'%d/%m/%Y %H:%M:%S')
        await ctx.send(embed=func.sSc('Success!' ,f'The member {member.mention} now is punished until `{date}` (blacklist)','blacklist'))
        await self.sendlog('User punished (blacklist)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Punished until: {date}` \n**Moderator:** `{ctx.author}`\n**Moderator ID:** `{ctx.author.id}`','blacklist',0xff2424)
        
        return


    @commands.command(name='modhelp',aliases=['mhelp'])
    async def modhelp(self,ctx):

        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return

        helppage = """
        `p^modhelp` - Shows this page.
        `p^check <@User>` - checks the user for any punishment.

        `p^main` - subjects a user to the "main" punishment role
        `p^vc` - subjects a user to the "vc" punishment role
        `p^globe` - subjects a user to the "global" punishment role
        `p^mute` - subjects a user to the "mute" punishment role
        `p^blacklist` - subjects a user to the "blacklist" punishment role

        **All punishment commands have the same format:**
        Example: `p^mute <@User> <time> (flags)`
        **Do not include <> or (). <> meaning necessary, () meaning optional.**

        **__Flags__** ( Optional )
        **-undo,-u** | removes the user\'s punishment
        **-minus,-m** | Instead of adding the time, it minuses it
        **-replace,-r** | replaces the current punishment time with the new time.
        
        **__Time__**
        Eg: `1d, 34m, f` (m = Minutes, h = Hour, d = Day,f = Forever) 
        """.replace('        ','')
        
        embed = discord.Embed(
            title = 'Moderator Help Page',
            description=helppage,
            colour = 0x00FF00,
            timestamp=datetime.utcnow()
            )
        embed.set_footer(text='Mod Help Page')

        await ctx.send(embed=embed)
        return

    @commands.command(name='check')
    async def check(self,ctx, member : discord.Member = None):
        if not await check.is_helper_role(self,ctx):
            await ctx.send(embed=func.NoPerm())
            return
            
        if member == None:
            await ctx.send(embed=func.eErr('Please mention a user','Usage: `p^check <@User>` Do not include <>','Check'))
            return
        
        self.cursor.execute(f'SELECT main, vc, globe, mute, blacklist FROM users WHERE userid = {member.id}')
        user = self.cursor.fetchone()


        out = lambda x : f'Punished until {x}' if x is not None and str(x).replace(' ','') is not '' else 'No punishment'
        outf = lambda x : True if x is not None and str(x).replace(' ','') is not '' else False

        if user == None or not (outf(user[0]) or outf(user[1]) or outf(user[2]) or outf(user[3]) or outf(user[4])):
            embed = discord.Embed(
                description='This user has no punishment',
                colour = 0x00FF00,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text='Check')

            await ctx.send(embed=embed)
            return

        output = f"""
        **User: {member} | {member.id} \'s punishent:**

        MAIN: `{out(user[0])}`
        VC: `{out(user[1])}`
        GLOBE: `{out(user[2])}`
        MUTE: `{out(user[3])}`
        BLACKLIST: `{out(user[4])}`
        """

        embed = discord.Embed(
            description=output,
            colour = 0x00FF00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text='Check')
        await ctx.send(embed=embed)
        return
            
    @tasks.loop(seconds=1)
    async def unpunish(self):

        self.cursor.execute(f'SELECT userid, main, vc, globe, mute, blacklist FROM users')
        users = self.cursor.fetchall()


        timeup_main = []
        timeup_vc = []
        timeup_globe = []
        timeup_mute = []
        timeup_blacklist = []

        for i in users:
            for num, value in enumerate(i):

                if num == 0:
                    continue

                try:
                    date = datetime.strptime(value,'%d/%m/%Y %H:%M:%S')
                except:
                    continue

                if date < datetime.utcnow():

                    if num == 1:
                        timeup_main.append(i[0])
                    elif num == 2:
                        timeup_vc.append(i[0])
                    elif num == 3:
                        timeup_globe.append(i[0])
                    elif num == 4:
                        timeup_mute.append(i[0])
                    elif num == 5:
                        timeup_blacklist.append(i[0])
                    else:
                        pass

        try:
            guild = self.bot.get_guild(self.serverid)
        except:
            return

        if guild == None:
            return

        role = get(guild.roles,id=self.mainrole)
        for user in timeup_main:

            member = get(guild.members,id = int(user))
            if member == None:
                continue

            self.cursor.execute(f'''
            UPDATE users
            SET main = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason='Time was up')
            await self.sendlog('User unpunished (main)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `Time was Up`\n**Moderator ID:** `Time was Up`','Main',0x00FF00)

        role = get(guild.roles,id=self.vcrole)
        for user in timeup_vc:

            member = get(guild.members,id = int(user))
            if member == None:
                continue

            self.cursor.execute(f'''
            UPDATE users
            SET vc = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason='Time was up')
            await self.sendlog('User unpunished (vc)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `Time was Up`\n**Moderator ID:** `Time was Up`','vc',0x00FF00)

        role = get(guild.roles,id=self.globerole)
        for user in timeup_globe:

            member = get(guild.members,id = int(user))
            if member == None:
                continue

            self.cursor.execute(f'''
            UPDATE users
            SET globe = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason='Time was up')
            await self.sendlog('User unpunished (globe)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `Time was Up`\n**Moderator ID:** `Time was Up`','globe',0x00FF00)

        role = get(guild.roles,id=self.muterole)
        for user in timeup_mute:

            member = get(guild.members,id = int(user))
            if member == None:
                continue

            self.cursor.execute(f'''
            UPDATE users
            SET mute = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason='Time was up')
            await self.sendlog('User unpunished (mute)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `Time was Up`\n**Moderator ID:** `Time was Up`','Mute',0x00FF00)

        role = get(guild.roles,id=self.blacklistrole)
        for user in timeup_blacklist:

            member = get(guild.members,id = int(user))
            if member == None:
                continue

            self.cursor.execute(f'''
            UPDATE users
            SET blacklist = ''
            WHERE userid = {member.id}
            ''')

            self.connect.commit()

            await member.remove_roles(role,reason='Time was up')
            await self.sendlog('User unpunished (blacklist)',f'**Member**: `{member}` - `{member.id}`\n**Action:** `Unpunished`\n**Moderator:** `Time was Up`\n**Moderator ID:** `Time was Up`','blacklist',0x00FF00)


            
        


        


        

        
        


        

        
        

        




    
def setup(bot):
    bot.add_cog(Mod(bot))
