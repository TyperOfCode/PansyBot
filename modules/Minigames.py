import datetime

from discord.ext import commands, tasks

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.words = {}
        self.counting = {}

        self.clearCooldown.start()

        self.last_to_delete = None

    @tasks.loop(seconds=10)
    async def clearCooldown(self):
        words = self.words.copy()
        counting = self.counting.copy()

        for user in words:
            if datetime.datetime.utcnow() > words[user]:
                del self.words[user]

        for user in counting:
            if datetime.datetime.utcnow() > counting[user]:
                del self.counting[user]


    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id == 548017507982901258: # Word Chain
            lastWord = await message.channel.history(limit=2).flatten()

            content = message.content.lower()

            if message.author.id != self.bot.user.id:
                if not content.startswith(lastWord[1].content[-1].lower()):
                    return await message.delete()

            if message.author.id != self.bot.user.id:
                if lastWord[1].author.id == message.author.id or self.last_to_delete == message.author.id:
                    await message.delete()
                    return await message.author.send("You cant play Word chain alone. Wait for others!")

            if message.author.id in self.words:
                return

            if message.author.id != self.bot.user.id:
                self.last_to_delete = None

            """if not sql.accountExists(message.author.id):
                return await message.author.send(embed=func.ErrorEmbed(f"Hey! You claimed a card but dont have a sCoin account? What are you doing!? Join now by typing h.sCoin in MAL."))

            useracc = sql.getAccount(message.author.id)
            sql.setCoins(message.author.id, useracc[2] + 0.0025)

            await message.author.send(embed=func.Embed("You gained 0.0025 sCoin for playing Wordchain!"))

            self.words[message.author.id] = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
            sql.sLog(message.author.id, 3, f"Added 0.0025 to {message.author.name}s eCoin balance",datetime.datetime.utcnow())"""

    @commands.Cog.listener(name="on_message")
    async def on_message_(self, message):
        if message.channel.id == 702994016743981197:  # Counting

            lastWord = await message.channel.history(limit=2).flatten()

            try:
                if not int(message.content) == (int(lastWord[1].content) + 1):
                    return await message.delete()
            except:
                return

            if lastWord[1].author.id == message.author.id:
                await message.delete()
                return await message.author.send("You cant count alone. Wait for others!")

            if message.author.id in self.counting:
                return

            """if not sql.accountExists(message.author.id):
                return await message.author.send(embed=func.ErrorEmbed(f"Hey! You claimed a card but dont have a sCoin account? What are you doing!? Join now by typing h.sCoin in MAL."))

            useracc = sql.getAccount(message.author.id)
            sql.setCoins(message.author.id, useracc[2] + 0.0025)

            await message.author.send(embed=func.Embed("You gained 0.0025 sCoin for playing Counting!"))

            self.counting[message.author.id] = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
            sql.sLog(message.author.id, 3, f"Added 0.0025 to {message.author.name}s eCoin balance",datetime.datetime.utcnow())"""

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.channel.id == 548017507982901258: # Word Chain

            lastWord = await message.channel.history(limit=1).flatten()

            content = message.content.lower()

            if not content.startswith(lastWord[0].content[-1].lower()):
                return
            else:
                if self.last_to_delete == message.author.id:
                    return

                self.last_to_delete = message.author.id

                await message.channel.send(f"({message.author.mention}) wrote: {message.content}")

def setup(bot):
    bot.add_cog(Minigames(bot))