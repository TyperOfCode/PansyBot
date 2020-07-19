import asyncio
import json

import discord
from discord.ext import commands, tasks
from discord.utils import get

import random
from datetime import datetime, timedelta

from utils.jsonhandler import js
from utils.embedfuncs import EmbedFuncs
import os
import string
import requests

import operator
import traceback


## TODO
"""
Squads system is extremely messy and unorganised, With a lot of holes and reasons to go wrong, IN the future hopefully we can recode this better. 
The Coding level displayed in this document is of amatuer standards. FIXME
"""



class Squads(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.filename = 'sqdata'

        self.squadpath = f'{self.filename}/squads/'
        self.userpath = f'{self.filename}/users/'

        self.confpath = f'{self.filename}/confdata.json'

        self.serverid = 540784184470274069

        self.dataindent = 4

        self.logsid = 693806099551485963
        self.lb = 684855120906813464
        

        self.sq_leader = 683448380537831432
        self.sq_member = 683448302024523823

        self.admin = 542297369698369546
        self.flower = 669728759951261697

        self.sq_cat = 684763587910303807

        self.yes_em = 657275749249712195
        self.no_em  = 657275797228486682

        self.everyonerole = 540784184470274069

        self.hypesquad_emote_switch = {
            "brilliance" : "<:HypeSquadBrilliance:720270426206371931>",
            "balance" : "<:HypeSquadBalance:720270426114228315>",
            "bravery" : "<:HypeSquadBravery:720270426407698477>"
        }

        self.postad_webhook_url = "https://canary.discordapp.com/api/webhooks/699260738124120204/XK6t9KBC9a7Q54Rue3JuxXq7s1lbTZIBLCqFE1RhbDwOBncKRqnnguMLnRKqoKqH3hD9"
        self.winner_update_webhook = "https://canary.discordapp.com/api/webhooks/727382772976582717/7WrEGZDw2Z37WCqVRIylbcvZqsj8DssVpqrQWJ7YW7iDHddETxD_O0a1kL5dzJ5RENLv"


        self.update_activated_squads.start()
        self.update_nicknames.start()
        self.update_squad_counts.start()
        self.update_temp_chans.start()
        #self.on_missing_leader.start()

        self.update_today.start()

    def cog_unload(self):
        self.update_activated_squads.cancel()
        self.update_nicknames.cancel()
        self.update_squad_counts.cancel()
        self.update_temp_chans.cancel()
        #self.on_missing_leader.cancel()

        self.update_today.cancel()

    def _getrolefrommain(self, id_):
        main =  self.bot.get_guild(self.serverid)

        return get(main.roles,id=id_)
        
    def _getchannelfrommain(self,id_):
        main =  self.bot.get_guild(self.serverid)

        return get(main.channels,id=id_)

    def _getmemberfrommain(self,id_):
        main = self.bot.get_guild(self.serverid)
        
        return get(main.members,id=id_)

    async def _sendtologs(self, **kwargs):
        try:
            content = kwargs['content']
        except:
            content = ''
            pass
        try:
            embed = kwargs['embed']
        except:
            embed = ''
            pass


        channel = self._getchannelfrommain(self.logsid)

        await channel.send(content=content,embed=embed)

    def _isadmin(self, user):
        return self.admin in [i.id for i in user.roles] or self.flower in [i.id for i in user.roles] 

    def _dmcheck(self, ctx):
        return isinstance(ctx.channel, discord.DMChannel) #and ctx.author.id in [636808158521589770, 231463189487943690, 343019667511574528]

    def _timetostr(self, time):
        return datetime.strftime(time,'%d/%m/%Y %H:%M:%S')

    def _strtotime(self, sttime):
        try:
            return datetime.strptime(sttime,'%d/%m/%Y %H:%M:%S')
        except:
            return datetime.utcnow() - timedelta(weeks=64)

    def _set_create_time(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        dat['last_made_squad'] = self._timetostr(datetime.utcnow())

        hand.write(dat,indent=self.dataindent)
    
    def _set_join_time(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        dat['last_joined_squad'] = self._timetostr(datetime.utcnow())

        hand.write(dat, indent=self.dataindent)

    def _set_postad_time(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        dat['last_post_ad'] = self._timetostr(datetime.utcnow())

        hand.write(dat, indent=self.dataindent)

    def _set_invite_time(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        dat['last_invite'] = self._timetostr(datetime.utcnow())

        hand.write(dat, indent=self.dataindent)

    def _is_on_create_cooldown(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        if dat == {}:
            return False

        if not self._strtotime(dat['last_made_squad']) + timedelta(weeks=1) > datetime.utcnow() :
            return False
        else:
            return True

    def _is_on_join_cooldown(self, ctx=None, hand=None,user=None):
        if ctx == None:
            uid = user.id

        else:
            uid = ctx.author.id

        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{uid}.json')

        dat = hand.grab()

        if dat == {}:
            return False

        if not self._strtotime(dat['last_joined_squad'])  + timedelta(days=3) > datetime.utcnow() :
            return False
        else:
            return True

    def _is_on_postad_cooldown(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        if dat == {}:
            return (False,0)

        if not self._strtotime(dat['last_post_ad']) + timedelta(minutes=30) > datetime.utcnow() :
            return (False,0)
        else:
            return (True, (self._strtotime(dat['last_post_ad']) + timedelta(minutes=30)) - datetime.utcnow())

    def _is_on_invite_cooldown(self, ctx, hand=None):
        if hand == None or not isinstance(hand, js.config):
            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

        dat = hand.grab()

        if dat == {}:
            return False

        if not self._strtotime(dat['last_joined_squad']) + timedelta(seconds=30) > datetime.utcnow() :
            return False
        else:
            return True

    def _create_squad(self, squadword, squadname, squadleader,squadleaderid=0,hypesquad=0):

       
        if squadleaderid == 0:
            squadleaderid = squadleader.id

        fil = open(f'{self.squadpath}{squadname.lower()}.json','w').close()
        hand = js.config(f'{self.squadpath}{squadname.lower()}.json')
        
        dat = hand.grab()

        dat['squadname'] = squadname
        dat['squadsuffix'] = squadword
        dat['created_on'] = self._timetostr(datetime.utcnow())
        dat['member_count'] = 1
        dat['day_messages'] = 0
        dat['day_voice'] = 0
        dat['total_messages'] = 0
        dat['total_voice'] = 0
        dat['members'] = [squadleaderid]
        dat['leader'] = squadleaderid
        dat['points'] = 0
        dat['founder'] = squadleaderid
        dat['squad_channel'] = 0
        dat['private'] = False
        dat['activated'] = False
        dat['desc'] = ''
        dat['image']= ''
        dat['exiled'] = []
        dat['channel_allow'] = False
        dat['supervisors'] = []
        dat['hypesquad'] = random.choice(['balance','brilliance','bravery']) if hypesquad == 0 else hypesquad
        hand.write(dat, indent=self.dataindent)
        return

    def _create_user(self, user):
        if user.bot:
            return 'bot'
        if os.path.exists(f'{self.userpath}{user.id}.json'):
            return
        

        fil = open(f'{self.userpath}{user.id}.json','w').close()
        hand = js.config(f'{self.userpath}{user.id}.json')
        
        dat = hand.grab()

        dat['total_messages'] = 0
        dat['total_voice'] = 0
        dat['today_message'] = 0
        dat['today_voice'] = 0
        dat['squad_name'] = "0"
        dat['last_made_squad'] = self._timetostr(datetime.utcnow() - timedelta(days=365))
        dat['last_message'] = self._timetostr(datetime.utcnow() - timedelta(days=365))
        dat['last_joined_squad'] = self._timetostr(datetime.utcnow() - timedelta(days=365))
        dat['last_post_ad'] = self._timetostr(datetime.utcnow() - timedelta(days=365))
        dat['last_invite'] = self._timetostr(datetime.utcnow() - timedelta(days=365))
        dat['last_left'] = '0'
        dat['update_messages'] = 0
        dat['update_voice'] = 0
        dat['toggle_nick'] = True


        hand.write(dat, indent=self.dataindent)
        return

    async def _activatesquad(self, squadname):
        spath = f'{self.squadpath}{squadname.lower()}.json'
        if not os.path.exists(spath):
            return False

        hand = js.config(spath)

        dat = hand.grab()

        if dat['member_count'] >= 4:
            

            try:
                leader = self._getmemberfrommain(dat['leader'])

                content=f'> :tada: {leader.mention} **{squadname} {dat["squadsuffix"]}** Has now been activated! '
                channel = self._getchannelfrommain(self.logsid)

                await channel.send(content=content)

                dat= hand.grab()
                dat['activated'] = True


                hand.write(dat,indent=self.dataindent)


            except Exception as e:
                print(e)
                return False

            return True

        dat= hand.grab()
        dat['activated'] = False
        hand.write(dat,indent=self.dataindent)
        
        return False

    def _isactivated(self, squadname):   
        spath = f'{self.squadpath}{squadname.lower()}.json'
        if not os.path.exists(spath):
            return False

        hand = js.config(spath)

        dat = hand.grab()

        if dat['activated']:
            return True

        return False

    def _squad_exists(self, name=None):

        if name != None:
            spath = f'{self.squadpath}{name.lower()}.json'
            if not os.path.exists(spath):
                return False
            return True
                    
        return False

    def _quickset_user(self,userid,obj,value):
        
        hand = js.config(f'{self.userpath}{userid}.json')
        dat = hand.grab()

        dat[obj] = value

        hand.write(dat,indent=self.dataindent)

    class _C():
        pink = 0xff0ff3
        orange = 0xFF4500

    @commands.group(name="squad", case_insensitive=True)
    async def squad(self, ctx):
        if self._dmcheck(ctx):
            return

    ##TODO
    """
        - Redesign needed
    """
    @squad.command(name='help')
    async def sq_help(self, ctx):
        if self._dmcheck(ctx):
            return

        if self._create_user(ctx.author) == "bot":
            return



        page = """
        `<>` - **means the argument is __necessary__**
        `[]` - **means the argument is __optional__**

        `h.squad help` : Shows this page
        `h.squad create` : Creates a Squad
        `h.squad join <Squad's Exact Name>` : Joins the Squad
        `h.squad leave` : Leaves the squad you are in
        `h.squad stats [Squad name]` : Shows stats for the squad 
        `h.squad user [@User]` : Shows stats for that user
        `h.squad list` : Shows the squad leaderboard
        `h.squad members [Squad Name]` : Shows the members of the squad
        `h.squad counters` : Shows all the active counters
        `h.squad nick` : Toggles whether to have your clan nickname or not


        """.replace('       ','')

        hand = js.config(f'{self.userpath}{ctx.author.id}.json')
        udat = hand.grab()
        if udat["squad_name"] != "0":
                
            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()
            

            if sdat['leader'] == ctx.author.id or ctx.author.id in sdat['supervisors']:
                page += """
                **-- Squad leader commands --**

                `h.squad leader <@User>` : Transfers leadership of a squad
                `h.squad description <description>` : Sets the description of the squad
                `h.squad image <url>` : sets an image for the squad 
                `h.squad private` : Toggles invite only squads.
                `h.squad addSupervisor <@User>` : adds the person as a supervisor of your squad.
                `h.squad removeSupervisor <@User>` : removes the person from being a supervisor of your squad.
                `h.squad postad` : Posts your squad's advertisment to <#684764188740026407> ***+supervisor***
                `h.squad kick <@User>` : Kicks a user from the squad. ***+supervisor***
                `h.squad exile <@User>` : Bans the user from your squad ***+supervisor***
                `h.squad unexile <@User>` : Unbans the user from your squad. ***+supervisor***
                `h.squad invite <@User>` : Invites the member to the squad. ***+supervisor***\n\n
                """.replace('                ','')
            

        if self._isadmin(ctx.author):
            page += '**-- Admin Commands --**\n`h.squad addp <squadname> <points>` : Adds/Rems points to that squad\n`h.squad reset <squadname>` : Resets all data for that squad\n`h.squad setobject <squad> <objectname> <value>` : Sets an object value (dangerous)\n`h.squad enablecounter <#channel> <duration>` : Enables counting of that channel for a duration of time.\n`h.squad permcount <#channel>` : Permanently sets the channel as eligble for message counting.\n`h.squad allowchannel <squadName>` : Toggles whether or not the squad can have a channel. Default: False'




        await ctx.send(embed=EmbedFuncs.SuccessEM('Squad Help',page,footer='Squad Help'))
    
    ##TODO
    """
        - This Command looks absolutely horrid inside, please FIXME, needs a complete rework
    """
    @squad.command(name='create')
    async def sq_create(self, ctx):
        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            nameerror = 'Squad Create error'

            if 660174109501554717 not in [i.id for i in ctx.author.roles]:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You don\'t have the verified role to create a squad!**\n**To get the Verified role, introduce yourself at** <#661259788759597076>', footer=nameerror) ) 
                return
            

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

            dat = hand.grab()

            if dat != {}:
                if dat['squad_name'] != "0":
                    await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'re already in a squad!**',footer=nameerror) )
                    return

            if self._is_on_create_cooldown(ctx,hand):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'ve already made a squad within the last 7 days**'))
                return

            hanamsg = await ctx.send(embed=EmbedFuncs.cEm('Squad Create','**What would you like to name your squad?**\n\n(This is the first part of your squad title, only write the **__name__**. `name` ~~`suffix`~~) ',color=self._C.pink,footer='(Dont include the word "squad" in it)'))

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for('message',check=check,timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return

            if any([True for i in ["squad","gang","band","group","clan","club","league"] if i.lower() in msg.content.lower()]):
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror, '**Woops!** Seems like you got a bit confused!\n\nThis is not the name of the entire squad title.\n`name` `suffix`, Example: `Bunny` `Squad`, You should only write "Bunny" in this stage, but of course with your own squad name.\n\n**[Squad Creation Cancelled]**'))
                return

            if len(msg.content) > 15 or "." in msg.content or msg.content.replace(' ','') == '':
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,f'**The name must be less than 15 Characters and must not contain `.` and cannot only consist of spaces!**\n**This name has:** `{len(msg.content)}` Characters.\n\n[Squad Creation Cancelled]'))
                return
            

            if self._squad_exists(msg.content):
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,f'**The name `{msg.content}` is already taken, please try again!**\n\n[Squad Creation Cancelled]'))
                return

            squad_name = msg.content

            await hanamsg.edit(embed=EmbedFuncs.cEm(f'Squad Create',f'**Are you sure you want your squad name to be `{squad_name}` **',color=self._C.pink, footer='Are you sure?'))
            
            def check(r,u):
                return u == ctx.author and (r.emoji.id == self.yes_em or r.emoji.id == self.no_em)

            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.yes_em))
            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.no_em))

            try:
                reaction , user = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return

            if reaction.emoji.id == self.no_em:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM('Cancelled','Squad creation cancelled','Cancel'))
                return

            nums = {
                '1' : 658785745804328980,
                '2' : 658785722265894932,
                '3' : 658785706201579570,
                '4' : 658785651881410573,
                '5' : 658785634479243315,
                '6' : 658785616120643604,
                '7' : 658785597804249117,
                '8' : 658785573598920741
            }
            await hanamsg.clear_reactions()
            await hanamsg.edit(embed=EmbedFuncs.cEm(f'Wait',f'Please wait while we add the necessary emojis...',color=self._C.orange, footer='Wait'))

            store = []

            for i in nums:
                store.append(nums[i])
                await hanamsg.add_reaction(get(ctx.guild.emojis,id=nums[i]))


            
            await hanamsg.edit(embed=EmbedFuncs.cEm(f'Squad Create',f'**Despite calling them Squads you\'re free use different names too, Which word would you like to choose to represent you?\neg. if you chose `6` your squad will be called `{squad_name} League`**\n\n<a:1_mal:658785745804328980> - Squad\n<a:2_mal:658785722265894932> - Gang\n<a:3_mal:658785706201579570> - Group\n<a:4_mal:658785651881410573> - Clan\n<a:5_mal:658785634479243315> - Club\n<a:6_mal:658785616120643604> - League\n<a:7_mal:658785597804249117> - Band\n<a:8_mal:658785573598920741> - Family', color=self._C.pink, footer='Suffix choose'))
            def check(r,u):

                return u == ctx.author and r.emoji.id in store

            try:    
                reaction , user = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return

            numswitch = {
                nums['1'] : 'Squad',
                nums['2'] : 'Gang',
                nums['3'] : 'Group',
                nums['4'] : 'Clan',
                nums['5'] : 'Club',
                nums['6'] : 'League',
                nums['7'] : 'Band',
                nums['8'] : 'Family'
            }

            squad_suffix = numswitch[reaction.emoji.id]
            await hanamsg.clear_reactions()

            nums = {
                '1' : 658785745804328980,
                '2' : 658785722265894932,
                '3' : 658785706201579570
            }
           
            await hanamsg.edit(embed=EmbedFuncs.cEm(f'Squad Create',f'What hypesquad would you like **{squad_name} {squad_suffix}** to be?\n\n**1.** Brilliance <:HypeSquadBrilliance:720270426206371931>\n**2.** Bravery <:HypeSquadBravery:720270426407698477>\n**3.** Balance <:HypeSquadBalance:720270426114228315>', color=self._C.pink, footer='Suffix choose'))
            
            
            store = []
            for i in nums:
                store.append(nums[i])
                await hanamsg.add_reaction(get(ctx.guild.emojis,id=nums[i]))



            def check(r,u):
                return u == ctx.author and r.emoji.id in store
            

            try:
                reaction , usr = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return



            squadswitch = {
                nums['1'] : 'brilliance',
                nums['2'] : 'bravery',
                nums['3'] : 'balance'
            }

            self._create_squad(squad_suffix, squad_name, ctx.author, hypesquad=squadswitch[reaction.emoji.id])
            await hanamsg.clear_reactions()

            await hanamsg.edit(content=f'> :white_check_mark: Finished! `Create Squad for user: {ctx.author}({ctx.author.id})` With hypesquad: `{squadswitch[reaction.emoji.id]}`',embed=None)

            await self._sendtologs(embed=EmbedFuncs.SuccessEM(':rocket: Squad Created',f'**Name**: `{squad_name} {squad_suffix}`\n**Founder**: `{ctx.author}` (`{ctx.author.id}`)\n**Channel of creation:** {ctx.channel.mention}',footer='Squad Create'))
            
            await ctx.send(embed=EmbedFuncs.SuccessEM(f'Successfully made {squad_suffix}',f'**Successfully added your new {squad_suffix} to our database!**\n\n**If you would like to activate it, you must get at least 4 members to join!**'))
            
            self._quickset_user(ctx.author.id, "squad_name", squad_name)

            self._set_create_time(ctx)
            self._set_join_time(ctx)

            await ctx.author.add_roles(self._getrolefrommain(self.sq_leader))
            await ctx.author.add_roles(self._getrolefrommain(self.sq_member))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Create',f'Encountered unprecedented error on Squad Create\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Create Error')) 
            return

    ##TODO
    """
    """
    @squad.command(name='join')
    async def sq_join(self, ctx, *, name=None):
        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad Join Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')

            user = hand.grab()
            if name == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**You must specify a squad name!** Usage: `squad join <squadname>`'))
                return
            
            name = name.strip()

            if not self._squad_exists(name.lower()):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,f'**The Squad `{name}` doesnt exist!**'))
                return

            if user['squad_name'] != "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'re already in a squad!** use `squad leave` to leave!'))
                return
            
            squadhand = js.config(f'{self.squadpath}{name.lower()}.json')

            squaddat = squadhand.grab()

            if squaddat['private'] == True:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**This Squad is Private! Please get the squad leader to invite you**'))
                return

            if ctx.author.id in squaddat['exiled']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**You\'ve been exiled from this squad!**'))
                return


            hanamsg = await ctx.send(f'**Are you sure you want to join: "{squaddat["squadname"]} {squaddat["squadsuffix"]}", you wont be able to leave for 3 days.**')
            def check(r,u):
                return u == ctx.author and (r.emoji.id == self.yes_em or r.emoji.id == self.no_em)

            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.yes_em))
            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.no_em))

            try:
                reaction , user = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return

            if reaction.emoji.id == self.no_em:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM('Cancelled','Squad Join cancelled','Cancel'))
                return


            
            try:
                if user['toggle_nick']:

                    newnick = ctx.author.display_name + f" | {squaddat['squadname']} {squaddat['squadsuffix']}"
                    if len(newnick) > 32:
                        raise ValueError

                    await ctx.author.edit(nick=newnick)
            except:
                pass

            squaddat = squadhand.grab()

            squaddat["member_count"] += 1
            squaddat['members'].append(ctx.author.id)
            if squaddat['member_count'] == 4:
                await self._activatesquad(squaddat['squadname'])

            squadhand.write(squaddat,indent=self.dataindent)

            self._set_join_time(ctx)

            self._quickset_user(ctx.author.id, "squad_name", squaddat['squadname'])

            await hanamsg.clear_reactions()
            
            await ctx.author.add_roles(self._getrolefrommain(self.sq_member))

            await ctx.send(embed=EmbedFuncs.SuccessEM('Successfully Joined Squad!',f'You have successfully joined the **{squaddat["squadname"]} {squaddat["squadsuffix"]}**'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Join',f'Encountered unprecedented error on Squad Join\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Join Error')) 
            return
    
    ##TODO
    """
    """
    @squad.command(name='leave')
    async def sq_leave(self, ctx, flags=None):
        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad leave Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            user = hand.grab()

            if not flags == "-f" and self._isadmin(ctx.author):
                if self._is_on_join_cooldown(ctx):
                    await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**You recently joined a squad in the past `3` days, please wait at least `3` days since you last joined the squad to leave it.**'))
                    return


            if user['squad_name'] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'re not in a squad!**'))
                return

            name = user['squad_name']
            
            squadhand = js.config(f'{self.squadpath}{name.lower()}.json')

            squaddat = squadhand.grab()

            if squaddat["leader"] == ctx.author.id:
                def check(m):
                    return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() in ['!agree','!no']

                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**If you leave the squad as a leader, the squad will be deleted.**\n\nType: `!agree` **To delete your Squad**\n:warning: **This action is permanent and cannot be reversed** :warning:\nType `!no` to cancel this process'))
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=20)
                except asyncio.TimeoutError:
                    await ctx.send(embed=EmbedFuncs.ErrorEM("Squad Delete Timed Out",f'The deletion of the {squaddat["squadname"]} {squaddat["squadsuffix"]} has been cancelled.','Timed Out'))
                    return

                if msg.content.lower() == '!agree':

                    members = squaddat['members']
                    for i in members:
                        uhan = js.config(f'{self.userpath}{i}.json')
                        udat = uhan.grab()

                        udat['squad_name'] = "0"
                        uhan.write(udat,indent=self.dataindent)    

                        user = self._getmemberfrommain(i)

                        newnick = f" | {squaddat['squadname']} {squaddat['squadsuffix']}"
                        newnick = user.display_name.replace(newnick,'')
                        try:
                            await user.edit(nick=newnick)        
                            await user.remove_roles(self._getrolefrommain(self.sq_member))    
                        except:
                            pass


                    os.remove(f'{self.squadpath}{name.lower()}.json')

                    ### REMOVED 2
                    #chan = self._getchannelfrommain(squaddat["squad_channel"])
                    #if chan != None:
                    #    await chan.delete()

                    chan = self._getchannelfrommain(squaddat["squad_channel"])
                    if chan != None:
                        everyone = self._getrolefrommain(self.everyonerole)
                        overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024))}
                        if chan.overwrites != overwrites:
                            await chan.edit(overwrites = overwrites)
                        
                    await ctx.author.remove_roles(self._getrolefrommain(self.sq_leader))
                    await ctx.send(embed=EmbedFuncs.ErrorEM("Squad Deleted","You left your squad, and it has been disbanded. This action is permanent.","Squad Deleted."))
                else:
                    await ctx.send(embed=EmbedFuncs.ErrorEM("Cancelled","Squad Deletion has been cancelled.","Cancelled."))
                return

            try:
                squaddat['members'].remove(ctx.author.id)
            except:
                pass
            squaddat['member_count'] -= 1

            self._quickset_user(ctx.author.id, "squad_name", "0")

            try:
                await ctx.author.edit(nick=self.display_name.replace(f" | {squaddat['squadname']} {squaddat['squadsuffix']}",''))
            except:
                pass

            squadhand.write(squaddat,indent=self.dataindent)

            await ctx.author.remove_roles(self._getrolefrommain(self.sq_member))

            await ctx.send(embed=EmbedFuncs.SuccessEM('Successfully Left Squad',f'You\'ve successfully left the **{squaddat["squadname"]} {squaddat["squadsuffix"]}**'))
            return

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Leave',f'Encountered unprecedented error on Squad Leave\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Leave Error')) 
            return
            
    
    @squad.command(name='nick')
    async def sq_nick(self, ctx):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad nick Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()


            if udat['toggle_nick']:
                udat['toggle_nick'] = False
                hand.write(udat,indent=self.dataindent)

               
                newnick = f" | {sdat['squadname']} {sdat['squadsuffix']}"
                newnick = ctx.author.display_name.replace(newnick,'')

                try:
                    await ctx.author.edit(nick=newnick)
                except:
                    pass
                await ctx.send(embed=EmbedFuncs.SuccessEM('Toggled Squad Nickname',':white_check_mark: Your nickname is now free of having your squad name.'))
                
            else:
                
                newnick = f" | {sdat['squadname']} {sdat['squadsuffix']}"
                if newnick in ctx.author.display_name:
                    pass
                else:   
                    newnick = ctx.author.display_name + newnick
                    if len(newnick) > 32:
                        await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, ':white_check_mark: Your nickname is too long, so it will remain unforced.'))
                        return

                udat['toggle_nick'] = True
                hand.write(udat,indent=self.dataindent)

                try:

                    await ctx.author.edit(nick=newnick)
                except:
                    pass
                await ctx.send(embed=EmbedFuncs.SuccessEM('Toggled Squad Nickname',':white_check_mark: Your nickname will now be forced with your squad name.'))
                

            
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad nick',f'Encountered unprecedented error on Squad nick\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad nick Error'))
            return
    

    ## PUBLIC COMMAND [STATS]
    ##TODO
    """
        - Add Squad Counters
    """

    @squad.command(name='stats')
    async def sq_stats(self, ctx, name=None):
        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad stats Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            user = hand.grab()


            if name == None:
                if user['squad_name'] == "0":
                    await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'re not in a squad! Join a squad or specify a name**'))
                    return
                name = user['squad_name']

            if not self._squad_exists(name.lower()):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**This Squad doesnt exist!**'))
                return


            
            
            squadhand = js.config(f'{self.squadpath}{name.lower()}.json')

            sdat = squadhand.grab()

            members = sdat['member_count']
            leader = self._getmemberfrommain(sdat['leader'])
            total_messages = sdat['total_messages']
            founder = self._getmemberfrommain(sdat['founder'])

            if founder == None:
                founder = '[Left the Server]'
            if leader == None:
                leader = '[Left the Server]'

            daymsgs = sdat['day_messages']
            createdon = sdat['created_on']
            points = sdat['points']

            total_voice = sdat['total_voice']
            dayvc = sdat['day_voice']

            ismember = f'`{"Is in this squad" if (ctx.author.id in sdat["members"]) else "Is not in this squad"}`'


            embed = discord.Embed(
                title= f"{self.hypesquad_emote_switch[sdat['hypesquad']]} {sdat['squadname']} {sdat['squadsuffix']} Stats",
                description = f'Some basics stats about the {sdat["squadsuffix"]}\n\n:crown: **Leader:** `{leader}`\n:shield: **Founder:** `{founder}`\n\n:busts_in_silhouette: **Member Count:** `{members}`\n:question: **{ctx.author}:** `{ismember}`\n\n:speech_balloon: **Messages Today**: `{daymsgs}`\n:microphone2: **Voice Minutes Today**: `{dayvc}`\n:speech_left: **Total Messages:** `{total_messages}`\n:mega: **Total Voice Minutes** `{total_voice}`\n\n<:malSquadPoint:726431928521064499> **Points:** `{points}`',
                color = 0xff1cf7
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Stats',f'Encountered unprecedented error on Squad Stats\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Stats Error')) 
            return

    @squad.command(name='user')
    async def sq_user(self, ctx, user : discord.Member=None):
        try:
            if self._dmcheck(ctx):
                return


            nameerror = "Squad user Error"

            
            if user == None:
                user = ctx.author
            if user.bot:
                return

            if self._create_user(user) == "bot":
                return

            hand = js.config(f'{self.userpath}{user.id}.json')
            

            duser = hand.grab()




            

            total_messages = duser['total_messages']
            total_voice = duser['total_voice']

            daymsgs = duser['today_message']
            dayvc = duser['today_voice']

            squadname = duser['squad_name']

            embed = discord.Embed(
                title= f":bell: {user} Stats",
                description = f'Some basics stats about the user: {user}\n\n:speech_balloon: **Messages Today**: `{daymsgs}`\n:microphone2: **Voice Minutes Today**: `{dayvc}`\n:speech_left: **Total Messages:** `{total_messages}`\n:mega: **Total Voice Minutes** `{total_voice}`\n\n:star: **Squad Name:** `{squadname if squadname != "0" else "Not in a squad."}`',
                color = 0xff1cf7
            )

            await ctx.send(embed=embed)

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad User',f'Encountered unprecedented error on Squad User\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad User Error')) 
            return

    @squad.command(name = "list")
    async def sq_list(self, ctx):

        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            squads_data = []

            squads = os.listdir(f'{self.squadpath}')

            for squad_dir in squads:
                try:
                    user = None
                    if not squad_dir.endswith('.json'):
                        continue
                    squad_file = js.config(f"{self.squadpath}{squad_dir}")
                    squad_data = squad_file.grab()

                    squads_data.append(
                        {
                            "name" : squad_data["squadname"], 
                            "suffix" : squad_data["squadsuffix"], 
                            "hypesquad" : squad_data["hypesquad"], 
                            "points" : squad_data["points"], 
                            "path" : f"{self.squadpath}{squad_dir}",
                            "member_count" : squad_data["member_count"],
                            "leader" : squad_data["leader"]
                        }
                    )

                except:
                    pass

            squads_data.sort(key=operator.itemgetter("points"))

            squads_data = squads_data[::-1]

            leaderboard = ""

            main =  self.bot.get_guild(self.serverid)   
            
            emoji = get(await main.fetch_emojis(), id=726431928521064499)

            for index, squad in enumerate(squads_data):
                leaderboard += f"`{index + 1}.` {self.hypesquad_emote_switch[squad['hypesquad']]}**{squad['name'].title()} {squad['suffix'].title()}** {str(emoji)}`{squad['points']}` :busts_in_silhouette:`{squad['member_count']}` :crown:{self._getmemberfrommain(squad['leader']).mention}\n"


            listEmbed = discord.Embed(title="**List of all squads in My Anime Land!**",description=leaderboard,color=self._C.pink)
            listEmbed.set_footer(text='to join a squad, write h.squad join <squad\'s name>')
            
            await ctx.send(embed=listEmbed)

            

            
           



        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad list',f'Encountered unprecedented error on Squad list\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad list Error')) 
            return

    @squad.command(name = 'members')
    async def sq_members(self, ctx, name = None):
        try:

            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad members Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            user = hand.grab()


            if name == None:
                if user['squad_name'] == "0":
                    await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You\'re not in a squad! Join a squad or specify a squad name**'))
                    return
                name = user['squad_name']

            if not self._squad_exists(name.lower()):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,f'**The Squad {name} doesn\'t exist!**'))
                return


            
            
            squadhand = js.config(f'{self.squadpath}{name.lower()}.json')

            sdat = squadhand.grab()

            memberList = ""

            for memberID in sdat['members']:
                member = self._getmemberfrommain(memberID)

                user_file = js.config(f"{self.userpath}{memberID}.json")
                user_data = user_file.grab()

                memberList += (f":crown: {member.mention} `Leader` :incoming_envelope: `{user_data['today_message']}` :microphone: `{user_data['today_voice']}`\n\n" if memberID == sdat['leader'] else f":shield: {member.mention} `Supervisor` :incoming_envelope: `{user_data['today_message']}` :microphone: `{user_data['today_voice']}`\n" if memberID in sdat['supervisors'] else f":bust_in_silhouette: {member.mention} `Member` :incoming_envelope: `{user_data['today_message']}` :microphone: `{user_data['today_voice']}`\n")
            
            memberListEmbed = discord.Embed(
                title=f'{sdat["squadname"]} {sdat["squadsuffix"]}\'s members',
                description = memberList,
                color = self._C.pink
            )
            memberListEmbed.set_footer(text="All messages and voice minutes correspond to their amount today")

            await ctx.send(embed=memberListEmbed)

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad members',f'Encountered unprecedented error on Squad members\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad members Error')) 
            return

    @squad.command(name="counters")
    async def sq_counters(self, ctx):
        try:
            if self._dmcheck(ctx):
                return

            if self._create_user(ctx.author) == "bot":
                return

            config_file = js.config(self.confpath)

            config_data = config_file.grab()

            pmc = config_data['perm_count_channels_msg']
            tmc = config_data['temp_count_channels_msg']
            pvc = config_data['perm_count_channels_vc']
            tvc = config_data['temp_count_channels_vc']

            embed = discord.Embed(
                title= 'Channels eligble for squad counting!',
                color = self._C.pink,
                description = "There are currently no active counters for **MAL**!" if any([pmc, tmc, pvc, tvc]) == False else None
            )


            if pmc or pvc:

                fieldValue = ""

                if pmc:
                    fieldValue += ":speech_balloon: Text Channels:  \n\n"
                    for index, channelID in enumerate(pmc):
                        fieldValue += f"`{index + 1}.` {self._getchannelfrommain(channelID).mention}\n"
                
                if pvc:
                    fieldValue += "\n\n:microphone2: Voice Channels:  \n\n"
                    for index, channelID in enumerate(pvc):
                        fieldValue += f"`{index + 1}.` **:speaker: {self._getchannelfrommain(channelID).name}**\n"

                embed.add_field(name=':lock: Permanent Counter Channels', value = fieldValue)

            if tmc or tvc:

                fieldValue = ""

                if tmc:
                    fieldValue += ":speech_balloon: Text Channels:  \n\n"
                    for index, channelID in enumerate(tmc):
                        secondsUntilExpire = (self._strtotime(tmc[channelID]) - datetime.utcnow()).seconds

                        hours , r = divmod(secondsUntilExpire, 3600)
                        minutes, seconds = divmod(r, 60)
                        fieldValue += f"`{index + 1}.` {self._getchannelfrommain(int(channelID)).mention} Duration: `{hours}h {minutes}m {seconds}s`\n"


                if tvc:
                    fieldValue += "\n\n:microphone2: Voice Channels: \n\n"
                    for index, channelID in enumerate(tvc):
                        secondsUntilExpire = (self._strtotime(tvc[channelID]) - datetime.utcnow()).seconds

                        hours , r = divmod(secondsUntilExpire, 3600)
                        minutes, seconds = divmod(r, 60)

                        fieldValue += f"`{index + 1}.`**:speaker: {self._getchannelfrommain(int(channelID)).name}** Duration: `{hours}h {minutes}m {seconds}s`\n"
                

                embed.add_field(name=':stopwatch: Event Counter Channels', value=fieldValue)

            await ctx.send(embed=embed)


        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Counters',f'Encountered unprecedented error on Squad Counters\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Counters Error')) 
            return




    ## LEADER COMMMANDS (SOME SUPERVISOR)
    @squad.command(name='leader')
    async def sq_leader(self, ctx, user : discord.Member = None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad leader Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to give the squad to!** Command Usage: `squad leader <@User>`'))
                return
            if user.bot:
                return

            if self._create_user(user) == "bot":
                return

            otherh = js.config(f'{self.userpath}{user.id}.json')

            uother = otherh.grab()

            if not user.id in sdat['members']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**The user you are trying to transfer the squad to isnt in the squad.**"))
                return

            hanamsg = await ctx.send(f'**Are you sure you want to transfer leadership of "{sdat["squadname"]} {sdat["squadsuffix"]}", to {user.mention}?**\n> :bell: - You wont be able to get leadership of the squad again unless they gives it back')
            def check(r,u):
                return u == ctx.author and (r.emoji.id == self.yes_em or r.emoji.id == self.no_em)

            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.yes_em))
            await hanamsg.add_reaction(get(ctx.guild.emojis,id=self.no_em))

            try:
                reaction , usr = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return

            if reaction.emoji.id == self.no_em:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM('Cancelled','Squad leader cancelled','Cancel'))
                return

            if self._create_user(user) == "bot":
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            sdat['leader'] = user.id
            squadhand.write(sdat ,indent=self.dataindent)


            await ctx.author.remove_roles(self._getrolefrommain(self.sq_leader))
            await user.add_roles(self._getrolefrommain(self.sq_leader))

            await ctx.send(embed=EmbedFuncs.SuccessEM('Successfully Transferred',f'**Successfully Transferred {sdat["squadname"]} {sdat["squadsuffix"]} to {user}!**'))
            return

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Leader',f'Encountered unprecedented error on Squad Leader\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Leader Error')) 
            return
    
    @squad.command(name='private')
    async def sq_private(self, ctx):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad private Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()


            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return

            if sdat['private']:
                sdat['private'] = False
                squadhand.write(sdat,indent=self.dataindent)
                await ctx.send(embed=EmbedFuncs.SuccessEM('Changed squad privacy',':white_check_mark: Changed your squad privacy to: **Public**'))
            else:
                sdat['private'] = True
                squadhand.write(sdat,indent=self.dataindent)
                await ctx.send(embed=EmbedFuncs.SuccessEM('Changed squad privacy',':white_check_mark: Changed your squad privacy to: **Private**'))

            
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad private',f'Encountered unprecedented error on private\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad private Error'))
            return
    
    @squad.command(name='hype')
    async def sq_hype(self, ctx):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad hype Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return
            
            nums = {
                '1' : 658785745804328980,
                '2' : 658785722265894932,
                '3' : 658785706201579570
            }
           
            hanamsg = await ctx.send(f'What hypesquad would you like **{sdat["squadname"]} {sdat["squadsuffix"]}** to be?\n\n**1.** Brilliance <:HypeSquadBrilliance:719317478416580608>\n**2.** Bravery <:HypeSquadBravery:719317478424969216>\n**3.** Balance <:HypeSquadBalance:719317478538477578>')
            

            store = []
            for i in nums:
                store.append(nums[i])
                await hanamsg.add_reaction(get(ctx.guild.emojis,id=nums[i]))



            def check(r,u):
                return u == ctx.author and r.emoji.id in store
            

            try:
                reaction , usr = await self.bot.wait_for('reaction_add',check=check, timeout=60)
            except asyncio.TimeoutError:
                await hanamsg.edit(embed=EmbedFuncs.ErrorEM(nameerror,'**You didnt response in time!**'))
                return



            squadswitch = {
                nums['1'] : 'brilliance',
                nums['2'] : 'bravery',
                nums['3'] : 'balance'
            }



            sdat = squadhand.grab()

            sdat['hypesquad'] = squadswitch[reaction.emoji.id]

            squadhand.write(sdat ,indent=self.dataindent)

            await hanamsg.edit(content="",embed=EmbedFuncs.SuccessEM(f'Hypesquad {squadswitch[reaction.emoji.id]} joined!',f'**Successfully joined the {squadswitch[reaction.emoji.id]} hypesquad!**'))
            return

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad hype',f'Encountered unprecedented error on Squad hype\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad hype Error')) 
            return
    
    ##TODO
    """
    """
    @squad.command(name='delete')
    async def sq_delete(self, ctx):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad delete Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()


            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author and m.content.lower() in ['!agree','!no']

            await ctx.send(embed=EmbedFuncs.ErrorEM("Squad Delete",'**Are you sure you want to delete your squad?**\n\nType: `!agree` **To delete your Squad**\n:warning: **This action is permanent and cannot be reversed** :warning:\nType `!no` to cancel this process'))
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send(embed=EmbedFuncs.ErrorEM("Squad Delete Timed Out",f'The deletion of the {sdat["squadname"]} {sdat["squadsuffix"]} has been cancelled.','Timed Out'))
                return

            if msg.content.lower() == '!agree':

                members = sdat['members']
                for i in members:
                    uhan = js.config(f'{self.userpath}{i}.json')
                    udat = uhan.grab()

                    udat['squad_name'] = "0"
                    uhan.write(udat,indent=self.dataindent)    

                    user = self._getmemberfrommain(i)

                    newnick = f" | {sdat['squadname']} {sdat['squadsuffix']}"
                    newnick = user.display_name.replace(newnick,'')
                    try:
                        await user.edit(nick=newnick)   
                        await user.remove_roles(self._getrolefrommain(self.sq_member))         
                    except:
                        pass


                os.remove(f'{self.squadpath}{sdat["squadname"].lower()}.json')

                ### REMOVED 2
                #chan = self._getchannelfrommain(squaddat["squad_channel"])
                #if chan != None:
                #    await chan.delete()

                chan = self._getchannelfrommain(sdat["squad_channel"])
                if chan != None:
                    everyone = self._getrolefrommain(self.everyonerole)
                    overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024))}
                    if chan.overwrites != overwrites:
                        await chan.edit(overwrites = overwrites)
                
                await ctx.author.remove_roles(self._getrolefrommain(self.sq_leader))
                await ctx.send(embed=EmbedFuncs.ErrorEM("Squad Deleted","You left your squad, and it has been disbanded. This action is permanent.","Squad Deleted."))
            else:
                await ctx.send(embed=EmbedFuncs.ErrorEM("Cancelled","Squad Deletion has been cancelled.","Cancelled."))
            return

            
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad delete',f'Encountered unprecedented error on delete\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad delete Error'))
            return
    
    @squad.command(name='description')
    async def sq_desc(self,ctx, *, desc=None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad description Error"

            if desc == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Missing Argument!** Usage: `squad description <description>` Keep your description over 30 characters!"))
                return

            if len(desc.replace(' ','').replace('\n','')) < 30:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Missing Argument!** Usage: `squad description <description>` Keep your description over 30 characters!"))
                return


            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()
            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return
            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return
            
            desc = desc.replace('\"','').replace("@",'@/')


            sdat["desc"] = desc

            squadhand.write(sdat ,indent=self.dataindent)




            await ctx.send(embed=EmbedFuncs.SuccessEM("Changed Squad Description!",f'**Changed Squad Description to:**\n\n{desc}'))
            return

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad Description',f'Encountered unprecedented error on Squad Description\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Description Error')) 
            return

    @squad.command(name='image')
    async def sq_image(self,ctx, url=None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad image Error"

            if url== None:


                

                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Missing Argument!** Usage: `squad image <url>`"))
                return




            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            


            udat = hand.grab()
            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return
            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')


            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return
            

            image_formats = ("image/png", "image/jpeg", "image/jpg","image/gif")
            try:
                r = requests.head(url)
            except:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**The URL you gave isnt an image or gif**'))
                return

            if r.headers["Content-Type"] not in image_formats:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**The URL you gave isnt an image or gif**'))
                return



            sdat["image"] = url

            squadhand.write(sdat ,indent=self.dataindent)




            
            embed = discord.Embed(
                title = "Changed Squad Image",
                description="**Changed Squad Image to:**",
                color = 0x8cff00,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Squad Image Changed")
            embed.set_image(url=url)

            await ctx.send(embed=embed)
            return

        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on Squad image',f'Encountered unprecedented error on Squad image\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad Image Error')) 
            return
    
    @squad.command(name='addSupervisor')
    async def sq_addsup(self, ctx, user : discord.Member = None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad addSupervisor Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to promote!** Command Usage: `squad addSupervisor <@User>`'))
                return

            if user.bot:
                return

            if user == ctx.author:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Hey!** You cant promote yourself!"))
                return

            if user.id in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**This user is already a supervisor!**"))
                return

            

            if self._create_user(user) == "bot":
                return


            otherh = js.config(f'{self.userpath}{user.id}.json')

            
            uother = otherh.grab()
            if uother['squad_name'] != udat['squad_name']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This user is not in your squad!**'))
                return

            sdat = squadhand.grab()
            sdat['supervisors'].append(user.id)
            squadhand.write(sdat,indent=self.dataindent)


            await ctx.send(embed=EmbedFuncs.SuccessEM(f'User promoted to Supervisor!', f'**The user {user.mention} has been promoted to squad supervisor!**'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad addSupervisor',f'Encountered unprecedented error on squad addSupervisor\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad addSupervisor Error'))
            return
   
    @squad.command(name='removeSupervisor') 
    async def sq_remsup(self, ctx, user : discord.Member = None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad removeSupervisor Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**You arent the squad leader!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to demote!** Command Usage: `squad removeSupervisor <@User>`'))
                return

            if user.bot:
                return

            if user == ctx.author:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Hey!** You cant demote yourself!"))
                return

            if user.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**This user is not a supervisor!**"))
                return

            

            if self._create_user(user) == "bot":
                return


            otherh = js.config(f'{self.userpath}{user.id}.json')

            
            uother = otherh.grab()
            if uother['squad_name'] != udat['squad_name']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This user is not in your squad!**'))
                return

            sdat = squadhand.grab()
            sdat['supervisors'].remove(user.id)
            squadhand.write(sdat,indent=self.dataindent)


            await ctx.send(embed=EmbedFuncs.SuccessEM(f'User demoted from Supervisor!', f'**The user {user.mention} has been demoted from squad supervisor!**'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad addSupervisor',f'Encountered unprecedented error on squad addSupervisor\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad addSupervisor Error'))
            return
    
    @squad.command(name='postad') ## SUPER
    async def sq_postad(self, ctx):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad postad Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if self._is_on_postad_cooldown(ctx)[0]:

                hours, remainder = divmod(self._is_on_postad_cooldown(ctx)[1].seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, f"**You're on a cooldown!** : `{minutes}m {seconds}s` left"))
                return

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id and ctx.author.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Only squad supervisors and the squad leader can run this command!**'))
                return

            if sdat['desc'] == '':
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This squad doesnt have a description!** Use: `squad description <description>`'))
                return
            
            if sdat['image'] == '':
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This Squad doesnt have a set image!** Use: `squad image <url>`'))
                return

            desc = sdat['desc'].replace('@','@/') + f'\n\n**__Join this squad using:__** `squad join {sdat["squadname"]}`\n{"-"*5 + "__ Stats __" + "-"*5}\n:busts_in_silhouette: Squad Member Count: `{sdat["member_count"]}`\n<:malSquadPoint:726431928521064499> Squad Points: `{sdat["points"]}`'

            data = {
            'username' : f'{ctx.author}',
            'avatar_url' : str(ctx.author.avatar_url),
            'content': f"{ctx.author.mention}", 
            'embeds': [
                {   
                    'title' : f'{sdat["squadname"]} {sdat["squadsuffix"]}',
                    'description': f'{desc}',
                    'color'  : random.randint(0,16777215),
                    'image' : {
                        'url' : sdat['image']
                    }
                }
            ]
            }

            headers = {
                'Content-Type' : 'application/json'
            }

            r = requests.post(self.postad_webhook_url, data=json.dumps(data), headers=headers)
            if r.status_code not in [200, 204]:
                await self._sendtologs(content='<@636808158521589770>',embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad post ad',f'Encountered unprecedented error on Squad postad\n\n**Error Message:** `{r.content}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad postad Error'))
                return

            self._set_postad_time(ctx)
            await ctx.send(embed=EmbedFuncs.SuccessEM('Posted ad!',':white_check_mark: Your ad was posted successfully in : <#684764188740026407>'))
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad post ad',f'Encountered unprecedented error on Squad postad\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad postad Error'))
            return
    
    ##TODO
    """
    """
    @squad.command(name='invite') ## SUPER
    async def sq_invite(self, ctx , user : discord.Member = None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad invite Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if self._is_on_invite_cooldown(ctx):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You're on a cooldown!**"))
                return


            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id and ctx.author.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Only squad supervisors and the squad leader can run this command!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to invite!** Command Usage: `squad invite <@User>`'))
                return

            if user.bot:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a __human__ user to invite!** Command Usage: `squad kick <@User>`'))
                return

            if self._create_user(user) == "bot":
                return

            if user.id in sdat['exiled']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This person has been exiled from this squad! You cant invite them!**'))
                return

            otherh = js.config(f'{self.userpath}{user.id}.json')

            uother = otherh.grab()

            if uother['squad_name'] == udat['squad_name']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This user is already in your squad!**'))
                return

            if self._is_on_join_cooldown(user=user):
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,f'**The user {user} is on a join cooldown!**'))
                return

            def check(m):
                return m.channel == ctx.channel and m.author == user and m.content.lower() in ['!agree','!no']
            
            await ctx.send(f'> :bell: --- **[SQUAD INVITE]** {user.mention}, {ctx.author.mention} has invited you to join **{sdat["squadname"]} {sdat["squadsuffix"]}**\n\n> :warning: This will **remove** you from your existing squad.\n\nType: `!agree` to join the squad, and `!no` to decline\n(*request timing out in 60 seconds*)')
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,f'Invite timed out. for user: {user}'))
                return
            
            if msg.content.lower() == '!no':
                await ctx.send(embed=EmbedFuncs.ErrorEM('Declined',f'The user {user} has declined {ctx.author}\'s invite.',footer='Declined'))
                return

            if user.id in sdat['exiled']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This person has been exiled from this squad!, You cant invite them!**'))
                return

            if uother["squad_name"] != "0":

                osquadhand = js.config(f'{self.squadpath}{uother["squad_name"].lower()}.json')

                osdat = squadhand.grab()

                osdat["member_count"] -= 1
                try:
                    osdat['members'].remove(user.id)
                except:
                    pass


                past_squad_str = f" | {osdat['squadname']} {osdat['squadsuffix']}"

                newnick = user.display_name.replace(past_squad_str,f' | {sdat["squadname"]} {sdat["squadsuffix"]}')

            else:
                try:
                    if uother['toggle_nick']:

                        newnick = user.display_name + f" | {sdat['squadname']} {sdat['squadsuffix']}"
                        if len(newnick) > 32:
                            raise ValueError

                        await user.edit(nick=newnick)
                except:
                    pass
            

            




            uother = otherh.grab()
            uother["last_joined_squad"] = self._timetostr(datetime.utcnow())
            uother['squad_name'] = sdat['squadname']

            sdat = squadhand.grab()
            sdat['members'].append(user.id)
            sdat['member_count'] += 1

            otherh.write(uother, indent=self.dataindent)
            squadhand.write(sdat, indent=self.dataindent)

        
            
            await user.add_roles(self._getrolefrommain(self.sq_member))
            await ctx.send(embed=EmbedFuncs.SuccessEM('Success!',f'You have successfully left your previous squad (if you were in one) to join **{sdat["squadname"]} {sdat["squadsuffix"]}**'))
            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad invite',f'Encountered unprecedented error on Squad invite\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad invite Error'))
            return
    
    ##TODO
    """
    """
    @squad.command(name='kick') ## SUPER
    async def sq_kick(self, ctx, user : discord.Member = None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad kick Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id and ctx.author.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Only squad supervisors and the squad leader can run this command!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to kick!** Command Usage: `squad kick <@User>`'))
                return

            if user.bot:
                return

            if user == ctx.author:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Hey!** You cant kick yourself!"))
                return

            

            if self._create_user(user) == "bot":
                return

            otherh = js.config(f'{self.userpath}{user.id}.json')

            
            uother = otherh.grab()
            if uother['squad_name'] != udat['squad_name']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This user is not in your squad!**'))
                return

            sdat = squadhand.grab()
            sdat["member_count"] -= 1
            sdat['members'].remove(user.id)
            squadhand.write(sdat,indent=self.dataindent)

            uother = otherh.grab()
            uother['squad_name'] = '0'
            otherh.write(uother,indent=self.dataindent)

            newnick = f" | {sdat['squadname']} {sdat['squadsuffix']}"
            newnick = user.display_name.replace(newnick,'')
            try:
                await user.edit(nick=newnick)
            except:
                pass
            
            await user.remove_roles(self._getrolefrommain(self.sq_member))
            await ctx.send(embed=EmbedFuncs.SuccessEM(f'User Kicked from {sdat["squadname"]} {sdat["squadsuffix"]}', f'**The user {user.mention} has been kicked from the {sdat["squadname"]} {sdat["squadsuffix"]}**'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad kick',f'Encountered unprecedented error on squad kick\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad kick Error'))
            return
    
    ##TODO
    """
    """
    @squad.command(name='exile') ## SUPER
    async def sq_exile(self, ctx, user : discord.Member=None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad exile Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()

            if sdat['leader'] != ctx.author.id and ctx.author.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Only squad supervisors and the squad leader can run this command!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to exile!** Command Usage: `squad exile <@User>`'))
                return

            if user.bot:
                return

            if user == ctx.author:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**Hey!** You cant exile yourself!"))
                return
            
            

            if self._create_user(user) == "bot":
                return

            otherh = js.config(f'{self.userpath}{user.id}.json')

            
            uother = otherh.grab()
            sdat = squadhand.grab()
            if uother['squad_name'] == udat['squad_name']:
                    

                
                sdat["member_count"] -= 1
                sdat['members'].remove(user.id)
                
                


                uother = otherh.grab()
                uother['squad_name'] = '0'
                otherh.write(uother,indent=self.dataindent)

                newnick = f" | {sdat['squadname']} {sdat['squadsuffix']}"
                newnick = user.display_name.replace(newnick,'')
                try:
                    await user.edit(nick=newnick)
                except:
                    pass

                await user.remove_roles(self._getrolefrommain(self.sq_member))
            
            sdat['exiled'].append(user.id)
            squadhand.write(sdat,indent=self.dataindent)

            await ctx.send(embed=EmbedFuncs.SuccessEM(f'User Exiled from {sdat["squadname"]} {sdat["squadsuffix"]}', f'**The user {user.mention} has been exiled from the {sdat["squadname"]} {sdat["squadsuffix"]}**\n\n> They are now banned from joining this squad.'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad exile',f'Encountered unprecedented error on squad exile\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad exile Error'))
            return

    @squad.command(name='unexile') ## SUPER
    async def sq_unexile(self, ctx, user : discord.Member=None):
        try:
            if self._dmcheck(ctx):
                return
            
            if self._create_user(ctx.author) == "bot":
                return

            nameerror = "Squad unexile Error"

            hand = js.config(f'{self.userpath}{ctx.author.id}.json')
            

            udat = hand.grab()

            if udat["squad_name"] == "0":
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, "**You arent in any Squad!**"))
                return

            squadhand = js.config(f'{self.squadpath}{udat["squad_name"].lower()}.json')

            sdat = squadhand.grab()


            if sdat['leader'] != ctx.author.id and ctx.author.id not in sdat['supervisors']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Only squad supervisors and the squad leader can run this command!**'))
                return

            if user == None:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror,'**Please specify a user to unexile!** Command Usage: `squad unexile <@User>`'))
                return

            if user.bot:
                return

            if user.id not in sdat['exiled']:
                await ctx.send(embed=EmbedFuncs.ErrorEM(nameerror, '**This person isn\'t exiled!'))
                return
            

            if self._create_user(user) == "bot":
                return

            sdat = squadhand.grab()
            sdat['exiled'].remove(user.id)
            squadhand.write(sdat,indent=self.dataindent)



            await ctx.send(embed=EmbedFuncs.SuccessEM(f'User unexiled from {sdat["squadname"]} {sdat["squadsuffix"]}', f'**The user {user.mention} has been unexiled from the {sdat["squadname"]} {sdat["squadsuffix"]}**\n\n> They are now allowed to join back into the squad.'))

            return
        except Exception as e:
            await self._sendtologs(embed=EmbedFuncs.ErrorEM(':rotating_light: Error on squad unexile',f'Encountered unprecedented error on squad unexile\n\n**Error Message:** `{e}`. Please contact <@636808158521589770>\n\n**Encountered by:** `{ctx.author}` (`{ctx.author.id}`)\n**In:** {ctx.channel.mention}',footer='Squad unexile Error'))
            return


        
    ## ADMIN COMMMANDS
    ##TODO
    """
        - Nearly all admin commands are just broken, please fix + add embeds FIXME
    """

    @squad.command(name='addp')
    async def sq_addp(self, ctx, name=None, points = None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

        if name == None:
            await ctx.send('> :x: Missing Squad Name')
            return

        if not self._squad_exists(name):
            await ctx.send('> :x: Squad Doesnt Exist')
            return

        if points == None:
            await ctx.send('> :x: missing points')
            return

        try:
            points = int(points)
        except:
            await ctx.send('> :x: Please insert a correct number')
            return

        squadhand = js.config(f'{self.squadpath}{name.lower()}.json')
        sdat = squadhand.grab()

        sdat['points'] = int(sdat['points']) + points
        squadhand.write(sdat ,indent=self.dataindent)

        await ctx.send(f'> :white_check_mark: Success, squad now has: {sdat["points"]}')
        return

    @squad.command(name='reset')
    async def sq_reset(self, ctx, name=None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

        if name == None:
            await ctx.send('> :x: Missing Squad Name')
            return

        if not self._squad_exists(name):
            await ctx.send('> :x: Squad Doesnt Exist')
            return

        squadhand = js.config(f'{self.squadpath}{name.lower()}.json')
        sdat = squadhand.grab()

        mem = sdat['members']
        mem_count = sdat['member_count']

        self._create_squad(sdat['squadsuffix'],sdat['squadname'],None,squadleaderid=sdat['leader'])

        sdat = squadhand.grab()

        sdat['members'] = mem
        sdat['member_count'] = mem_count

        squadhand.write(sdat ,indent=self.dataindent)

        await ctx.send(f'> :white_check_mark: Success wiped data of {sdat["squadname"]}')
        return

    @squad.command(name='setobject')
    async def sq_sobj(self, ctx, name=None, objectname=None, value=None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

        if name == None:
            await ctx.send('> :x: Missing Squad Name')
            return

        if not self._squad_exists(name):
            await ctx.send('> :x: Squad Doesnt Exist')
            return

        if objectname == None:
            await ctx.send('> :x: missing obj name')
            return

        if value == None:
            await ctx.send('> :x: missing value')
            return

        squadhand = js.config(f'{self.squadpath}{name.lower()}.json')
        sdat = squadhand.grab()

        sdat[objectname] = value

        await ctx.send(f'> :white_check_mark: Successfully set {objectname} to {value} for {name}')
        return

    ##FIXME
    @squad.command(name='enablecounter')
    async def sq_ecount(self, ctx, channel = None, duration = None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

            

        if channel == None:
            await ctx.send('> :x: Missing channel')
            return

        if duration == None:
            await ctx.send('> :x: Missing Duration')
            return

        channel = channel.replace('<#','').replace(">",'')
        try:
            if self._getchannelfrommain(int(channel)) == None:
                await ctx.send("> :x: Bad Channel")
                return

            channel = self._getchannelfrommain(int(channel))
        except:
            await ctx.send("> :x: Bad Channel")
            return

        
        def formatTime(timee):
            def isInt(st):
                try:
                    return True if type(int(st)) == int else False
                except:
                    return False

            if timee == None or len(timee.replace(' ','')) == 0:
                raise SyntaxError

            cmd = 'z ='
            amount = 0
            allowed = ['h','d','m','w','s']
            fixed_time = ''
            
            for i in timee:
                if i in allowed or isInt(i):
                    if not isInt(i):
                        fixed_time += i
                        break
                    fixed_time += i

            
            

            
            cmd += fixed_time.replace('h','*3600').replace('d','*86400').replace('m','*60').replace('w','*604800').replace('s','*1')


            global z
            exec(cmd, None, globals())
            return int(z)
        
        try:
            duration = formatTime(duration)
        except:
            await ctx.send("> :x: Invalid Duration")
            return

        han = js.config(self.confpath)
        dat = han.grab()

        if isinstance(channel,discord.TextChannel):
            dat['temp_count_channels_msg'][channel.id] = self._timetostr(datetime.utcnow() + timedelta(seconds=duration))
            
        if isinstance(channel, discord.VoiceChannel):
            dat['temp_count_channels_vc'][channel.id] = self._timetostr(datetime.utcnow() + timedelta(seconds=duration))

        han.write(dat)



        hours , r = divmod(duration, 3600)
        minutes, seconds = divmod(r, 60)

        await ctx.send(f'> :white_check_mark: Successfully enabled counter for {channel.name}, Duration: `{hours}h {minutes}m {seconds}s`')
        return

    @squad.command(name='permcount')
    async def sq_pcount(self, ctx, channel = None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

        if channel == None:
            await ctx.send('> :x: Missing channel')
            return

        han = js.config(self.confpath)
        dat = han.grab()

        channel = channel.replace('<#','').replace(">",'')
        try:
            if self._getchannelfrommain(int(channel)) == None:
                await ctx.send("> :x: Bad Channel")
                return

            channel = self._getchannelfrommain(int(channel))
        except:
            await ctx.send("> :x: Bad Channel")
            return
             
        if isinstance(channel, discord.TextChannel):
            dat['perm_count_channels_msg'].append(channel.id)
        elif isinstance(channel, discord.VoiceChannel):
            dat['perm_count_channels_vc'].append(channel.id)

            
        

        han.write(dat,indent=self.dataindent)

        await ctx.send(f'> :white_check_mark: Successfully enabled counter for {channel} perm')
        return

    @squad.command(name='allowchannel')
    async def sq_reset(self, ctx, name=None):
        if self._dmcheck(ctx):
            return
        if not self._isadmin(ctx.author):
            await ctx.send(embed=EmbedFuncs.NoPerm())
            return

        if name == None:
            await ctx.send('> :x: Missing Squad Name')
            return

        if not self._squad_exists(name):
            await ctx.send('> :x: Squad Doesnt Exist')
            return

        squadhand = js.config(f'{self.squadpath}{name.lower()}.json')
        sdat = squadhand.grab()

        sdat['channel_allow'] = not sdat['channel_allow']

        squadhand.write(sdat ,indent=self.dataindent)

        await ctx.send(f'> :white_check_mark: Successfully set channel_allow to `{sdat["channel_allow"]}` for squad `{sdat["squadname"]}`')
        return

    #@squad.command(name='bypcool')
    async def sq_bypcool(self, ctx):
        if self._dmcheck(ctx):
            return
        
        if self._create_user(ctx.author) == "bot":
            return

        nameerror = "Squad bypcool Error"

        hand = js.config(f'{self.userpath}{ctx.author.id}.json')
        

        udat = hand.grab()

        udat['last_post_ad'] = "30/04/2019 12:33:39"
        udat["last_invite"] = "30/04/2019 12:33:39" 
        udat["last_joined_squad"] = "30/04/2019 12:33:39"
        udat["last_message"] = "30/04/2019 12:33:39"
        udat["last_made_squad"] = "30/04/2019 12:33:39"

        hand.write(udat, indent=self.dataindent)
        await ctx.send(':white_check_mark: Bypassed Cooldowns: You now have no ongoing cooldowns')
        return





    @commands.Cog.listener()
    async def on_message(self, msg):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        try:

            confhan = js.config(self.confpath)
            conf = confhan.grab()


            if str(msg.channel.id) in conf['temp_count_channels_msg'] or msg.channel.id in conf['perm_count_channels_msg']:

                if self._create_user(msg.author) == "bot":
                    return

                han = js.config(f'{self.userpath}{msg.author.id}.json')
                dat = han.grab()


                if not self._strtotime(dat['last_message']) < datetime.utcnow() - timedelta(seconds=conf['count_cooldown'] ):
                    return


                dat['total_messages'] += 1

                dat['today_message'] += 1

                dat['update_messages'] += 1

                dat['last_message'] = self._timetostr(datetime.utcnow())
                han.write(dat ,indent=self.dataindent)

                return
        except Exception as e:
            print(f'>> Exception on _message -- {e}')

   
    ##TODO
    """
        - This is broken, linked to the broken admin commands FIXME
    """
    @tasks.loop(seconds=10)
    async def update_temp_chans(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        try:
            confhan = js.config(f'{self.confpath}')
            cdat = confhan.grab()

            temp_msgs = cdat['temp_count_channels_msg']
            temp_vc = cdat['temp_count_channels_vc']

            new_temp_msgs = dict(temp_msgs)
            new_temp_vc = dict(temp_vc)
            for chan in temp_msgs:
                if self._strtotime(temp_msgs[chan]) < datetime.utcnow():
                    del new_temp_msgs[chan]
            

            for chan in temp_vc:
                if self._strtotime(temp_vc[chan]) < datetime.utcnow():
                    del new_temp_vc[chan]


            cdat['temp_count_channels_msg'] = new_temp_msgs
            cdat['temp_count_channels_vc'] = new_temp_vc

            confhan.write(cdat ,indent=self.dataindent)
        except Exception as e:
            print(f'> Exeption on update_temp_chans -- {e}')

    ## TODO
    """

    // This is used to send the daily message
    """
    @tasks.loop(seconds=31)
    async def update_today(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        try:
            if datetime.strftime(datetime.utcnow(),"%H:%M") == "00:00":

                users = os.listdir(f'{self.userpath}')
                squads = os.listdir(f'{self.squadpath}')
                


                """
                    Gathering all the information needed for the leaderboards and daily updates
                """
                ## [Dict: SquadName : Message/Minutes]

                squad_pairs = {
                    "24h_msgs" : [],
                    "24h_vc" : [],
                    "t_msgs" : [],
                    "t_vc" : []
                }

                for squad_dir in squads:
                    try:
                        user = None
                        if not squad_dir.endswith('.json'):
                            continue
                        squad_file = js.config(f"{self.squadpath}{squad_dir}")
                        squad_data = squad_file.grab()

                        squad_pairs["24h_msgs"].append( 
                            {
                                "name" : squad_data["squadname"], 
                                "suffix" : squad_data["squadsuffix"], 
                                "value" : squad_data["day_messages"], 
                                "hypesquad" : squad_data["hypesquad"], 
                                "points" : squad_data["points"], 
                                "path" : f"{self.squadpath}{squad_dir}",
                                "image" : squad_data["image"]
                            } 
                        )
                        squad_pairs["24h_vc"].append( 
                            {
                                "name" : squad_data["squadname"], 
                                "suffix" : squad_data["squadsuffix"], 
                                "value" : squad_data["day_voice"], 
                                "hypesquad" : squad_data["hypesquad"], 
                                "points" : squad_data["points"], 
                                "path" : f"{self.squadpath}{squad_dir}"
                            } 
                        )
                        squad_pairs["t_msgs"].append( 
                            {
                                "name" : squad_data["squadname"], 
                                "suffix" : squad_data["squadsuffix"], 
                                "value" : squad_data["total_messages"], 
                                "hypesquad" : squad_data["hypesquad"], 
                                "points" : squad_data["points"], 
                                "path" : f"{self.squadpath}{squad_dir}"
                            } 
                        )
                        squad_pairs["t_vc"].append( 
                            {
                                "name" : squad_data["squadname"], 
                                "suffix" : squad_data["squadsuffix"], 
                                "value" : squad_data["total_voice"], 
                                "hypesquad" : squad_data["hypesquad"], 
                                "points" : squad_data["points"], 
                                "path" : f"{self.squadpath}{squad_dir}"
                            } 
                        )

                        squad_data["day_messages"] = 0
                        squad_data["day_voice"] = 0

                        squad_file.write(squad_data)

                        for user in squad_data["members"]:
                            user_file = js.config(f"{self.userpath}{user}.json")
                            user_data = user_file.grab()

                            user_data["today_message"] = 0
                            user_data["today_voice"] = 0

                            user_file.write(user_data)
                    except:
                        
                        print(f'Problem in loop for update today for squad_file {squad_dir} and user: {user}')
                        traceback.print_exc()






                """
                    Order the Squad pairs by value key
                """
                for pair_name in squad_pairs:
                    squad_pairs[pair_name].sort(key=operator.itemgetter("value"))


                """ 
                                [Daily Winner Squad]
                    Daily winner squad is a webhook message that gets sent to a channel that announces the squad which has sent the most messages in the previous 24 hours
                """
                
                winning_squad = squad_pairs["24h_msgs"][::-1][0]

                username = "Hana"

                PFP = "https://images-ext-2.discordapp.net/external/Pr7SpQKlec2PDaxUktdvUxGDHJSZFjIS_-sN-WSxbyE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/682585660355510275/4df79016175a9392d63e3523150631cb.webp"


                data = {
                    'username' : username,
                    'avatar_url' : PFP, 
                    'embeds': [
                        {
                            "title" : "**Daily Winner Squad**",
                            "description": f"{self.hypesquad_emote_switch[winning_squad['hypesquad']]} **{winning_squad['name']} {winning_squad['suffix']}** <:SentMessages:706890846657577051> ``{winning_squad['value']}`` <:malSquadPoint:726431928521064499> ``100``\n\n**{winning_squad['name']} {winning_squad['suffix']}** have been the most active squad in the previous 24 hours, congratulations! <a:malYay:608280367580971017>" ,
                            "color": 0x4BCC30
                        }
                    ]
                }


                if winning_squad["image"] != "":
                    
                    data['embeds'][0]["thumbnail"] = {"url" : winning_squad["image"]}


                headers = {
                    'Content-Type' : 'application/json'
                }
                
                r = requests.post(self.winner_update_webhook,json.dumps(data),headers=headers)
            
                win_squad_file = js.config(winning_squad["path"])
                win_squad_data = win_squad_file.grab()
                win_squad_data["points"] += 100
                win_squad_file.write(win_squad_data)

                


                del squad_pairs
              





                
                
               




                        


        except Exception as e:
            print(f'>> Error in update_today Error:')
            traceback.print_exc()
            
    @tasks.loop(minutes=1)
    async def update_squad_counts(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        try:
        
            users = os.listdir(f'{self.userpath}')

            #print(users)
            for name in users:
                #print(name)

                if not name.endswith('.json'):
                    continue
                if name == '0.json':
                    return
                
                han = js.config(f'{self.userpath}{name}')

                dat = han.grab()
                
                #print(1)

                if dat['squad_name'] != "0":
                    #print(2)
                    if dat['update_messages'] != 0 or dat['update_voice'] != 0:
                        #print(3)

                        shan = js.config(f'{self.squadpath}{dat["squad_name"].lower()}.json')
                        sdat = shan.grab()
                        

                        sdat['total_messages'] += dat['update_messages']
                        sdat['day_messages'] += dat['update_messages']

                        sdat['total_voice'] += dat['update_voice']
                        sdat['day_voice'] += dat['update_voice']

                        dat['update_messages'] = 0
                        dat['update_voice'] = 0



                        shan.write(sdat ,indent=self.dataindent )
                        han.write(dat ,indent=self.dataindent )
                await asyncio.sleep(0.2)
        except Exception as e:
            print(f'> Exception in update_squad_counts for name: {name} error: {e}')

    @tasks.loop(minutes=1)
    async def voicecount(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)
        guild = get(self.bot.guilds,id=self.serverid)

        confhan = js.config(self.confpath)
        conf = confhan.grab()


        voicechannels = guild.voice_channels
        for vc in voicechannels:
            if str(vc.id) in conf['temp_count_channels_vc'] or vc.id in conf['perm_count_channels_vc']:
                members = vc.members
                for mem in members:
                    if self._create_user(mem) == "bot":
                        continue

                    memhan = js.config(f'{self.userpath}{mem.id}.json')
                    mdat = memhan.grab()

                    mdat['update_voice'] += 1
                    mdat['today_voice'] += 1
                    mdat['total_voice'] += 1

                    memhan.write(mdat ,indent=self.dataindent )

    @tasks.loop(minutes=1)
    async def update_nicknames(self):
        while not self.bot.is_ready():
            await asyncio.sleep(1)

        users = os.listdir(f'{self.userpath}')

        guild = get(self.bot.guilds, id=self.serverid)

        for name in [i for i in users if i.endswith('.json')]:
            try:
                if name == '0.json':
                    continue

                hand = js.config(f'{self.userpath}{name}')
                dat = hand.grab()
                if not dat['toggle_nick']:
                    continue

                ID = int(name.replace('.json',''))

                member = self._getmemberfrommain(ID)
                

                if guild.me.top_role <= member.top_role:
                    continue

                if dat['squad_name'] == "0":
                    continue


                spath = f'{self.squadpath}{dat["squad_name"].lower()}.json'


                shan = js.config(spath)
                sdat = shan.grab()


                clan_string = f" | {dat['squad_name']} {sdat['squadsuffix']}"

                if member.display_name.endswith(clan_string):
                    continue

                newname = member.display_name.split(' | ')[0]

                if len(newname) > 15:
                    newname = newname[:14]

                newname += clan_string
                try:


                    await member.edit(nick=newname)
                except:
                    pass
                    
                await asyncio.sleep(0.5)

            except Exception as e:
                pass
                #print(f'> Exception in update_nicknames for name: {name} error: {e}')

    @tasks.loop(seconds=10)
    async def update_activated_squads(self):
        squads = os.listdir(f'{self.squadpath}')
        while not self.bot.is_ready():
            await asyncio.sleep(1)

        

        for name in [i for i in squads if i.endswith('.json')]:
            try:

                sqhan = js.config(f'{self.squadpath}{name}')

                sq = sqhan.grab()



                try:
                    if sq['member_count'] < 4 and self._isactivated(sq['squadname']):
                        sq['activated'] = False
                        sqhan.write(sq)
                        sq = sqhan.grab()

                        continue
                except:
                    continue


                


                if not self._isactivated(sq['squadname']):
                    suc = await self._activatesquad(sq["squadname"])

                
                if sq['member_count'] >= 4:
                    suc = True

                
                if not sq['channel_allow']:
                    
                    if sq['squad_channel'] != 0:
                        chan = self._getchannelfrommain(sq['squad_channel'])
                        anchorchan = self._getchannelfrommain(665196276291207178)

                        if chan == None:
                            if anchorchan == None:
                                continue

                        everyone = self._getrolefrommain(self.everyonerole)
                        overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024))}
                        if chan.overwrites != overwrites:
                            await chan.edit(overwrites = overwrites)
                    continue

                if suc:

                    if sq["squad_channel"] == 0:
                        guild = get(self.bot.guilds,id=self.serverid)
                        cat = get(guild.categories,id=self.sq_cat)

                        everyone = self._getrolefrommain(self.everyonerole)

                        sq_members = [self._getmemberfrommain(i) for i in sq['members']]

                        mods = self._getrolefrommain(542298007765516298)
                        overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024)), mods : discord.PermissionOverwrite.from_pair(discord.Permissions(1024), discord.Permissions(2048))}

                        for i in sq_members:
                            if i != None:
                                if i.id == sq['leader']:
                                    overwrites[i] = discord.PermissionOverwrite.from_pair(discord.Permissions(140288), discord.Permissions(0))
                                    continue
                                overwrites[i] = discord.PermissionOverwrite.from_pair(discord.Permissions(33792), discord.Permissions(0))
                        

                        chan = await cat.create_text_channel(name=f'{sq["squadname"]}-{sq["squadsuffix"]}',overwrites=overwrites, topic='Squad Chat')
                        leader = self._getmemberfrommain(sq["leader"])
                        sq = sqhan.grab()
                        sq['squad_channel'] = chan.id
                        sqhan.write(sq)

                        await chan.send(f'> <a:yayhyper:658788790432956427> This channel has been created for your squad! **Your squad is now activated!** {leader.mention}')
                        continue
                    else:

                        chan = self._getchannelfrommain(sq['squad_channel'])
                        anchorchan = self._getchannelfrommain(665196276291207178)
                        if chan == None:

                            if anchorchan == None:
                                continue
                            
                            chanretry = self._getchannelfrommain(sq['squad_channel'])

                            #print(f'------------\nSituation 1 of set sc to 0\nValues at time:\n\nChannel: {chan}\nChannel Retry: {chanretry}\nBot ready: {self.bot.is_ready()}\nConnection Closed: {self.bot.is_closed()}\nChannel List: \n---{", ".join([channel.name for channel in main.text_channels])}\n---\nInput channel check name: {sq["squadname"].lower()}-{sq["squadsuffix"].lower()}')
                            
                            sq = sqhan.grab()
                            sq['squad_channel'] = 0
                            sqhan.write(sq)

                            continue

                        everyone = self._getrolefrommain(self.everyonerole)

                        sq_members = [self._getmemberfrommain(i) for i in sq['members']]
                        mods = self._getrolefrommain(542298007765516298)
                        overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024)), mods : discord.PermissionOverwrite.from_pair(discord.Permissions(1024), discord.Permissions(2048))}

                        for i in sq_members:
                            if i != None:
                                if i.id == sq['leader']:
                                    overwrites[i] = discord.PermissionOverwrite.from_pair(discord.Permissions(140288), discord.Permissions(0))
                                    continue
                                overwrites[i] = discord.PermissionOverwrite.from_pair(discord.Permissions(33792), discord.Permissions(0))

                        if chan.overwrites != overwrites:
                            await chan.edit(overwrites=overwrites)
                            continue
                        else:
                            continue

                        

                else:
                    if sq["squad_channel"] != 0:

                        chan = self._getchannelfrommain(sq['squad_channel'])
                        anchorchan = self._getchannelfrommain(665196276291207178)
                        if chan == None:
                            if anchorchan == None:
                                continue

                            sq = sqhan.grab()
                            sq['squad_channel'] = 0
                            sqhan.write(sq)

                            continue

                        everyone = self._getrolefrommain(self.everyonerole)

                        overwrites = {everyone : discord.PermissionOverwrite.from_pair(discord.Permissions(0), discord.Permissions(1024))}
                        if chan.overwrites != overwrites:
                            await chan.edit(overwrites = overwrites)
                            #leader= self._getmemberfrommain(sq["leader"]).mention
                            #await chan.send(f'> :no_bell: The squad\'s chat has been frozen until it is activated again! {leader}')
            
            except Exception as e:
                print(f'>> Exception in update_activated_squads : ')
                traceback.print_exc()

            await asyncio.sleep(0.5)

    ## TODO
    """
        -  Missing Leader event is BROKEN FIXME
        -  There is no event for when a member leaves the server smh
    """

    # @tasks.loop(seconds=1)
    # async def on_missing_leader(self):
    #     squads = os.listdir(f'{self.squadpath}')
    #     while not self.bot.is_ready():
    #         await asyncio.sleep(1)

    #     for name in [i for i in squads if i.endswith('.json')]:
    #         try:

    #             sqhan = js.config(f'{self.squadpath}{name}')

    #             sq = sqhan.grab()

    #             anchoruser = 231463189487943690

    #             if not os.path.exists(f'{self.userpath}{sq["leader"]}.json'):
    #                 continue
    #             uhan = js.config(f'{self.userpath}{sq["leader"]}.json')
    #             udat = uhan.grab()

    #             if udat in [None, {}]:
    #                 continue

    #             if self._getmemberfrommain(sq['leader']) == None:
    #                 if self._getmemberfrommain(anchoruser) == None:
    #                     continue
                    
                    
    #                 if udat == '0':
    #                     print('Leader left')
    #                     udat['last_left'] = self._timetostr(datetime.utcnow())

    #                     uhan.write(udat)

    #                 else:

    #                     if datetime.utcnow() - self._strtotime(udat['last_left']) > timedelta(minutes=5):
    #                         os.remove(f'{self.userpath}{sq["leader"]}.json')

                            
    #                         if len(sq['members']) != 1:
    #                             oldest = (0,datetime.utcnow() - timedelta(days=10950))
    #                             for member in sq['members']:
    #                                 mhan = js.config(f'{self.userpath}{member}.json')
    #                                 mdat = uhan.grab()
    #                                 if self._strtotime(mdat['last_joined_squad']) < oldest[1]:
    #                                     oldest = (member, mdat['last_joined_squad'])
    #                             if oldest[0] == 0:
    #                                 os.remove(f'{self.squadpath}{name}')
    #                                 continue
    #                             else:
    #                                 sq = sqhan.grab()
    #                                 sq['leader'] = oldest[0]
    #                                 sqhan.write(sq)
    #                                 continue
    #                         else:
    #                             os.remove(f'{self.squadpath}{name}')
    #                             continue
                                    


    #             else:
                    
    #                 if udat['last_left'] != '0':
    #                     print('Leader rejoined')
    #                     udat['last_left'] = '0'
    #                     uhan.write(udat)
    #         except:
    #             print(f'>> Exception in on_missing_leader : ')
    #             traceback.print_exc()

 



  

                            
def setup(bot):
    bot.add_cog(Squads(bot))


