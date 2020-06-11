import datetime
import discord
import time

from discord.ext import commands,tasks

class RateMyAvatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.rating_channel_id = 700865540213833760
        self.rating_channel = None

        self.rating_message = None

        self.users = {}

        self.user_to_rate = None

        self.cooldown = 2

        self.emotes = {'1️⃣': 1, '2️⃣': 2, '3️⃣': 3, '4️⃣': 4, '5️⃣': 5, '6️⃣': 6, '7️⃣': 7, '8️⃣': 8, '9️⃣': 9, '🔟': 10}

        self.reactions = {1: "<:malSaayaWhaa:640472459350376468>", 2: "<a:malKawaiispooked:653601138720899101>", 3: "<:malKanonCry:644320461135806464>", 4: "<:malThinku:627916285912678429>", 5: "<:malNezukoAnger:625754858405888009>", 6: "<a:malPleaseStop:613541345004486657>", 7: "<:malKasuPray:686770171523891221>", 8: "<:malPouts:642018487996383242>", 9: "<:malYayy:608273843710197761>", 10: "<a:malYay:608280367580971017>"}

        self.init.start()
        self.clearCooldown.start()

    @tasks.loop(count=1)
    async def init(self):
        try:
            self.rating_channel = await self.bot.fetch_channel(self.rating_channel_id)
            """if self.rating_channel is None:
                print('[RateMyAvatar] The #ratemyavatar channel does not exist. Shutting down the RateMyAvatar cog.')
                self.bot.unload_extension(f"modules.cogs.ratemyavatar1")"""

            message = await self.rating_channel.fetch_message(self.rating_channel.last_message_id)

            self.user_to_rate = message.author

            self.rating_message = await self.SendAvatar()
        except Exception as e:
            print(e)

    @tasks.loop(seconds=5)
    async def clearCooldown(self):
        for user in self.users:
            if datetime.datetime.now() > self.users[user]:
                try:
                    del self.users[user]
                    return
                except:
                    return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print(payload)
        #user = await self.bot.fetch_user(payload.user_id)
        if payload.member.bot or payload.member == self.user_to_rate:
            return

        if payload.message_id != self.rating_message.id:
            print(f"MessageID Didnt Match {payload.message_id} --- {self.rating_message.id}")
            return

        if payload.user_id in self.users:
            return await self.CooldownMessage(payload.member)

        avatar_rating = self.emotes[str(payload.emoji)]

        emote_rating = self.reactions[avatar_rating]

        await self.rating_channel.send(f"{self.user_to_rate.mention}, your avatar has been rated {avatar_rating}/10 by {payload.member.mention}! {emote_rating}")

        self.user_to_rate = payload.member

        self.users[self.user_to_rate.id] = datetime.datetime.now() + datetime.timedelta(hours=self.cooldown)

        self.rating_message = await self.SendAvatar()

    async def SendAvatar(self):
        embed = discord.Embed(colour=self.user_to_rate.top_role.colour)

        embed.set_image(url=self.user_to_rate.avatar_url)
        embed.set_author(name=f"Rate {self.user_to_rate.display_name}'s avatar!")

        e = await self.rating_channel.send(embed=embed)

        for emote in self.emotes:
            await e.add_reaction(emote)

        return e

    def CalcTime(self, userid):
        delta =  self.users[userid] - datetime.datetime.now()
        secs = delta.total_seconds()
        return secs

    async def CooldownMessage(self, user):
        secs = self.CalcTime(user.id)
        coolTime = time.gmtime(secs)
        embed = discord.Embed(description="You can rate another avatar in {}".format(time.strftime("%H hours, %M minutes and %S seconds.", coolTime)), colour=discord.Colour(0xff0000))
        embed.set_author(name=f"You are on cooldown!")

        await user.send(embed=embed)

def setup(bot):
    bot.add_cog(RateMyAvatar(bot))
