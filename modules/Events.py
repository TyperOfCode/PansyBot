import discord


import random
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 540784184470274069:
            guild = self.bot.get_guild(540784184470274069)
            people = format(len(guild.members), ",")
            watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
            await self.bot.change_presence(activity=watch)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 540784184470274069:
            guild = self.bot.get_guild(540784184470274069)
            people = format(len(guild.members), ",")
            watch = discord.Activity(type=discord.ActivityType.watching, name=f"over {people} people")
            await self.bot.change_presence(activity=watch)

    @commands.Cog.listener(name="on_message")
    async def on_message_pingcheck(self, message):
        try:
            if 439327545557778433 in message.raw_mentions:
                await message.add_reaction("<a:malBH:629149080286789633>")
        except Exception:
            return

    @commands.Cog.listener(name="on_message")
    async def on_message_check(self, message):
        if 'Stig' in message.content.split() or 'stig' in message.content.split():
            user = await self.bot.fetch_user(439327545557778433)

        if 'dirt' in message.content.lower().replace(' ',''):
            user = await self.bot.fetch_user(636808158521589770)

        embed = discord.Embed(colour=0xc70300, description=message.content)
        embed.add_field(name="Who", value=message.author.mention, inline=True)
        embed.add_field(name="Where", value=message.channel.name, inline=True)
        embed.add_field(name="Jump", value=f"[Link]({message.jump_url})", inline=True)

        await user.send(embed=embed)

    @commands.Cog.listener(name="on_member_update")
    async def on_verified_role_given(self, before, after):
        if 660174109501554717 not in [i.id for i in before.roles]:
            if 660174109501554717 in [i.id for i in after.roles]:
                verifiedChannel = await self.bot.fetch_channel(719211743808716880)
                verifiedEmbed = discord.Embed(title = f"Welcome to Our Community {after.name} <a:malNekoHeart:720291512046321666>", description = "<a:malHeartu:608280365605453844> Thanks for introducing yourself, get to know everyone and enjoy your stay! <a:malMarihearts:720322374440058930> ", color=random.choice([0x91F586, 0x41C533, 0x18FE00, 0x66ED5D]))
                verifiedEmbed.set_footer(text=f"Be sure to check the pinned messages of each channel!", icon_url=after.avatar_url)
                await verifiedChannel.send(embed=verifiedEmbed, content=after.mention)


def setup(bot):
    bot.add_cog(Events(bot))
