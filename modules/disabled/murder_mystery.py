import discord
import random
import asyncio


from discord.ext import commands, tasks

class MurderMystery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.armory = {
            "Weapons": {
                1: {"Name": "RPG-7",
                    "Damage": 100,
                    "Accuracy": 100,
                    "Ammunition": 1,
                    "AmmoType": "Rocket"
                },
                2: {"Name": "Explosive Suitcase",
                    "Damage": 300,
                    "Accuracy": 50,
                    "Ammunition": 1,
                    "AmmoType": "Plastic Explosive"
                },
                3: {"Name": "AK-47",
                    "Damage": 100,
                    "Accuracy": 100,
                    "Ammunition": 1,
                    "AmmoType": "Rifle Bullet"
                },
                4: {"Name": "Glock 19",
                    "Damage": 100,
                    "Accuracy": 100,
                    "Ammunition": 2,
                    "AmmoType": "Pistol Bullet"
                },
                5: {"Name": "Samurai Sword",
                    "Damage": 60,
                    "Accuracy": 30,
                    "Ammunition": 3,
                    "AmmoType": "Sharpening Steel"
                },
                6: {"Name": "Crossbow",
                    "Damage": 30,
                    "Accuracy": 20,
                    "Ammunition": 4,
                    "AmmoType": "Bolt"
                }
            },
            "Parts": {
                1: "Titanium", 2: "Gunpowder", 3: "Handle", 4: "Iron", 5: "Casting Iron"
            }
        }
        self.game = {
            "Active": False,
            "Playing": False,

            "Timer": 300,
            "IconURL": None,

            "Players": {},
        }

        self.playermodel = {"PlayerID": 0,
                            "Username": None,
                            "TheirTurn": False,

                            "Weapon": {
                               "Parts": [],
                               "Equipped": "Unarmed",
                               "UsesRemaining": 0
                                },

                            "Stats": {
                               "PlayerTurn": 0,
                               "TotalUses": 0,
                               "TotalTurns": 0,

                               "Kills": 0,
                               "SearchAttempts": 0
                                }
                            }
        self.gamemodel = {
                        "Active": False,
                        "Playing": False,
                        "Channel": None,

                        "Timer": 300,
                        "Murderer": None,
                        "IconURL": None,

                        "Players": {},
                         }

        self.creator = None
        self.murderer = None
        self.startingembed = None
        self.updateTimer.start()

    @tasks.loop(seconds=5)
    async def updateTimer(self):

        if self.game["Active"]:
            if not self.game["Playing"]:

                if self.game["Timer"] <= 0:
                    return await self.ResetGame()

                self.game["Timer"] -= 5

                e = await self.StartingEmbed()

                await self.startingembed.edit(embed = e)

    @commands.group(aliases=["mm"], invoke_without_command=True)
    @commands.guild_only()
    async def murdermystery(self, ctx):

        description = f"""
        `{ctx.prefix}mm start` - Starts a new game
        `{ctx.prefix}mm join` - Joins the current game
        `{ctx.prefix}mm leave` - Leaves the current game

        `{ctx.prefix}mm help` - Game help

        **Ingame**
        `{ctx.prefix}mm search` - Search for parts or ammo
        `{ctx.prefix}mm craft` - Craft a weapon when you have enough parts
        `{ctx.prefix}mm loadout` - Shows your equipment

        """

        embed = discord.Embed(
            title="Commands",
            colour=0x43c8e6,
            description=description
            )

        embed.set_author(name="MAL Murder Mysteries", icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed)

    @murdermystery.group(invoke_without_command=True)
    @commands.guild_only()
    async def start(self, ctx):
        if not self.game["Active"]:

            await self.ResetGame()

            self.game["Active"] = True
            self.creator = ctx.author
            self.game["IconURL"] = ctx.guild.icon_url
            self.game["Channel"] = ctx.channel.id

            await self.JoinGame(ctx.author, ctx)

    @murdermystery.group(name="join", invoke_without_command=True)
    @commands.guild_only()
    async def join_(self, ctx):

        if self.game["Active"]:
            await self.JoinGame(ctx.author)

    # Starting Mechanics

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if not self.startingembed or user.bot or reaction.message.id != self.startingembed.id:
            return

        if str(reaction.emoji) == "<a:malAR:634796125999595520>":

            await reaction.remove(user)

            if user.id not in self.game["Players"]:
                await self.JoinGame(user)

            if len(self.game["Players"]) >= 2:
                await self.startingembed.add_reaction("👍")

        elif str(reaction.emoji) == "👍":
            if user.id == self.creator.id:
                await self.StartGame()
            else:
                await reaction.remove(user)

    async def JoinGame(self, user, creator=None):

        self.game["Players"][user.id] = self.playermodel.copy()

        PlayerID = len(self.game["Players"])

        self.game["Players"][user.id]["PlayerID"] = PlayerID
        self.game["Players"][user.id]["Username"] = user.name

        if creator:
            embed = await self.StartingEmbed()
            self.startingembed = await creator.channel.send(embed=embed)
            try:
                return await self.startingembed.add_reaction("<a:malAR:634796125999595520>")
            except:
                return

        embed = await self.StartingEmbed()

        await self.startingembed.edit(embed=embed)

    async def StartGame(self):

        self.game["Active"] = True
        self.game["Playing"] = True

        murdererID = random.randint(1, int(len(self.game["Players"])))

        for i in self.game["Players"]:
            print(self.game["Players"][i]["PlayerID"])
            if self.game["Players"][i]["PlayerID"] == murdererID:
                self.murderer = await self.bot.fetch_user(i)

        await self.murderer.send("You are the murderer. Try and kill everyone before they kill you!")

        del self.game["Players"][self.murderer.id]

        for player in self.game["Players"]:

            user = await self.bot.fetch_user(player)

            try:
                await user.send("You're Innocent, start finding weapons to stop the executioner before its too late")
            except:
                pass

        try:
            await self.startingembed.delete()
        except:
            pass

        first = next(iter(self.game["Players"]))

        user = await self.bot.fetch_user(first)

        await user.send(embed=self.GoodEmbed("Its your turn!"))
        channel = await self.bot.fetch_channel(self.game["Channel"])
        await channel.send(embed=self.GoodEmbed(f"It is now {user.mention}'s turn!"))
        self.game["Players"][first]["TheirTurn"] = True

    async def StartingEmbed(self):

        if len(self.game["Players"]) >= 5:
            desc = f"""**A match has been started by {self.creator.name}**
            One of you is a murderer, and the rest are innocent. Find the murderer, and execute them before its too late.

            React 👍 to start, {self.creator.name}!
            """
        else:

            desc = f"""**A match has been started by {self.creator.name}**
            One of you is a murderer, and the rest are innocent. Find the murderer, and execute them before its too late.

            React to join!
            """

        players = ""
        for i in self.game["Players"]:

            player = await self.bot.fetch_user(i)

            players += f"\n{player.name}"

        embed = discord.Embed(
            colour=0x42bd40,
            description=desc)
        embed.set_author(name="MAL Murder Mysteries", icon_url=self.game["IconURL"])

        if self.game["Active"]:
            embed.set_footer(text=f"Match Expires in: {self.game['Timer']}")

        embed.add_field(name="Players", value=players, inline=False)

        return embed

    # ---

    @murdermystery.group(invoke_without_command=True)
    @commands.guild_only()
    async def leave(self, ctx):
        if not self.game["Active"]:

            if ctx.author.id not in self.game["Players"]:
                return

            del self.game["Players"][ctx.author.id]

            embed = await self.StartingEmbed()
            await self.startingembed.edit(embed=embed)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.guild_only()
    async def search(self, ctx):

        # If the game is active, and the author is in the game
        if not self.game["Playing"] and not self.game["Active"] and not self.game["Players"][ctx.author.id]:
            return

        if not self.game["Players"][ctx.author.id]["TheirTurn"]:
            return await ctx.author.send(embed=self.BadEmbed("It is not your turn"))

        # If player has a weapon, search for ammo instead
        if self.game["Players"][ctx.author.id]["Weapon"]["Equipped"] != "Unarmed":
            findings = await self.SearchForAmmo(ctx.author)
            if findings:
                return await ctx.author.send(self.GoodEmbed(f"You found: || {findings} ||"))
            else:
                return await ctx.author.send(embed=self.BadEmbed("Unlucky! You didnt find anything this time."))

        # If they have enough parts to craft a weapon
        if len(self.game["Players"][ctx.author.id]["Weapon"]["Parts"]) == 5:
            return await ctx.author.send(embed=self.GoodEmbed("You have enough parts to craft a weapon!"))

        part = await self.SearchForParts(ctx.author)

        if part:
            await ctx.author.send(f"Lucky! You found a {part}")
        else:
            await ctx.author.send(embed=self.BadEmbed("Unlucky! You couldnt find a weapon part this time."))

        await self.TurnsEngine(ctx.author)

    # Searching Mechanics

    async def SearchForParts(self, user):

        chances = random.randint(0, 1)

        if chances == 1:

            part = random.randint(0, 4)

            if part in self.game["Players"][user.id]["Weapon"]["Parts"]:
                await self.SearchForParts(user)

            if not part or not self.armory["Parts"][part]:
                await self.SearchForParts(user)

            if part not in self.game["Players"][user.id]["Weapon"]["Parts"]:
                self.game["Players"][user.id]["Weapon"]["Parts"].append(part)

                return self.armory["Parts"][part]

    async def SearchForAmmo(self, user):

        part = random.randint(1, 100)

        if part > 80:

            UserWeapon = self.game["Players"]["Weapon"]["Equipped"]

            return self.armory["Weapons"][UserWeapon]["AmmoType"]

    # ---

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def craft(self, ctx):

        if not self.game["Playing"] and self.game["Active"] and not self.game["Players"][ctx.author.id]:
            return

        if not self.game["Players"][ctx.author.id]["TheirTurn"]:
            return await ctx.author.send(embed=self.BadEmbed("It is not your turn"))

        if len(self.game["Players"][ctx.author.id]["Weapon"]["Parts"]) < 4:
            return await ctx.author.send(embed=self.BadEmbed("You dont have enough parts. Try searching for more!"))

        await ctx.author.send(embed=self.GoodEmbed("Your weapon is being prepared. Eta: 1 minute"))

        weapon = await self.CraftWeapon(ctx.author)

        await asyncio.sleep(5) # CHANGE THIS TO 60

        await ctx.author.send(embed=self.GoodEmbed(f"Your weapon is done crafting!\n\nYou crafted: || {weapon} ||"))

        await self.TurnsEngine(ctx.author)

    # Crafting Mechanics

    async def CraftWeapon(self, user):
        Weapons = ["RPG-7", "Explosive Suitcase", "AK-47", "Glock", "Samurai Sword", "Bow and Arrow"]

        chances = random.randint(0, 100)

        self.game["Players"][user.id]["Weapon"]["Parts"].clear()

        if chances >= 0 and chances <= 1:
            Weapon = 1

        if chances >= 2 and chances <= 6:
            Weapon = 2

        if chances >= 7 and chances <= 21:
            Weapon = 3

        if chances >= 22 and chances <= 41:
            Weapon = 4

        if chances >= 42 and chances <= 65:
            Weapon = 5

        if chances >= 66 and chances <= 100:
            Weapon = 6

        self.game["Players"][user.id]["Weapon"] = self.armory["Weapons"][Weapon]

        return Weapons[Weapon]

    # ---

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.author.send("You are still on cooldown! Try again soon")

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.author.send("Go to the channel, dumb fuck")

        else:
            raise error

    # Other Game Mechanics

    async def ResetGame(self):

        try:
            await self.startingembed.delete()
        except:
            pass

        self.game = self.gamemodel.copy()

    def BadEmbed(self, description):

        embed = discord.Embed(
            title="Oof",
            colour=0xff4f4f,
            description=description
        )

        embed.set_author(name="MAL Murder Mysteries", icon_url=self.game["IconURL"])

        return embed

    def GoodEmbed(self, description):

        embed = discord.Embed(
            title="Alright.",
            colour=0x43c8e6,
            description=description
        )

        embed.set_author(name="MAL Murder Mysteries", icon_url=self.game["IconURL"])

        return embed

    async def TurnsEngine(self, user):

        PrevPlayerID = self.game["Players"][user.id]["PlayerID"]
        self.game["Players"][user.id]["TheirTurn"] = False
        await user.send(embed=self.GoodEmbed("Your turn has ended"))


        # Need to check if PlayerID is the last player, if it is wrap back to the first


        for i in self.game["Players"]:
            if self.game["Players"][i]["PlayerID"] == PrevPlayerID:
                self.game["Players"][i]["TheirTurn"] = True

                channel = await self.bot.fetch_channel(self.game["Channel"])
                newPlayer = await self.bot.fetch_user(i)

                await channel.send(embed=self.GoodEmbed(f"It is now {newPlayer.mention}'s turn!"))

                await newPlayer.send(embed=self.GoodEmbed("Its your turn!"))

    # ---

    # For each 3 moves of players, the murderer gets 1

def setup(bot):
    bot.add_cog(MurderMystery(bot))