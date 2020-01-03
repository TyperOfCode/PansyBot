import discord
from datetime import datetime
from discord.ext import tasks, commands
import asyncio
from discord.utils import get
import os
from random import choice, randint
import string


class cotd(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.FILEPATH = os.path.abspath(__file__)
        self.FILEDIR = self.FILEPATH.replace(os.path.basename(self.FILEPATH),'')
        self.SAVELOC = self.FILEDIR[:-5] + "storageTXT/"

        self.serverid = 540784184470274069
        self.pingroleid = 661212314908884992

        self.servercheck = lambda x : x == self.serverid
        self.dmcheck = lambda x : str(x.channel).startswith('Direct')
        self.yesno = lambda x : ':white_check_mark:' if x is '1' else ':x:'

        self.cotdchoose.start()

    def cog_unload(self):
        self.cotdchoose.cancel()

    def errorembed(self, title, content, guild):
        embed = discord.Embed(title=title,description=content,color=0xff0000)
        embed.set_footer(icon_url=guild.icon_url,text="Error - Pansy - MAL")
        return embed

    def miscembed(self,title,content,guild):
        embed = discord.Embed(title=title,description=content,color=0xB407DE)
        embed.set_footer(icon_url=guild.icon_url,text="Misc - Pansy - MAL")
        return embed

    def acceptembed(self,title,content,guild):
        embed = discord.Embed(title=title,description=content,color=0x00ff00)
        embed.set_footer(icon_url=guild.icon_url,text="Accept - Pansy - MAL")
        return embed

    def adminperms(self, ctx):
        if 542297369698369546 in [y.id for y in ctx.author.roles]:
            return True
        elif 611661848961351691 in [y.id for y in ctx.author.roles]:
            return True
        else:
            return False

    @commands.group(name='channel')
    async def _channel(self,ctx):
        """The channel group , base for all ^channel commands"""

        if not self.dmcheck(ctx.message):
            if ctx.invoked_subcommand is None:
                page = """
                `{p}channel add` - adds a channel to the list of cotd choices
                `{p}channel remove` - removes a channel from the list of cotd choices
                `{p}channel list` - lists the current cotd choices
                `{p}channel removeall` - clears the cotd choicelist
                `{p}channel reset` - resets the channels
                `{p}channel choosenow` - Chooses a cotd channel immediately
                """.replace('            ','').format(p='p^')

                await ctx.send(embed=self.miscembed('Channel Help Page',page,ctx.guild)) 


    @_channel.command(name='add')
    async def _add(self, ctx, channelm: discord.TextChannel = None):
        """add the mentioned channel to the list"""

        if not self.dmcheck(ctx.message):

            if self.adminperms(ctx):  
            
                if self.servercheck(ctx.guild.id):
                    
                        if channelm == None:
                            await ctx.send(embed=self.errorembed('Error - Missing argument','Please mention a channel to add to the list',ctx.guild))
                            return

                        multiple = False

                        if len(ctx.message.channel_mentions) > 1:
                            multiple = True

                        multilist = []
                       
                        
                        for i in ctx.message.channel_mentions:
                            ### alrighty here we go

                            channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')
                            if str(i.id) in [i.split('|')[0] for i in channellist]:
                                await ctx.send(embed=self.errorembed('Error - Dupecheck',f'{i.mention} is already in the list, skipping..',ctx.guild))
                                continue
                            
                            if not multiple:
                                await ctx.send(embed=self.acceptembed('Success!',f'Channel {i.mention} has been added to the list',ctx.guild))
                            
                            write = open(self.SAVELOC + 'cotd.txt','a')
                            write.write(f"\n{i.id}|0")
                            write.close()

                            multilist.append(i)

                        if multiple:
                            channelmentions = ''
                            for i in multilist:
                                channelmentions += f'{i.mention}, '
                            
                            await ctx.send(embed=self.acceptembed('Success!',f'Channels {channelmentions} have been added to the list',ctx.guild))

                        return
                else:
                    await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))
            else:
                await ctx.send(embed=self.errorembed('Error - Missing Permissions','You dont have the authority to use this command',ctx.guild))
                return 
        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

    @_channel.command(name='remove')
    async def _remove(self, ctx, channelm: discord.TextChannel = None):
        """remove the mentioned channel from the list"""

        if not self.dmcheck(ctx.message):

            if self.adminperms(ctx):  
            
                if self.servercheck(ctx.guild.id):
                    
                        if channelm == None:
                            await ctx.send(embed=self.errorembed('Error - Missing argument','Please mention a channel to remove from the list',ctx.guild))
                            return
                        


                        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                        if str(channelm.id) not in [i.split('|')[0] for i in channellist]:
                            await ctx.send(embed=self.errorembed('Error - ID Check',f'{channelm.mention} is not in the list',ctx.guild))
                            return

                        await ctx.send(embed=self.acceptembed('Success!',f'Channel {channelm.mention} has been removed from the list',ctx.guild))

                        st = ''
                        for i in channellist:
                            if i.split('|')[0] != str(channelm.id):
                                st += f'\n{i}'

                        write = open(self.SAVELOC + 'cotd.txt','w')
                        write.write(st)
                        write.close()


                        return
                else:
                    await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

            else:
                await ctx.send(embed=self.errorembed('Error - Missing Permissions','You dont have the authority to use this command',ctx.guild))
                return 

        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

    @_channel.command(name='removeall')
    async def _removeall(self, ctx):
        """removes the list"""

        if not self.dmcheck(ctx.message):

            if self.adminperms(ctx):  
            
                if self.servercheck(ctx.guild.id):
                    
                        write = open(self.SAVELOC + 'cotd.txt','w')
                        write.write('')
                        write.close()

                        await ctx.send(embed=self.acceptembed('Success!',f'The list has been cleared!',ctx.guild))

                        return
                else:
                    await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

            else:
                await ctx.send(embed=self.errorembed('Error - Missing Permissions','You dont have the authority to use this command',ctx.guild))
                return 

        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

    @_channel.command(name='list')
    async def _list(self, ctx):
        """lists all the channels that are on the list"""

        if not self.dmcheck(ctx.message):


            
            if self.servercheck(ctx.guild.id):
                
                    
                    channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                    chanstr = ''

                    for i in channellist:
                        if i == '':
                            continue
                        splitted = i.split('|')

                        channel = await self.bot.fetch_channel(int(splitted[0]))

                        chanstr += f'{channel.mention} - {self.yesno(splitted[1])}\n'
                    if chanstr != '':
                        await ctx.send(embed=self.miscembed('Channel List',chanstr,ctx.guild))
                    else:
                        await ctx.send(embed=self.miscembed('Channel list','The channel list is empty!',ctx.guild))
                    return
            else:
                await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

            

        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

    @_channel.command(name='reset')
    async def _reset(self, ctx):
        """remove the mentioned channel to the list"""

        if not self.dmcheck(ctx.message):

            if self.adminperms(ctx):  
            
                if self.servercheck(ctx.guild.id):
                        

                        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                        
                        msg = await ctx.send(embed=self.miscembed('Resetting list','Resetting the list....',ctx.guild))


                        st = ''
                        for i in channellist:
                            if i != '':
                                try:
                                    trye = await self.bot.fetch_channel(int(i.split('|')[0]))
                                    st += '\n{}|0'.format(i.split('|')[0])
                                except:
                                    pass

                        write = open(self.SAVELOC + 'cotd.txt','w')
                        write.write(st)
                        write.close()


                        

                        

                        save = open(self.SAVELOC + 'cotdSave.txt','r').read().split('\n')

                        try:
                            returnchannel = await self.bot.fetch_channel(int(save[0]))
                            returncategory = await self.bot.fetch_channel(int(save[2]))
                            try:
                                await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                            except:
                                pass
                        except:
                            pass

                        reset = open(self.SAVELOC + 'cotdSave.txt','w')
                        reset.close()

                        await msg.edit(embed=self.acceptembed('Success!','The list has been resetted!',ctx.guild))



                        return
                else:
                    await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

            else:
                await ctx.send(embed=self.errorembed('Error - Missing Permissions','You dont have the authority to use this command',ctx.guild))
                return 

        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

    @_channel.command(name='choosenow')
    async def _choosenow(self, ctx):
        """chooeses a cotd immediately"""

        if not self.dmcheck(ctx.message):

            if self.adminperms(ctx):  
            
                if self.servercheck(ctx.guild.id):
                        chooselist = []

                        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                        for i in channellist:
                            if '|0' in i:
                                chooselist.append(int(i.split('|')[0]))

                        save = open(self.SAVELOC + 'cotdSave.txt','r').read().split('\n')

                        if chooselist == []:
                            try:
                                returnchannel = await self.bot.fetch_channel(int(save[0]))
                                returncategory = await self.bot.fetch_channel(int(save[2]))
                                await ctx.send(embed=self.errorembed('List is complete or empty','Cant choose from complete or empty list\n - List has auto been resetted',ctx.guild))
                                try:
                                    await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                                except:
                                    pass
                                
                            except:
                                pass

                            channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')
                            
                            
                            st = ''
                            for i in channellist:
                                if i != '':
                                    st += '\n{}|0'.format(i.split('|')[0])

                            write = open(self.SAVELOC + 'cotd.txt','w')
                            write.write(st)
                            write.close()

                           

        
                            reset = open(self.SAVELOC + 'cotdSave.txt','w')
                            reset.close()

                            chooselist = []

                            channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                            for i in channellist:
                                if '|0' in i:
                                    chooselist.append(int(i.split('|')[0]))

                            save = open(self.SAVELOC + 'cotdSave.txt','r').read().split('\n')

                            

                            
                        
                        channel = await self.bot.fetch_channel(int(choice(chooselist)))

                        st = ''
                        for i, v in enumerate(channellist):
                            if v.startswith(str(channel.id)):
                                channellist[i] = f'{channel.id}|1'
                            st += '\n%s'%(channellist[i])

                        write = open(self.SAVELOC + 'cotd.txt','w')
                        write.write(st)
                        write.close()

                        

                        if len(save) == 4:
                            try:
                                returnchannel = await self.bot.fetch_channel(int(save[0]))
                                returncategory = await self.bot.fetch_channel(int(save[2]))
                            except:
                                pass
                            try:
                                await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                            except:
                                pass
                            
                        new = open(self.SAVELOC + 'cotdSave.txt','w')
                        new.write(f'{channel.id}\n{channel.name}\n{channel.category_id}\n{channel.position}')
                        new.close()

                        newname = '\N{tulip}\u30FB'
                        for i in channel.name:
                            if i in string.ascii_letters or i == '-':
                                newname += i

                        try:
                            await ctx.send(embed=self.acceptembed('Success!',f'Chose {channel.name}',ctx.guild))
                            await channel.edit(name=newname,category=None)

                            
                            pingrole = get(get(self.bot.guilds,id=self.serverid).roles,id=self.pingroleid)
                            await pingrole.edit(mentionable=True)
                            await channel.send(f'{pingrole.mention}',delete_after=2)
                            await pingrole.edit(mentionable=False)
                        except:
                           return


                else:
                    await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))

            else:
                await ctx.send(embed=self.errorembed('Error - Missing Permissions','You dont have the authority to use this command',ctx.guild))
                return 

        else:
            await ctx.send(embed=self.errorembed('Error - Wrong Channel','Please only use the channel commands in the MAL server',ctx.guild))
    
    @tasks.loop(seconds=1)
    async def cotdchoose(self):


        time = datetime.now().strftime("%H:%M:%S")
        if time == '00:00:00':
            chooselist = []

            channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

            for i in channellist:
                if '|0' in i:
                    chooselist.append(int(i.split('|')[0]))

            save = open(self.SAVELOC + 'cotdSave.txt','r').read().split('\n')

            if chooselist == []:
                try:
                    returnchannel = await self.bot.fetch_channel(int(save[0]))
                    returncategory = await self.bot.fetch_channel(int(save[2]))

                    try:
                        await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                    except:
                        pass
                    
                except:
                    pass

                channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')
                
                
                st = ''
                for i in channellist:
                    if i != '':
                        st += '\n{}|0'.format(i.split('|')[0])

                write = open(self.SAVELOC + 'cotd.txt','w')
                write.write(st)
                write.close()

                


                reset = open(self.SAVELOC + 'cotdSave.txt','w')
                reset.close()

                chooselist = []

                channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

                for i in channellist:
                    if '|0' in i:
                        chooselist.append(int(i.split('|')[0]))

                save = open(self.SAVELOC + 'cotdSave.txt','r').read().split('\n')

                
            
            channel = await self.bot.fetch_channel(int(choice(chooselist)))

            st = ''
            for i, v in enumerate(channellist):
                if v.startswith(str(channel.id)):
                    channellist[i] = f'{channel.id}|1'
                st += '\n%s'%(channellist[i])

            write = open(self.SAVELOC + 'cotd.txt','w')
            write.write(st)
            write.close()

            

            if len(save) == 4:
                try:
                    returnchannel = await self.bot.fetch_channel(int(save[0]))
                    returncategory = await self.bot.fetch_channel(int(save[2]))
                except:
                    pass
                try:
                    await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                except:
                    pass
                
            new = open(self.SAVELOC + 'cotdSave.txt','w')
            new.write(f'{channel.id}\n{channel.name}\n{channel.category_id}\n{channel.position}')
            new.close()

            newname = '\N{tulip}\u30FB'
            for i in channel.name:
                if i in string.ascii_letters or i == '-':
                    newname += i

            try:
                
                await channel.edit(name=newname,category=None)

                
                pingrole = get(get(self.bot.guilds,id=self.serverid).roles,id=self.pingroleid)
                await pingrole.edit(mentionable=True)
                await channel.send(f'{pingrole.mention}',delete_after=2)
                await pingrole.edit(mentionable=False)
            except:
                return

            

    
def setup(bot):
    bot.add_cog(cotd(bot))
