from discord.ext import commands, tasks
from typing import Union
import asyncio
import datetime
import discord.utils
import traceback

from random import randint

class RateMyAvatar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.rating_channel_id = 669566246227935263
        self.rating_message_id: Union[int, None] = None
        self.rated_user_id: Union[int, None] = None
        self.rating_cooldown = {}
        self.cooldown_time = 24
        self.numeric_reaction_to_rating = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5, '6️⃣': 6, '7️⃣': 7, '8️⃣': 8, '9️⃣': 9, '🔟': 10}
        self.number_rating_to_emoji_reation = {1: 626479116643860480, 2: 593137372615671843, 3: 660459012650827777, 4: 642018487996383242, 5: 587373930579230724, 6: 607838396349677568, 7: 662915142878494730, 8: 593872466095636500, 9: 614525816360927233, 10: 608278534456344577,}

        self.initialize_rating.start()

    async def __send_avatar_to_rate(self, rating_user: Union[discord.User, discord.Member], rating_channel: discord.abc.GuildChannel):
        embed = discord.Embed(title=f'Rate {rating_user.display_name}\'s avatar from 1-10!', color=discord.Color.blurple())
        embed.set_image(url=rating_user.avatar_url)
        message = await rating_channel.send(embed=embed)

        self.rating_message_id = message.id

        for numeric_reaction in self.numeric_reaction_to_rating:
            await message.add_reaction(numeric_reaction)
            await asyncio.sleep(1/4)

    @tasks.loop(count=1)
    async def initialize_rating(self):
        await self.bot.wait_until_ready()

        rating_channel = self.bot.get_channel(self.rating_channel_id)
        if rating_channel is None:
            print('[RateMyAvatar] The #ratemyavatar channel does not exist. Shutting down the RateMyAvatar cog.')
            self.bot.remove_cog(self.qualified_name)

        rating_user = None
        guild = self.bot.get_guild(540784184470274069)
        members = guild.members
        choice = randint(0, len(members))
        rating_user = members[choice]

        self.rating_cooldown[rating_user.id] = datetime.datetime.now()
        await self.__send_avatar_to_rate(rating_user, rating_channel)


    @commands.Cog.listener('on_reaction_add')
    async def reaction_handler(self, reaction: discord.Reaction, reaction_user: Union[discord.User, discord.Member]):

        if reaction_user.bot:
            return

        if reaction.message.id != self.rating_message_id:
            return

        if reaction_user.id in self.rating_cooldown:
            user_cooldown = self.rating_cooldown[reaction_user.id]

            now = datetime.datetime.now()
            difference = now - self.rating_cooldown[reaction_user.id]
            hours = difference.total_seconds() / 3600

            if hours < self.cooldown_time:
                await reaction.remove(reaction_user)
                return
        else:
            self.rating_cooldown[reaction_user.id] = datetime.datetime.now()

        # check if the rating channel exists still
        guild = self.bot.get_guild(540784184470274069)
        rating_channel = guild.get_channel(self.rating_channel_id)
        if rating_channel is None:
            print('[RateMyAvatar] The #ratemyavatar channel does not exist. Shutting down the RateMyAvatar cog.')
            self.bot.remove_cog(self.qualified_name)
            return

        # if the user adds a foreign emoji or it's the user meant to be reacted to, remove reaction
        if not str(reaction) in self.numeric_reaction_to_rating or reaction_user.id == self.rated_user_id:
            await reaction.remove(reaction_user)
            return

        # check if the user exists still (if they left)
        reacted_message_user = self.bot.get_user(self.rated_user_id)
        if reacted_message_user is None:
            await rating_channel.send(f'It seems that the user that you rated has left, {reaction_user.mention}! Let\'s rate your avatar instead!')
        else:
            avatar_rating_value = self.numeric_reaction_to_rating[str(reaction)]
            avatar_rating_emoji_id = self.number_rating_to_emoji_reation[avatar_rating_value]
            avatar_rating_emoji = str(self.bot.get_emoji(avatar_rating_emoji_id))

            await rating_channel.send(f'{reacted_message_user.mention}, your avatar has been rated {avatar_rating_value}/10 by {reaction_user.mention}! {avatar_rating_emoji}')

        self.rated_user_id = reaction_user.id
        await self.__send_avatar_to_rate(reaction_user, rating_channel)


def setup(bot: commands.Bot):
    bot.add_cog(RateMyAvatar(bot))
