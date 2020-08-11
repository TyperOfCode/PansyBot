import datetime
import discord
import string
import os

from discord.ext import tasks, commands
from random import choice

from utils.functions import func
from utils import functions
from utils import sql

config = functions.get("utils/config.json")

class cotd(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.FILEPATH = os.path.abspath(__file__)
        self.FILEDIR = self.FILEPATH.replace(os.path.basename(self.FILEPATH), '')
        self.SAVELOC = "./modules/cogs/data/cotd/"

        self.MAL_ID = 540784184470274069
        self.pingroleid = 661212314908884992

        self.yesno = lambda x : ':white_check_mark:' if x == '1' else ':x:'

    @commands.group()
    async def channel(self, ctx):

        if not ctx.guild:
            return

        if ctx.invoked_subcommand is None:
            page = f"""
            `{ctx.prefix}channel add` - adds a channel to the list of cotd choices
            `{ctx.prefix}channel remove` - removes a channel from the list of cotd choices
            `{ctx.prefix}channel list` - lists the current cotd choices
            `{ctx.prefix}channel removeall` - clears the cotd choicelist
            `{ctx.prefix}channel reset` - resets the channels
            `{ctx.prefix}channel choosenow` - Chooses a cotd channel immediately
            """

            await ctx.send(embed=func.Embed(page))

    @channel.command()
    async def add(self, ctx, channel: discord.TextChannel = None):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        if not channel:
            return await ctx.send(embed=func.ErrorEmbed('Please mention a channel to add to the list'))

        multiple = False

        if len(ctx.message.channel_mentions) > 1:
            multiple = True

        multilist = []

        for i in ctx.message.channel_mentions:

            channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')
            if str(i.id) in [i.split('|')[0] for i in channellist]:
                await ctx.send(embed=func.ErrorEmbed(f'{i.mention} is already in the list, skipping..'))
                continue

            if not multiple:
                await ctx.send(embed=func.Embed(f'Channel {i.mention} has been added to the list'))

            write = open(self.SAVELOC + 'cotd.txt', 'a')
            write.write(f"\n{i.id}|0")
            write.close()

            multilist.append(i)

        if multiple:
            channelmentions = ''
            for i in multilist:
                channelmentions += f'{i.mention}, '

            await ctx.send(embed=func.Embed(f'Channels {channelmentions} have been added to the list'))

    @channel.command()
    async def remove(self, ctx, channel: discord.TextChannel = None):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        if not channel:
            return await ctx.send(embed=func.ErrorEmbed('Please mention a channel to remove from the list'))

        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

        if str(channel.id) not in [i.split('|')[0] for i in channellist]:
            return await ctx.send(embed=func.ErrorEmbed(f'{channel.mention} is not in the list'))

        await ctx.send(embed=func.Embed(f'Channel {channel.mention} has been removed from the list'))

        st = ''
        for i in channellist:
            if i.split('|')[0] != str(channel.id):
                st += f'\n{i}'

        write = open(self.SAVELOC + 'cotd.txt','w')
        write.write(st)
        write.close()

    @channel.command()
    async def removeall(self, ctx):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        write = open(self.SAVELOC + 'cotd.txt','w')
        write.write('')
        write.close()

        await ctx.send(embed=func.Embed('The list has been cleared!'))

    @channel.command()
    async def list(self, ctx):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

        chanstr = ''

        for i in channellist:
            if i == '':
                continue
            splitted = i.split('|')

            channel = await self.bot.fetch_channel(int(splitted[0]))

            chanstr += f'{channel.mention} - {self.yesno(splitted[1])}\n'
        if chanstr != '':
            await ctx.send(embed=func.Embed(chanstr))
        else:
            await ctx.send(embed=func.Embed('The channel list is empty!'))
        return

    @channel.command()
    async def reset(self, ctx):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        channellist = open(self.SAVELOC + 'cotd.txt','r').read().split('\n')

        msg = await ctx.send(embed=func.Embed('Resetting the list....'))

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
                await returnchannel.edit(name=save[1], category=returncategory, position=int(save[3]))
            except:
                pass
        except:
            pass

        reset = open(self.SAVELOC + 'cotdSave.txt','w')
        reset.close()

        await msg.edit(embed=func.Embed('The list has been resetted!'))

    @channel.command()
    async def _choosenow(self, ctx):

        if not ctx.guild:
            return

        if not ctx.guild.id == self.MAL_ID:
            return

        if not sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        chooselist = []

        channellist = open(self.SAVELOC + 'cotd.txt', 'r').read().split('\n')

        for i in channellist:
            if '|0' in i:
                chooselist.append(int(i.split('|')[0]))

        save = open(self.SAVELOC + 'cotdSave.txt', 'r').read().split('\n')

        if chooselist == []:
            try:
                returnchannel = await self.bot.fetch_channel(int(save[0]))
                returncategory = await self.bot.fetch_channel(int(save[2]))
                await ctx.send(embed=func.ErrorEmbed('Cant choose from complete or empty list'))
                try:
                    await returnchannel.edit(name=save[1],category=returncategory,position=int(save[3]))
                except:
                    pass
            except:
                pass

            channellist = open(self.SAVELOC + 'cotd.txt', 'r').read().split('\n')

            st = ''
            for i in channellist:
                if i != '':
                    st += '\n{}|0'.format(i.split('|')[0])

            write = open(self.SAVELOC + 'cotd.txt', 'w')
            write.write(st)
            write.close()
            reset = open(self.SAVELOC + 'cotdSave.txt', 'w')
            reset.close()

            chooselist = []

            channellist = open(self.SAVELOC + 'cotd.txt', 'r').read().split('\n')

            for i in channellist:
                if '|0' in i:
                    chooselist.append(int(i.split('|')[0]))

            save = open(self.SAVELOC + 'cotdSave.txt', 'r').read().split('\n')

        channel = await self.bot.fetch_channel(int(choice(chooselist)))

        st = ''
        for i, v in enumerate(channellist):
            if v.startswith(str(channel.id)):
                channellist[i] = f'{channel.id}|1'
            st += '\n%s'%(channellist[i])

        write = open(self.SAVELOC + 'cotd.txt', 'w')
        write.write(st)
        write.close()

        if len(save) == 4:
            try:
                returnchannel = await self.bot.fetch_channel(int(save[0]))
                returncategory = await self.bot.fetch_channel(int(save[2]))
            except:
                pass
            try:
                await returnchannel.edit(name=save[1], category=returncategory, position=int(save[3]))
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
            await ctx.send(embed=func.Embed(f'Chose {channel.name}'))
            await channel.edit(name=newname,category=None)

            pingrole = discord.utils.get(discord.utils.get(self.bot.guilds, id=self.MAL_ID).roles, id=self.pingroleid)
            await pingrole.edit(mentionable=True)
            await channel.send(f'{pingrole.mention}', delete_after=2)
            await pingrole.edit(mentionable=False)
        except:
           return

    @tasks.loop(seconds=1)
    async def cotdchoose(self):

        time = datetime.datetime.now().strftime("%H:%M:%S")
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
                        await returnchannel.edit(name=save[1], category=returncategory, position=int(save[3]))
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

                await channel.edit(name=newname, category=None)

                pingrole = discord.utils.get(discord.utils.get(self.bot.guilds, id=self.MAL_ID).roles, id=self.pingroleid)
                await pingrole.edit(mentionable=True)
                await channel.send(f'{pingrole.mention}', delete_after=2)
                await pingrole.edit(mentionable=False)
            except:
                return

def setup(bot):
    bot.add_cog(cotd(bot))
