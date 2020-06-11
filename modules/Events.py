import discord

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
                await message.add_reaction("<a:malnya:608688667078295557>")
        except Exception:
            return

    @commands.Cog.listener(name="on_message")
    async def on_message_check(self, message):
        if 'Stig' in message.content.split() or 'stig' in message.content.split():
            user = await self.bot.fetch_user(439327545557778433)
            embed = discord.Embed(colour=0xc70300, description=message.content)
            embed.add_field(name="Who", value=message.author.mention, inline=True)
            embed.add_field(name="Where", value=message.channel.mention, inline=True)
            embed.add_field(name="Jump", value=f"[Link]({message.jump_url})", inline=True)

            await user.send(embed=embed)

def setup(bot):
    bot.add_cog(Events(bot))
