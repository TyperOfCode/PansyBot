from discord.ext import commands

class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 548017507982901258: # Word Chain
            lastWord = await message.channel.history(limit=2).flatten()

            content = message.content.lower()

            if not content.startswith(lastWord[1].content[-1].lower()):
                return await message.delete()

            if lastWord[1].author.id == message.author.id:
                await message.delete()
                await message.author.send("You cant play Word chain alone. Wait for others!")

    @commands.Cog.listener(name="on_message")
    async def on_message_(self, message):
        if message.channel.id == 702994016743981197:  # Counting

            lastWord = await message.channel.history(limit=2).flatten()

            if not int(message.content) == (int(lastWord[1].content) + 1):
                return await message.delete()

            if lastWord[1].author.id == message.author.id:
                await message.delete()
                await message.author.send("You cant count alone. Wait for others!")

def setup(bot):
    bot.add_cog(Minigames(bot))
