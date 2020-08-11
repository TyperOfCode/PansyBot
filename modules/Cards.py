import datetime
import discord
import json
import re

from discord.ext import commands, tasks

from utils.functions import func
from utils import sql

class Cards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.network_chat_id = 626749195318984704
        self.shoob_id = 673362753489993749
        self.most_recent_card_name = None
        self.most_recent_tier = None
        self.card_id = None

        # Event

        self.event = {"Started": False, "TotalDuration": None, "Remaining": None, "Reward": None}
        self.event_message = None
        self.leaderboard_message = None
        self.channel = None

        self.update.start()

        with open("./modules/data/cards/MentionRoles.json") as f:
            self.roles = json.load(f)


    def ReloadJSON(self):
        with open("./modules/data/cards/MentionRoles.json") as f:
            self.roles = json.load(f)
            return self.roles

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id != self.network_chat_id:
            return

        if message.author.id != self.shoob_id:
            return

        # Claiming -------------------------------------

        for embed in message.embeds:
            embed = embed.to_dict()

            try:
                if "To claim, use:" in embed["description"]:
                    self.card_id = message.id
                    self.most_recent_card_name = embed['title'][:embed['title'].index("Tier")]
                    tier = embed['title'].split(":")
                    self.most_recent_tier = tier[1].replace(" ", "")
                    sql.AddCard(self.card_id, self.most_recent_card_name, tier[1], datetime.datetime.utcnow(), embed['image']['url'])
                    if int(tier[1]) > 4:
                        await self.MentionRoles(message, self.most_recent_card_name, tier[1])

                if f"got the card! `{self.most_recent_card_name[:-1]}`" in embed["description"]:
                    version = embed['description'].split(":")
                    ver = version[3].split(".")
                    v = ver[0].replace("`", "")
                    numbers = re.findall(r'[0-9]+', embed['description'])

                    if self.event["Started"]:
                        sql.CardClaimed(self.card_id, numbers[1], v, datetime.datetime.utcnow(), True)
                    else:
                        sql.CardClaimed(self.card_id, numbers[1], v, datetime.datetime.utcnow())

                    user = await self.bot.fetch_user(numbers[1])

                    if not sql.accountExists(user.id):
                        return await user.send(embed=func.ErrorEmbed(f"Hey! You claimed a card but dont have a sCoin account? What are you doing!? Join now by typing h.sCoin in MAL."))

                    useracc = sql.getAccount(user.id)
                    amount = 0.02 * float(self.most_recent_tier)
                    sql.setCoins(user.id, float(useracc[2]) + amount)

                    sql.sLog(message.author.id, 3, f"Added {amount} to {message.author.name}s eCoin balance", datetime.datetime.utcnow())
                    await message.channel.send(embed=func.Embed(f"{user.mention} Gained {amount} sCoin for claiming {self.most_recent_card_name}: Tier {self.most_recent_tier}!"))

            except Exception as e:
                print(e)

        # ----------------------------------------------

    @commands.group(invoke_without_command=True)
    async def card(self, ctx):
        await ctx.send(embed=func.Embed(f"`{ctx.prefix}card stats @user` - Get a users cards stats\n`{ctx.prefix}card history` - View card history"))

    @card.group(invoke_without_command=True)
    async def stats(self, ctx, user: discord.User=None):
        if not user:
            return

        Stats = [sql.TotalCardCount(user.id), sql.LastClaimedCard(user.id), sql.RarestCard(user.id)]

        if Stats:
            embed = discord.Embed(colour=0xcf53ee)
            embed.set_author(name=f"{user.name} - Card Stats", icon_url=user.avatar_url)
            embed.add_field(name="Total Cards", value=Stats[0], inline=True)
            embed.add_field(name="Last Claimed", value=Stats[1], inline=True)
            embed.add_field(name="Rarest Card", value=Stats[2], inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("That user has not claimed any cards!")

    @card.group(invoke_without_command=True)
    async def history(self, ctx):
        sorted_cards = []

        cards = sql.CardsHistory()

        i = 0
        for row in cards:
            i += 1
            if row[1] == 0:
                sorted_cards.append(f"{row[0]}- Tier {row[2]} is __unclaimed__")
                if i == 20:
                    last_time = row[3]
            if row[1] == 1:
                sorted_cards.append(f"{row[0]}- Tier {row[2]} is __claimed__")
                if i == 20:
                    last_time = row[3]

        embed = discord.Embed(
            description="\n".join(sorted_cards),
            colour=0xcf53ee,
        )
        embed.set_footer(text=f"Last Card Sent: {last_time}")

        await ctx.send(embed=embed)

    async def MentionRoles(self, message, name, tier):
        self.roles = self.ReloadJSON()

        if int(tier) == 5:
            channel = self.bot.get_channel(self.network_chat_id)
            role = discord.utils.get(message.guild.roles, id=self.roles["Tier5"])
            await channel.send(f"{role.mention} {name}- Tier 5 has spawned!")

        if int(tier) == 6:
            channel = self.bot.get_channel(self.network_chat_id)
            role = discord.utils.get(message.guild.roles, id=self.roles["Tier6"])
            await channel.send(f"{role.mention} {name}- Tier 6 has spawned!")

    @commands.command()
    async def mentions(self, ctx, tier:int=None, role:int=None):
        if not role or not tier:
            await ctx.send(embed=func.Embed(f"Use the command like this:\n\n{ctx.prefix}mentions [5 / 6] [roleid]"))

        if tier < 5:
            return

        check = discord.utils.get(ctx.guild.roles, id=role)

        if not check:
            return await ctx.send(embed=func.ErrorEmbed("I couldnt find that role"))

        self.roles[f"Tier{tier}"] = role
        with open("./modules/data/cards/MentionRoles.json", "w") as f:
            json.dump(self.roles, f)

            await ctx.send("Updated")

    # Event --------------------------------------------------------

    @tasks.loop(seconds=5)
    async def update(self):

        if not self.event_message or not self.event["Started"]:
            return

        try:
            if self.event["Remaining"] < 0:
                endembed = await self.leaderboardsMessage(True)
                await self.leaderboard_message.edit(embed=endembed)
                self.ResetEvent()

            embed = await self.EventMessage()
            self.event["Remaining"] -= 5
            await self.event_message.edit(embed=embed)

            embed1 = await self.leaderboardsMessage()
            await self.leaderboard_message.edit(embed=embed1)
        except Exception as e:
            print(e)

    @commands.group()
    async def shoob(self, ctx, event = None, duration = None, *args):

        if not await sql.isStaff(ctx.author):
            return await ctx.send(embed=func.NoPerm())

        if not event or not duration or not args:
            return await ctx.send(embed=func.Embed(f"If you want to start an event use the command like this:\n\n{ctx.prefix}shoob event [duration] [card]\n\nDurations: m, h, d, w"))

        self.event["Reward"] = ' '.join(args)
        self.event["TotalDuration"] = self.timeformat(duration)
        self.event["Remaining"] = self.event["TotalDuration"]
        self.channel = ctx.channel

        embed = await self.EventMessage()
        self.event_message = await ctx.send(embed=embed)
        self.event["Started"] = True

        embed = await self.leaderboardsMessage()
        self.leaderboard_message = await ctx.send(embed=embed)

    @shoob.group()
    async def cancel(self, ctx):
        if not await sql.isStaff(ctx.author):
            return ctx.send(embed=func.NoPerm())

    async def leaderboardsMessage(self, end=False):

        rows = sql.GetLeaderboard()
        rows_sorted = []
        i = 1

        if rows and not end:
            for card in rows:
                user = await self.bot.fetch_user(card[1])
                rows_sorted.append(f"👤 {i}. {user.mention} <a:mal_AS:658788811333042187> {card[2]}")
                i += 1

            desc = "\n".join(rows_sorted)

        if end:
            self.event["Started"] = False
            for card in rows:
                if i == 1:
                    user = await self.bot.fetch_user(card[1])
                    rows_sorted.append(f"Congratulations {user.mention}, you've won {self.event['Reward']}")
                    rows_sorted.append("")
                    rows_sorted.append(f"🏆 {user.mention} <a:mal_AS:658788811333042187> {card[2]}")
                if i == 2 or i == 3:
                    user = await self.bot.fetch_user(card[1])
                    rows_sorted.append(f"🏅 {user.mention} <a:mal_AS:658788811333042187> {card[2]}")

                i += 1

            desc = "\n".join(rows_sorted)

        if not rows:
            desc = "No cards have been claimed yet."

        embed = discord.Embed(
            description=desc,
            colour=0xcf53ee
        )

        rows_sorted.clear()
        return embed

    def ResetEvent(self):
        self.event = {"Started": False, "TotalDuration": None, "Remaining": None, "Reward": None}
        self.event_message = None
        self.leaderboard_message = None
        self.channel = None

    async def EventMessage(self):

        Duration = str(datetime.timedelta(seconds=int(self.event["TotalDuration"])))

        embed = discord.Embed(
            description=f"Ok! Starting an event with a duration of {Duration} with a reward of **{self.event['Reward']}**.",
            colour=0xcf53ee,
        )
        embed.set_footer(text="Duration Remaining: {}".format(str(datetime.timedelta(seconds=int(self.event["Remaining"])))))

        return embed

    def timeformat(self, st): # Get Seconds

        available_times = ['m', 'h', 'd', 'w']
        multiplier = [60, 3600, 86400, 604800]
        time = ''

        try:
            for i in st:
                try:
                    time += str(int(i))
                except:
                    if i in available_times:
                        time += i
                        break
        except:
            return False

        if time == '':
            return False

        for i, v in enumerate(available_times):
            if v in time:
                return int(time[:-1]) * multiplier[i]

        try:
            return int(time)
        except:
            pass

        return False

def setup(bot):
    bot.add_cog(Cards(bot))