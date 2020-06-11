import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
import datetime
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL

from utils.essentials import functions
from utils.essentials.functions import func


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpegopts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def create_source(self, cls, ctx, search: str, *, loop, stream=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=not stream)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            data = data['entries'][0]

        views = data["view_count"]

        embed = discord.Embed(
            colour=0x9bf442,
            description="Added {} to the Queue".format(data["title"]),
            timestamp=datetime.datetime.utcnow()
            )

        embed.set_thumbnail(url=data["thumbnail"])
        embed.set_author(name=f"{ctx.author.name} Enqueued a song", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Views", value=f"{views:,}", inline=True)
        embed.add_field(name="Artist", value=data["creator"], inline=True)
        embed.add_field(name="URL", value="[Youtube]({})".format(data["uploader_url"]), inline=True)

        await ctx.send(embed=embed)

        if stream:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):

        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            loop = asyncio.get_event_loop()
            to_run = partial(ytdl.extract_info, url=source.title, download=False)
            data = await loop.run_in_executor(None, to_run)

            if 'entries' in data:
                data = data['entries'][0]

            views = data["view_count"]

            embed = discord.Embed(
                colour=0x9bf442,
                description=f"Now playing {source.title}",
                timestamp=datetime.datetime.utcnow()
                )

            embed.set_thumbnail(url=data["thumbnail"])
            embed.set_author(name=f"{source.requester.name} requested a song", icon_url=source.requester.avatar_url)
            embed.add_field(name="Views", value=f"{views:,}", inline=True)
            embed.add_field(name="Artist", value=data["creator"], inline=True)
            embed.add_field(name="URL", value="[Youtube]({})".format(data["uploader_url"]), inline=True)

            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            source.cleanup()
            self.current = None

            try:
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join', 'summon'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return

        if ctx.voice_client:
            if ctx.voice_client.channel.id == channel.id:
                return
            try:
                await ctx.voice_client.move_to(channel)
            except asyncio.TimeoutError:
                return
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                return

    @commands.command(name='play', aliases=['sing'])
    async def play_(self, ctx, *, search: str):
        if not ctx.voice_client:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        source = await YTDLSource.create_source(self, ctx, search, loop=self.bot.loop)

        await player.queue.put(source)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.author.voice:
                if not ctx.voice_client.is_paused():
                    ctx.voice_client.pause()
                    await ctx.send(embed=self.MEmbed("The current track has been paused.", f"{ctx.author.name} paused the music!", ctx.author.avatar_url))
            else:
                await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
        else:
            await ctx.send(embed=self.ENoFooter("Im not playing anything!"))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def resume(self, ctx):
        if ctx.voice_client and not ctx.voice_client.is_playing():
            if ctx.author.voice:
                if ctx.voice_client.is_paused():
                    ctx.voice_client.resume()
                    await ctx.send(embed=self.MEmbed("The current track has been resumed.", f"{ctx.author.name} resumed the music!", ctx.author.avatar_url))
            else:
                await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
        else:
            await ctx.send(embed=self.ENoFooter("Im not playing anything!"))

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            if ctx.author.voice:
                    ctx.voice_client.stop()
                    await ctx.send(embed=self.MEmbed("The current track has been skipped.", f"{ctx.author.name} skipped the current song!", ctx.author.avatar_url))
            else:
                await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
        else:
            await ctx.send(embed=self.ENoFooter("Im not playing anything!"))


    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_info(self, ctx):
        if ctx.voice_client:
            player = self.get_player(ctx)
            if not player.queue.empty():
                upcoming = list(itertools.islice(player.queue._queue, 0, 5))
                fmt = '\n'.join(f'__{_["title"]}__' for _ in upcoming)
                embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt, colour=0x9bf442)
                await ctx.send(embed=embed)
            else:
                return await ctx.send(embed=self.ENoFooter("The queue is empty"))
        else:
            return await ctx.send(embed=self.ENoFooter("Im not playing anything!"))

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        if ctx.voice_client:
            player = self.get_player(ctx)
            if player.current:
                try:
                    await player.np.delete()
                except discord.HTTPException:
                    pass
                player.np = await ctx.send(embed=self.MEmbed(f"Now playing {ctx.voice_client.source.title}", f"{ctx.voice_client.source.requester.name} requested a song", ctx.voice_client.source.requester.avatar_url))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def volume(self, ctx, volume: int):
        if ctx.voice_client:
            if ctx.author.voice:
                if volume > 0 and volume <= 100:
                    player = self.get_player(ctx)
                    ctx.voice_client.source.volume = volume / 100
                    player.volume = volume / 100
                    await ctx.send(embed=self.MEmbed(f"The volume is now {volume}%", f"{ctx.author.name} set the volume!", ctx.author.avatar_url))
                else:
                    await ctx.send(embed=self.ENoFooter("Please enter a volume between 0% and 100%!"))
            else:
                await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
        else:
            await ctx.send(embed=self.ENoFooter("Im not in a voice channel!"))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
     if ctx.voice_client:
         if ctx.author.voice:
             if ctx.author is ctx.voice_client.source.requester or not ctx.voice_client.source.requester:
                 await ctx.voice_client.disconnect()
                 await self.cleanup(ctx.guild)
             else:
                 await ctx.send(embed=self.ENoFooter("Only the song requester can stop the current track!"))
         else:
             await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
     else:
         await ctx.send(embed=self.ENoFooter("Im not in a voice channel!"))

     @commands.command()
     @commands.cooldown(1, 10, commands.BucketType.guild)
     async def sstop(self, ctx):
         if ctx.author.guild_permissions.manage_roles:
             if ctx.voice_client:
                 if ctx.author.voice:
                     await ctx.voice_client.disconnect()
                     await self.cleanup(ctx.guild)
                 else:
                     await ctx.send(embed=self.ENoFooter("You arent in a voice channel!"))
             else:
                 await ctx.send(embed=self.ENoFooter("Im not in a voice channel!"))
         else:
             await ctx.send(embed=func.NoPerm())

    def MEmbed(self, description, author, avatar):
        embed = discord.Embed(
            description =  description,
            colour = 0x9bf442,
            timestamp=datetime.datetime.utcnow()
            )
        embed.set_author(name=author, icon_url=avatar)

        return embed

    def ENoFooter(self, title):
        embed = discord.Embed(
            title = title,
            timestamp=datetime.datetime.utcnow(),
            colour = 0xd42c2c
            )

        return embed


def setup(bot):
    bot.add_cog(Music(bot))
