import discord
from discord.ext import commands, tasks
import aiohttp

import asyncio
import datetime

class AnimeForm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.completed_role_id = 662039067789099008 # Weird plant role
        self.completed_role = None

        self.favorites_channel_id = 694030910936317982 #Favorites
        self.favorites_channel = None

        self.form_entry_channel_id = 622906588562456576 # This is #general (bots)
        self.form_entry_channel = None

        self.users = {}

        self.timeout = 600

        self.question_no = 0

        self.emotes = {
        'YES': "<:malYES:657275749249712195>",
        'NO': "<:malNO:657275797228486682>",
        9: "<a:9_mal:658785549540392960>",
        8: "<a:8_mal:658785573598920741>",
        7: "<a:7_mal:658785597804249117>",
        6: "<a:6_mal:658785616120643604>",
        5: "<a:5_mal:658785634479243315>",
        4: "<a:4_mal:658785651881410573>",
        3: "<a:3_mal:658785706201579570>",
        2: "<a:2_mal:658785722265894932>",
        1: "<a:1_mal:658785745804328980>",
        0: "<a:0_mal:658785774258487299>",
        'SKIP': '⛔'
        }


    @commands.Cog.listener()
    async def on_message(self, message):

        try:
            self.form_entry_channel = self.bot.get_channel(self.form_entry_channel_id)
            self.favorites_channel = self.bot.get_channel(self.favorites_channel_id)
            self.completed_role = discord.utils.get(message.guild.roles, id=self.completed_role_id)
        except Exception as e:
            return

        if self.form_entry_channel is None:
            print("[AnimeForm] Entry Channel missing. Unloading")
            self.bot.unload_extension(f"modules.cogs.anime_form")
            return

        if self.favorites_channel is None:
            print("[AnimeForm] Favourites Channel missing. Unloading")
            self.bot.unload_extension(f"modules.cogs.anime_form")
            return

        if message.author.bot or message.author.id in self.users:
            return

        if not message.content.lower() == "h^animanga":
            return
        
        if self.completed_role in message.author.roles:
            await message.author.send("You have already completed the Animanga Survey!")
            return

        if self.users:
            await message.author.send("You will need to wait. Only 1 user can take the survey at a time due to discord limitations.")
            return

        if message.channel.id != self.form_entry_channel_id:
            await self.form_entry_channel.send(f"{message.author.mention}")
            return

        await message.delete()

        try:
            colour = await self.Colour()
        except Exception:
            try:
                colour = await self.Colour()
            except Exception:
                await ctx.send("Unexpected Error Occurred. Please retry")
                return

        self.users[message.author.id] = {"Colour": colour, "Question": 0, "Roles": [], "Anime_Q": {}, "Manga": {}, "LightNovel": {}, "Animanga": {}, "Characters": {}}

        self.Question = self.users[message.author.id]["Question"]
        self.Roles = self.users[message.author.id]["Roles"]
        self.Anime_Q = self.users[message.author.id]["Anime_Q"]
        self.Manga = self.users[message.author.id]["Manga"]
        self.LightNovel = self.users[message.author.id]["LightNovel"]
        self.Animanga = self.users[message.author.id]["Animanga"]
        self.Characters = self.users[message.author.id]["Characters"]

        responses = {self.emotes['YES'], self.emotes['NO']}

        start_msg = f"""Hello, {message.author.mention} would you like to take our Animanga survey?

                    Survey Details:
                    You may type `skip` on question after question 2, or press ⛔
                    There is a 200 word limit to written questions.
                    Do not take longer than 10 minutes per response."""

        start_response = await self.request_emote(message.author, start_msg, "", responses)

        if start_response != self.emotes['YES']:
            del self.users[message.author.id]
            return await self.form_entry_channel.send('Ok, thank you.', delete_after=15)

        page = 0
        total_pages = 0
        templist = []

        # ------------------------- Anime

        await self.Anime_Qs(message)

        if self.Anime_Q:
            total_pages += 1
            for k,v in self.Anime_Q.items():
                text = f"<a:malARL:629155002505756672> {k} <a:malStar1:614619624268365829> **{v}**\n"
                templist.append(text)

            anime_description = f"""<a:malHeartDose:613541345021263881> <a:mal_AA:667431391918555174> <a:mal_NN:667432127893209098> <a:mal_II:667431773659201578> <a:mal_MM:667432082603114497> <a:mal_EE:667431579530035200> <a:malHeartDose:613541345021263881>

                                {"".join(templist)}"""
            templist.clear()

        # ------------------------- Manga

        await self.Manga_Qs(message)

        if self.Manga:
            total_pages += 1
            for k,v in self.Manga.items():
                text = f"<a:malARL:629155002505756672> {k} <a:malStar1:614619624268365829> **{v}**\n"
                templist.append(text)

            manga_description = f"""<a:malHeartDose:613541345021263881> <a:mal_MM:667432082603114497> <a:mal_AA:667431391918555174> <a:mal_NN:667432127893209098> <a:mal_GG:667431704868290578> <a:mal_AA:667431391918555174>  <a:malHeartDose:613541345021263881>

                                {"".join(templist)}"""
            templist.clear()

        # ------------------------- LightNovel

        await self.LightNovel_Qs(message)

        if self.LightNovel:
            total_pages += 1
            for k,v in self.LightNovel.items():
                text = f"<a:malARL:629155002505756672> {k} <a:malStar1:614619624268365829> **{v}**\n"
                templist.append(text)

            light_description = f"""<a:malHeartDose:613541345021263881> <a:mal_LL:667432051896483842> <a:mal_II:667431773659201578> <a:mal_GG:667431704868290578> <a:mal_HH:667431741736353803> <a:mal_TT:667432620149440523> <a:mal_NN:667432127893209098> <a:mal_OO:667432275314606117> <a:mal_VV:667432907983421445> <a:mal_EE:667431579530035200> <a:mal_LL:667432051896483842> <a:malHeartDose:613541345021263881>

                                {"".join(templist)}"""
            templist.clear()

        # ------------------------- Animanga

        await self.Animanga_Qs(message)

        if self.Animanga:
            total_pages += 1
            for k,v in self.Animanga.items():
                text = f"<a:malARL:629155002505756672> {k} <a:malStar1:614619624268365829> **{v}**\n"
                templist.append(text)

            animanga_description = f"""<a:malHeartDose:613541345021263881><a:mal_AA:667431391918555174><a:mal_NN:667432127893209098><a:mal_II:667431773659201578><a:mal_MM:667432082603114497>  <a:mal_MM:667432082603114497> <a:mal_AA:667431391918555174> <a:mal_NN:667432127893209098> <a:mal_GG:667431704868290578> <a:mal_AA:667431391918555174>  <a:malHeartDose:613541345021263881>

                                {"".join(templist)}"""
            templist.clear()

        # ------------------------- Characters

        await self.Characters_Qs(message)

        if self.Characters:
            total_pages += 1
            for k,v in self.Characters.items():
                text = f"<a:malARL:629155002505756672> {k} <a:malStar1:614619624268365829> **{v}**\n"
                templist.append(text)

            characters_description = f"""<a:malHeartDose:613541345021263881> <a:mal_CC:667431463024590894> <a:mal_HH:667431741736353803> <a:mal_AA:667431391918555174> <a:mal_RR:667432427865505809> <a:mal_AA:667431391918555174> <a:mal_CC:667431463024590894> <a:mal_TT:667432620149440523> <a:mal_EE:667431579530035200> <a:mal_RR:667432427865505809> <a:mal_SS:667432471352180736>  <a:malHeartDose:613541345021263881>

                                {"".join(templist)}"""
            templist.clear()

        # ------------------------- Send Embeds

        link = await self.request_message(message.author, "Do you have a MyAnimeList profile?\nIf you do, send the link to your MyAnimeList profile.\n\nE.G [Link](https://myanimelist.net/profile/-NeW-)", "")

        if link:
            if not "https://myanimelist.net/profile/" in link.lower():
                link = ""

        if link:
            title = "My Anime List Profile"
        else:
            title = ""

        await self.favorites_channel.send(message.author.mention)

        if self.Anime_Q:
            page += 1
            Anime_QE = discord.Embed(title = title, description = anime_description, colour=self.users[message.author.id]["Colour"], url=link)
            Anime_QE.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            Anime_QE.set_footer(text=f"Page {page} / {total_pages}")

            await self.favorites_channel.send(embed=Anime_QE)

        if self.Manga:
            page += 1
            mangaE = discord.Embed(description = manga_description, colour=self.users[message.author.id]["Colour"])
            mangaE.set_footer(text=f"Page {page} / {total_pages}")

            await self.favorites_channel.send(embed=mangaE)

        if self.LightNovel:
            page += 1
            lightnovelE = discord.Embed(description = light_description, colour=self.users[message.author.id]["Colour"])
            lightnovelE.set_footer(text=f"Page {page} / {total_pages}")

            await self.favorites_channel.send(embed=lightnovelE)

        if self.Animanga:
            page += 1
            animangaE = discord.Embed(description = animanga_description, colour=self.users[message.author.id]["Colour"])
            animangaE.set_footer(text=f"Page {page} / {total_pages}")

            await self.favorites_channel.send(embed=animangaE)

        if self.Characters:
            page += 1
            charactersE = discord.Embed(description = characters_description, colour=self.users[message.author.id]["Colour"])
            charactersE.set_footer(text=f"Page {page} / {total_pages}")

            await self.favorites_channel.send(embed=charactersE)

        for role in self.Roles:
            if role:
                roletoadd = discord.utils.get(message.guild.roles, id=role)
                await message.author.add_roles(roletoadd)

        await message.author.add_roles(self.completed_role)
        self.users = {}

        done = discord.Embed(title=f"{message.author.name} Just completed their Animanga Survey!", description = "Send `h^animanga` in <#622906588562456576> to start!", colour=0xa9a9a9)

        await self.form_entry_channel.send(embed=done)


    # Questions

    async def Anime_Qs(self, message):

        # ------------- Q1

        anime_res_1 = {
            self.emotes[1]: ( 'More than 5', 661860188931751961 ),
            self.emotes[2]: ( 'More than 25', 661860189569417216 ),
            self.emotes[3]: ( 'More than 50', 661860192119554048 ),
            self.emotes[4]: ( 'More than 100', 662018064036003840 ),
            self.emotes[5]: ( 'More than 250', 662018064707223582 ),
            self.emotes[6]: ( 'More than 500', 662018066489540609 )
        }

        anime_desc_1 = f"""
                        How much anime have you watched?
                        {self.emotes[1]}: More than 5
                        {self.emotes[2]}: More than 20
                        {self.emotes[3]}: More than 50
                        {self.emotes[4]}: More than 100
                        {self.emotes[5]}: More than 250
                        {self.emotes[6]}: More than 500
                        """

        anime_ans_1 = await self.request_emote(message.author, anime_desc_1, "", anime_res_1)

        if anime_ans_1 in anime_res_1:
            response, role_id = anime_res_1[anime_ans_1]
            self.Anime_Q['Anime Watched'] = response
            if role_id:
                self.Roles.append(role_id)
        else:
            del self.users[message.author.id]
            return

        # ------------- Q2

        anime_ans_2 = await self.request_message(message.author, "List upto 5 titles of your favorite anime.", "Please seperate your titles with ,")

        if anime_ans_2:
            anime_ans_2 = anime_ans_2.replace(",", " <a:malCstars:608135899565522963> ")

            self.Anime_Q['Favorite Anime'] = anime_ans_2


        # ------------- Q3

        anime_res_3 = {
            self.emotes[1]: ( 'Subbed', 674757863733985320 ),
            self.emotes[2]: ( 'Dubbed', 674757861871452170 ),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        anime_desc_3 = f"""Do you prefer to watch Anime Subbed or Dubbed?
                                                {self.emotes[1]}: Subbed
                                                {self.emotes[2]}: Dubbed"""

        anime_ans_3 = await self.request_emote(message.author, anime_desc_3, "", anime_res_3)

        if anime_ans_3 in anime_res_3:
            response, role_id = anime_res_3[anime_ans_3]
            if response != 'Skipped':
                self.Anime_Q['Sub / Dub'] = response
            if role_id is not None:
                self.Roles.append(role_id)

        # ------------- Q4

        anime_res_4 = {
            self.emotes[1]: ( 'New Generation Anime', 662018072911020078 ),
            self.emotes[2]: ( 'Old Generation Anime', 662018073028722748 ),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        anime_desc_4 = f"""Favorite Generation
                        {self.emotes[1]}: New Generation Anime
                        {self.emotes[2]}: Old Generation Anime"""

        anime_ans_4 = await self.request_emote(message.author, anime_desc_4, "", anime_res_4)

        if anime_ans_4 in anime_res_4:
            response, role_id = anime_res_4[anime_ans_4]
            if response != 'Skipped':
                self.Anime_Q['Favorite Generation'] = response
            if role_id is not None:
                self.Roles.append(role_id)

        # ------------- Q5

        anime_ans_5 = await self.request_message(message.author, "What Anime World do you wish to live in?", "You may type `skip`")

        if anime_ans_5:
            self.Anime_Q['Favorite World'] = anime_ans_5

        # ------------- Q6

        anime_ans_6 = await self.request_message(message.author, "What's your favorite Anime Studio?", "You may type `skip`")

        if anime_ans_6:
            self.Anime_Q['Favorite Studio'] = anime_ans_6

        # ------------- Q7

        anime_ans_7 = await self.request_message(message.author, "Write the title of an anime that you think is __overrated.__", "You may type `skip`")

        if anime_ans_7:
            self.Anime_Q['Overrated Anime'] = anime_ans_7

        # ------------- Q8

        anime_ans_8 = await self.request_message(message.author, "Write the title of an anime that you think is __underrated.__", "You may type `skip`")

        if anime_ans_8:
            self.Anime_Q['Underrated Anime'] = anime_ans_8

        # ------------- Q9

        anime_ans_9 = await self.request_message(message.author, "Which Anime __Opening__ theme is your favorite?", "You may type `skip`")

        if anime_ans_9:
            self.Anime_Q['Favorite Anime Opening'] = anime_ans_9

        # ------------- Q10

        anime_ans_10 = await self.request_message(message.author, "Which Anime __Ending__ theme is your favorite?", "You may type `skip`")

        if anime_ans_10:
            self.Anime_Q['Favorite Anime Ending'] = anime_ans_10 # 10 Questions

    async def Manga_Qs(self, message):

        # ------------- Q1

        manga_res_1 = {
            self.emotes[1]: ( 'More than 5', 662018066611306548 ),
            self.emotes[2]: ( 'More than 25', 662018067978649610 ),
            self.emotes[3]: ( 'More than 50', 662018068012072976 ),
            self.emotes[4]: ( 'More than 100', 662018069052260414 ),
            self.emotes[5]: ( 'More than 250', 662018070591701055 ),
            self.emotes[6]: ( 'More than 500', 662018070675718144 ),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        manga_desc_1 = f"""How Much Manga Have you Read?
                        {self.emotes[1]}: More than 5
                        {self.emotes[2]}: More than 25
                        {self.emotes[3]}: More than 50
                        {self.emotes[4]}: More than 100
                        {self.emotes[5]}: More than 250
                        {self.emotes[6]}: More than 500
                        """

        manga_ans_1 = await self.request_emote(message.author, manga_desc_1, "", manga_res_1)

        if manga_ans_1 in manga_res_1:
            response, role_id = manga_res_1[manga_ans_1]
            if response != 'Skipped':
                self.Manga['Manga Read'] = response
            if role_id is not None:
                self.Roles.append(role_id)


        # ------------- Q2

        manga_ans_2 = await self.request_message(message.author, "List up to five titles of your favorite Manga!", "Please seperate your titles with ,")

        if manga_ans_2:
            manga_ans_2 = manga_ans_2.replace(",", " <a:malCstars:608135899565522963> ")

            self.Manga['Favorite Manga'] = manga_ans_2

        # ------------- Q3

        manga_res_3 = {
            self.emotes[1]: ( 'Japanese Manga', None ),
            self.emotes[2]: ( 'Korean Manhwa', None ),
            self.emotes[3]: ( 'Chinese Manhua', None ),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        manga_desc_3 = f"""Which Manga type do you prefer?
                        {self.emotes[1]}: Japanese Manga
                        {self.emotes[2]}: Korean Manhwa
                        {self.emotes[3]}: Chinese Manhua
                        """

        manga_ans_3 = await self.request_emote(message.author, manga_desc_3, "", manga_res_3)
        if manga_ans_3 in manga_res_3:
            response, role_id = manga_res_3[manga_ans_3]
            if response != 'Skipped':
                self.Manga['Manga Preferred'] = response
            if role_id is not None:
                self.Roles.append(role_id)

        # ------------- Q4

        manga_ans_4 = await self.request_message(message.author, "What's the weirdest Manga you've read?", "You may type `skip`")

        if manga_ans_4:
            self.Manga['Weirdest Manga'] = manga_ans_4

        # ------------- Q5

        manga_ans_5 = await self.request_message(message.author, "Write the title of a manga that you think is __Overrated__.", "You may type `skip`")

        if manga_ans_5:
            self.Manga['Overrated Manga'] = manga_ans_5

        # ------------- Q6

        manga_ans_6 = await self.request_message(message.author, "Write the title of a manga that you think is __Underrated__.", "You may type `skip`")

        if manga_ans_6:
            self.Manga['Underrated Manga'] = manga_ans_6 # 6 Questions

    async def LightNovel_Qs(self, message):

        # ------------- Q1

        light_res_1 = {
            self.emotes[1]: ( 'More than 2', None ),
            self.emotes[2]: ( 'More than 5', None ),
            self.emotes[3]: ( 'More than 10', None ),
            self.emotes[4]: ( 'More than 15', None ),
            self.emotes[5]: ( 'More than 25', None ),
            self.emotes[6]: ( 'More than 40', None ),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        light_desc_1 = f"""How Many Light Novels Have you Read?
                        {self.emotes[1]}: More than 2
                        {self.emotes[2]}: More than 5
                        {self.emotes[3]}: More than 10
                        {self.emotes[4]}: More than 15
                        {self.emotes[5]}: More than 25
                        {self.emotes[6]}: More than 40
                        """

        light_ans_1 = await self.request_emote(message.author, light_desc_1, "", light_res_1)

        if light_ans_1 in light_res_1:
            response, role_id = light_res_1[light_ans_1]
            if response != 'Skipped':
                self.LightNovel['LightNovel Read'] = response
            if role_id is not None:
                self.Roles.append(role_id)

        # ------------- Q2

        light_ans_2 = await self.request_message(message.author, "List up to three titles of your favorite Lightnovels!", "Please seperate your titles with ,")

        if light_ans_2:
            
            light_ans_2 = light_ans_2.replace(",", " <a:malCstars:608135899565522963> ")
            
            self.LightNovel['Favorite LightNovel'] = light_ans_2 # 2 Questions

    async def Animanga_Qs(self, message):

        # ------------- Q1

        animanga_res_1 = {
            self.emotes[1]: ( 'Action', 662039056728981514 ),
            self.emotes[2]: ( 'Drama', 662038700607143985 ),
            self.emotes[3]: ( 'Comedy', 662038701559513089 ),
            self.emotes[4]: ( 'Isekai', 662038702955954207 ),
            self.emotes[5]: ( 'Romance', 662038703295692859 ),
            self.emotes[6]: ( 'Harem', 662038703723642911 ),
            self.emotes[7]: ( 'Slice of Life', 662039057248944139 ),
            self.emotes[8]: ( 'Romance', 662039058423349253 ),
            self.emotes[9]: ( 'Harem', 662039058809356309 ),
            self.emotes[0]: ( 'Seinen', 662039059379519499),
            self.emotes['SKIP']: ( 'Skipped', None )
        }

        animanga_desc_1 = f"""What is your favorite Genre?
                            {self.emotes[1]}: Action
                            {self.emotes[2]}: Drama
                            {self.emotes[3]}: Comedy
                            {self.emotes[4]}: Isekai
                            {self.emotes[5]}: Romance
                            {self.emotes[6]}: Harem
                            {self.emotes[7]}: Slice of Life
                            {self.emotes[8]}: Romance
                            {self.emotes[9]}: Harem
                            {self.emotes[0]}: Seinen
                            """

        animanga_ans_1 = await self.request_emote(message.author, animanga_desc_1, "", animanga_res_1)

        if animanga_ans_1 in animanga_res_1:
            response, role_id = animanga_res_1[animanga_ans_1]
            if response != 'Skipped':
                self.Animanga['Favorite Genre'] = response
            if role_id is not None:
                self.Roles.append(role_id)

        # ------------- Q2


        animanga_ans_2 = await self.request_message(message.author, "What's your favorite Anime Movie?", "Please seperate your titles with ,")

        if animanga_ans_2:
            self.Animanga['Favorite Animanga Movie'] = animanga_ans_2

        # ------------- Q3

        animanga_ans_3 = await self.request_message(message.author, "What's your favorite Anime Episode?", "Examples: Re Zero Episode 15, Haikyuu S3 Episode 4")

        if animanga_ans_3:
            self.Animanga['Favorite Animanga Episode'] = animanga_ans_3

        # ------------- Q4

        animanga_ans_4 = await self.request_message(message.author, "What's your favorite Anime Season?", "Examples: Winter 2019, Spring 2011")

        if animanga_ans_4:
            self.Animanga['Favorite Anime Season'] = animanga_ans_4

        # ------------- Q5

        animanga_ans_5 = await self.request_message(message.author, "What's your favorite Manga Volume?", "Examples: Shingeki no Kyojin Volume 20, Slam Dunk Volume 31")

        if animanga_ans_5:
            self.Animanga['Favorite Manga Volume'] = animanga_ans_5

        # ------------- Q6

        animanga_ans_6 = await self.request_message(message.author, "When was the first time you watched your first anime on the internet?", "Format DD/MM/YY or MM/YY")

        if animanga_ans_6:
            self.Animanga['First time'] = animanga_ans_6 # 6 Questions

    async def Characters_Qs(self, message):

        # ------------- Q1

        char_ans_1 = await self.request_message(message.author, "Who's your favorite Male Protagonist?", "You may type `skip`")

        if char_ans_1:
            self.Characters['Favorite Male Protagonist'] = char_ans_1

        # ------------- Q2

        char_ans_2 = await self.request_message(message.author, "Who's your favorite Female Protagonist?", "You may type `skip`")

        if char_ans_2:
            self.Characters['Favorite Female Protagonist'] = char_ans_2

        # ------------- Q3

        char_ans_3 = await self.request_message(message.author, "Who's your favorite Male Antagonist?", "You may type `skip`")

        if char_ans_3:
            self.Characters['Favorite Male Antagonist'] = char_ans_3

        # ------------- Q4

        char_ans_4 = await self.request_message(message.author, "Who's your favorite Female Antagonist?", "You may type `skip`")

        if char_ans_4:
            self.Characters['Favorite Female Antagonist'] = char_ans_4

        # ------------- Q5

        char_ans_5 = await self.request_message(message.author, "Who's your favorite Couple?", "For example, Naruto x Hinata, Kousei x Kaori")

        if char_ans_5:
            self.Characters['Favorite Couple'] = char_ans_5

        # ------------- Q6

        char_ans_6 = await self.request_message(message.author, "What's your favorite Anime pet?", "For example, Happy from Fairy tail, Sadaharu from Gintama")

        if char_ans_6:
            self.Characters['Favorite Pet'] = char_ans_6 # 6 Questions

    # Functions

    async def request_emote(self, author : discord.User, message, footer, emotes : dict):

        message = await self.form_entry_channel.send(embed=self.Question_Embed(author, self.users[author.id]["Question"], message, footer))

        for i in emotes:
            await message.add_reaction(i)

        if self.users[author.id]["Question"] > 2:
            await message.add_reaction(self.emotes['SKIP'])


        response = await self.wait_for_reaction(author, emotes)

        await message.delete()

        self.users[author.id]["Question"] += 1

        return response

    async def request_message(self, author : discord.User, message, footer):

        reply = await self.form_entry_channel.send(embed=self.Question_Embed(author, self.users[author.id]["Question"], message, footer))

        response = await self.wait_for_message(author)

        await reply.delete()

        self.users[author.id]["Question"] += 1

        return response

    async def wait_for_message(self, author: discord.User):

        def message_check(message):
            return message.channel.id == self.form_entry_channel_id and message.author == author

        try:
            response = await self.bot.wait_for('message', check=message_check, timeout=self.timeout)
            character_limit = 200

            if "skip" in response.content.lower():
                await response.delete()
                return None

            while len(response.content) > character_limit:
                await self.form_entry_channel.send(f'Sorry, we only allow responses with less than {character_limit} characters! Please try again.')
                try:
                    response = await self.bot.wait_for('message', check=message_check, timeout=self.timeout)
                except asyncio.TimeoutError:
                    del self.users[author.id]

            await response.delete()
            return response.content
        except asyncio.TimeoutError:
            del self.users[author.id]

    async def wait_for_reaction(self, author: discord.User, emotes : dict):

        def response_check(reaction, user):
            if reaction.message.channel.id == self.form_entry_channel_id:
                if user == author:
                    if str(reaction.emoji) in emotes:
                        return True

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=response_check, timeout=self.timeout)
            return str(reaction.emoji)
        except asyncio.TimeoutError:
            del self.users[author.id]

    def Question_Embed(self, author, question_no, question, footer):
        embed = discord.Embed(
            title = f"Question {question_no} / 31",
            description = question,
            colour = 0x37e666
            )
        embed.set_footer(text=footer)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        return embed

    async def Colour(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://www.colr.org/json/color/random") as r:
                res = await r.json(content_type=None)
                colour = res["new_color"]
                embedcolour = int(colour, 16)

                return embedcolour






def setup(bot):
    bot.add_cog(AnimeForm(bot))
