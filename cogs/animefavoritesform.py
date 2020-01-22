__author__ = 'wallace05#0828'

from discord.ext import commands, tasks
from typing import Union
from concurrent import futures
import asyncio
import discord
import discord.utils
import threading

class AnimeFavoritesForm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.embed_color: discord.Color = discord.Color.blurple()
        self.timeout = 60

        self.completed_form_role_id = 662039067789099008

        # favorites channel id
        self.favorites_channel_id = 504040460524716037#662046896147136542

        # general bot channel id
        self.form_entry_channel_id = 504040460524716037#622906588562456576
        self.form_entry_channel = None

        # hold people that are taking the survey -.-
        self.taking_survey = set()

        self.responses_to_emoji_id = {
            'YES': 657275797228486682,
            'NO': 657275749249712195,
            '9': 662039058809356309,
            '8': 662039058423349253,
            '7': 662039057248944139,
            '6': 662038703723642911,
            '5': 662038703295692859,
            '4': 662038702955954207,
            '3': 662038701559513089,
            '2': 662038700607143985,
            '1': 662039056728981514,
            '0': 662039059379519499,
            'SKIP': '⛔'
        }

    @commands.Cog.listener('on_message')
    async def message_handler(self, message):
        # don't read from bots
        if message.author.bot:
            return

        self.form_entry_channel = self.bot.get_channel(self.form_entry_channel_id)
        if self.form_entry_channel is None:
            print('[AnimeFavoritesForm] The form entry channel does not exist. Unloading this cog.')
            self.bot.unload_extension(self.qualified_name)
            return

        # only listen for messages sent in the favorites channel
        if message.channel.id != self.favorites_channel_id:
            return

        if message.author.id in self.taking_survey:
            return

        self.taking_survey.add(message.author.id)

        # check if the user already has the role
        #completed_form_role = discord.utils.get(message.guild.roles, id=self.completed_form_role_id)
        
        #if completed_form_role is None:
        #    print('[AnimeFavoritesForm] The form completed role does not exist. Unloading this cog.')
        #    self.bot.unload_extension(self.qualified_name)
        #    return
        
        #if completed_form_role in message.author.roles:
        #    return

        self.form_entry_author = message.author

        # this is for checking if the custom emoji still exists and falling back to a default emoji if not
        response_emoji = {
            0: self.bot.get_emoji(self.responses_to_emoji_id['0']) or '0️⃣',
            1: self.bot.get_emoji(self.responses_to_emoji_id['1']) or '1️⃣', 
            2: self.bot.get_emoji(self.responses_to_emoji_id['2']) or '2️⃣', 
            3: self.bot.get_emoji(self.responses_to_emoji_id['3']) or '3️⃣', 
            4: self.bot.get_emoji(self.responses_to_emoji_id['4']) or '4️⃣', 
            5: self.bot.get_emoji(self.responses_to_emoji_id['5']) or '5️⃣',
            6: self.bot.get_emoji(self.responses_to_emoji_id['6']) or '6️⃣', 
            7: self.bot.get_emoji(self.responses_to_emoji_id['7']) or '7️⃣', 
            8: self.bot.get_emoji(self.responses_to_emoji_id['8']) or '8️⃣', 
            9: self.bot.get_emoji(self.responses_to_emoji_id['9']) or '9️⃣',
            'YES': self.bot.get_emoji(self.responses_to_emoji_id['YES']) or '👍',
            'NO': self.bot.get_emoji(self.responses_to_emoji_id['NO']) or '👎',
            'SKIP': self.responses_to_emoji_id['SKIP']
        }

        greeting_title = f'Hello, {message.author.name}! I\'ve seen that you sent a message at <#608076056208867328>, would you like to take our Animanga survey?'
        greeting_responses = { 
            response_emoji['YES']: ( 'Yes', None ), 
            response_emoji['NO']: ( 'No', None ), 
        }

        greeting_response = await self.__send_reaction_form_query(message.author, greeting_title, greeting_responses)

        if greeting_response != response_emoji['YES']:
            await self.form_entry_channel.send('Alright, thank you.')
            return
            
        display_message = await self.form_entry_channel.send('Let\'s start!')
        
        # this will hold all the user's responses
        responses = list()

        # this will hold all the role ids to add to the user at the end
        role_ids_to_add = list()

        number_of_questions = 29

        first_question_title = 'How much anime have you watched?'
        first_question_responses = { 
            response_emoji[1]: ( 'More than 5', 661860188931751961 ), 
            response_emoji[2]: ( 'More than 20', 661860189569417216 ), 
            response_emoji[3]: ( 'More than 50', 661860192119554048 ), 
            response_emoji[4]: ( 'More than 100', 662018064036003840 ), 
            response_emoji[5]: ( 'More than 300', 662018066489540609 ), 
            response_emoji[6]: ( 'More than 500', 662018066489540609 ), 
            response_emoji[0]: ( 'Skip', None ), 
        }

        first_question_response = await self.__send_reaction_form_query(message.author, first_question_title, first_question_responses, f'Question 1/{number_of_questions}')

        if first_question_response in first_question_responses:
            response, role_id = first_question_responses[first_question_response]
            responses.append(('Anime Watched', response))
            if role_id is not None:
                role_ids_to_add.append(role_id)
        else:
            return

        second_question_title = 'What do you prefer?'
        second_question_responses = { 
            response_emoji[1]: ( 'New Generation Anime', 662018072911020078 ), 
            response_emoji[2]: ( 'Old Generation Anime', 662018073028722748 ), 
            response_emoji[3]: ( 'Skip', None),  
        }

        second_question_response = await self.__send_reaction_form_query(message.author, second_question_title, second_question_responses, f'Question 2/{number_of_questions}')

        if second_question_response in second_question_responses:
            response, role_id = second_question_responses[second_question_response]
            responses.append(('Prefers', response))
            if role_id is not None:
                role_ids_to_add.append(role_id)
        else:
            return

        third_question_title = 'Favorite anime?'
        third_question_response = await self.__send_message_form_query(message.author, third_question_title, f'Question 3/{number_of_questions}')
        if third_question_response is None:
            return

        responses.append(('Favorite Anime', third_question_response))

        fourth_question_title = 'Anime world you wish to live in?'
        fourth_question_response = await self.__send_message_form_query(message.author, fourth_question_title, f'Question 4/{number_of_questions}')
        if fourth_question_response is None:
            return

        responses.append(('Anime World', fourth_question_response))

        fifth_question_title = 'Favorite anime studio?'
        fifth_question_response = await self.__send_message_form_query(message.author, fifth_question_title, f'Question 5/{number_of_questions}')
        if fifth_question_response is None:
            return

        responses.append(('Favorite Anime Studio', fifth_question_response))

        sixth_question_title = 'Write the title of an anime that you think is overrated.'
        sixth_question_response = await self.__send_message_form_query(message.author, sixth_question_title, f'Question 6/{number_of_questions}')
        if sixth_question_response is None:
            return

        responses.append(('Overrated Anime', sixth_question_response))

        seventh_question_title = 'Write the title of an anime that you think is underrated.'
        seventh_question_response = await self.__send_message_form_query(message.author, seventh_question_title, f'Question 7/{number_of_questions}')
        if seventh_question_response is None:
            return

        responses.append(('Underrated Anime', seventh_question_response))

        eigth_question_title = 'Which Anime Opening is your favorite to listen to?'
        eigth_question_response = await self.__send_message_form_query(message.author, eigth_question_title, f'Question 8/{number_of_questions}')
        if eigth_question_response is None:
            return

        responses.append(('Favorite Anime Opening', eigth_question_response))

        ninth_question_title = 'Which Anime Ending is your favorite to listen to?'
        ninth_question_response = await self.__send_message_form_query(message.author, ninth_question_title, f'Question 9/{number_of_questions}')
        if ninth_question_response is None:
            return

        responses.append(('Favorite Anime Ending', ninth_question_response))

        tenth_question_title = 'How much manga have you read?'
        tenth_question_responses = { 
            response_emoji[1]: ( 'More than 5', 662018066611306548 ), 
            response_emoji[2]: ( 'More than 20', 662018067978649610 ), 
            response_emoji[3]: ( 'More than 50', 662018068012072976 ), 
            response_emoji[4]: ( 'More than 100', 662018069052260414 ), 
            response_emoji[5]: ( 'More than 300', 662018070591701055 ), 
            response_emoji[6]: ( 'More than 500', 662018070675718144 ), 
            response_emoji[0]: ( 'Skip', None ), 
        }

        tenth_question_response = await self.__send_reaction_form_query(message.author, tenth_question_title, tenth_question_responses, f'Question 10/{number_of_questions}')

        if tenth_question_response in tenth_question_responses:
            response, role_id = tenth_question_responses[tenth_question_response]
            responses.append(('Manga Read', response))
            if role_id is not None:
                role_ids_to_add.append(role_id)
        else:
            return

        eleventh_question_title = 'Favorite manga?'
        eleventh_question_response = await self.__send_message_form_query(message.author, eleventh_question_title, f'Question 11/{number_of_questions}')
        if eleventh_question_response is None:
            return

        responses.append(('Favorite Manga', eleventh_question_response))

        twelth_question_title = 'Weirdest manga you read?'
        twelth_question_response = await self.__send_message_form_query(message.author, twelth_question_title, f'Question 12/{number_of_questions}')
        if twelth_question_response is None:
            return

        responses.append(('Weirdest Manga', twelth_question_response))

        thirteenth_question_title = 'Write the title of a manga that you think is overrated.'
        thirteenth_question_response = await self.__send_message_form_query(message.author, thirteenth_question_title, f'Question 13/{number_of_questions}')
        if thirteenth_question_response is None:
            return

        responses.append(('Overrated Manga', thirteenth_question_response))

        fourteenth_question_title = 'Underrated manga?'
        fourteenth_question_response = await self.__send_message_form_query(message.author, fourteenth_question_title, f'Question 14/{number_of_questions}')
        if fourteenth_question_response is None:
            return

        responses.append(('Underrated Manga', fourteenth_question_response))

        fifteenth_question_title = 'How many Light Novels have you read?'
        fifteenth_question_responses = { 
            response_emoji[1]: ( 'More than 5', None ), 
            response_emoji[2]: ( 'More than 20', None ), 
            response_emoji[3]: ( 'More than 50', None ), 
            response_emoji[4]: ( 'More than 100', None ), 
            response_emoji[5]: ( 'More than 300', None ), 
            response_emoji[6]: ( 'More than 500', None ), 
            response_emoji[0]: ( 'Skip', None ), 
        }

        fifteenth_question_response = await self.__send_reaction_form_query(message.author, fifteenth_question_title, fifteenth_question_responses, f'Question 15/{number_of_questions}')

        if fifteenth_question_response in fifteenth_question_responses:
            response, role_id = fifteenth_question_responses[fifteenth_question_response]
            responses.append(('Light Novels Read', response))
            if role_id is not None:
                role_ids_to_add.append(role_id)
        else:
            return

        sixteenth_question_title = 'Favorite Light Novel?'
        sixteenth_question_response = await self.__send_message_form_query(message.author, sixteenth_question_title, f'Question 16/{number_of_questions}')
        if sixteenth_question_response is None:
            return

        responses.append(('Favorite Light Novel', sixteenth_question_response))

        seventeenth_question_title = 'What is your favorite genre?'
        seventeenth_question_responses = { 
            response_emoji[1]: ( 'Action', 662039056728981514 ), 
            response_emoji[2]: ( 'Drama', 662038700607143985 ), 
            response_emoji[3]: ( 'Comedy', 662038701559513089 ), 
            response_emoji[4]: ( 'Isekai', 662038702955954207 ), 
            response_emoji[5]: ( 'Romance', 662038703295692859 ), 
            response_emoji[6]: ( 'Harem', 662038703723642911 ), 
            response_emoji[7]: ( 'Slice of Life', 662039057248944139 ), 
            response_emoji[8]: ( 'Sports', 662039058423349253 ), 
            response_emoji[9]: ( 'Shounen', 662039058809356309 ), 
            response_emoji[0]: ( 'Seinen', 662039059379519499 ), 
            response_emoji['SKIP']: ( 'Skip', None ), 
        }

        seventeenth_question_response = await self.__send_reaction_form_query(message.author, seventeenth_question_title, seventeenth_question_responses, f'Question 17/{number_of_questions}')

        if seventeenth_question_response in seventeenth_question_responses:
            response, role_id = seventeenth_question_responses[seventeenth_question_response]
            responses.append(('Favorite Genre', response))
            if role_id is not None:
                role_ids_to_add.append(role_id)
        else:
            responses.append(('Favorite Genre', None))

        eighteenth_question_title = 'Favorite Anime Movie?'
        eighteenth_question_response = await self.__send_message_form_query(message.author, eighteenth_question_title, f'Question 18/{number_of_questions}')
        if eighteenth_question_response is None:
            return

        responses.append(('Favorite Anime Movie', eighteenth_question_response))

        nineteenth_question_title = 'Favorite Anime Episode?'
        nineteenth_question_response = await self.__send_message_form_query(message.author, nineteenth_question_title, f'Question 19/{number_of_questions}')
        if nineteenth_question_response is None:
            return

        responses.append(('Favorite Anime Episode', nineteenth_question_response))

        twentieth_question_title = 'Favorite Anime Season?'
        twentieth_question_description = 'For example: Summer 2017, Winter 2019, etc.'
        twentieth_question_response = await self.__send_message_form_query(message.author, twentieth_question_title, twentieth_question_description, f'Question 20/{number_of_questions}')
        if twentieth_question_response is None:
            return

        responses.append(('Favorite Anime Season', twentieth_question_response))

        twenty_first_question_title = 'Favorite Manga Volume?'
        twenty_first_question_description = 'For example: Volume 10 of Slam Dunk, Volume 5 of Kimetsu no Yaiba, etc.'
        twenty_first_question_response = await self.__send_message_form_query(message.author, twenty_first_question_title, twenty_first_question_description, f'Question 21/{number_of_questions}')
        if twenty_first_question_response is None:
            return

        responses.append(('Favorite Manga Volume', twenty_first_question_response))

        twenty_second_question_title = 'Favorite Male Protagonist?'
        twenty_second_question_response = await self.__send_message_form_query(message.author, twenty_second_question_title, f'Question 22/{number_of_questions}')
        if twenty_second_question_response is None:
            return

        responses.append(('Favorite Male Protagonist', twenty_second_question_response))

        twenty_third_question_title = 'Favorite Female Protagonist?'
        twenty_third_question_response = await self.__send_message_form_query(message.author, twenty_third_question_title, f'Question 23/{number_of_questions}')
        if twenty_third_question_response is None:
            return

        responses.append(('Favorite Female Protagonist', twenty_third_question_response))

        twenty_fourth_question_title = 'Favorite Antagonist?'
        twenty_fourth_question_response = await self.__send_message_form_query(message.author, twenty_fourth_question_title, f'Question 24/{number_of_questions}')
        if twenty_fourth_question_response is None:
            return

        responses.append(('Favorite Antagonist', twenty_fourth_question_response))

        twenty_fifth_question_title = 'Favorite Male Support Character?'
        twenty_fifth_question_response = await self.__send_message_form_query(message.author, twenty_fifth_question_title, f'Question 25/{number_of_questions}')
        if twenty_fifth_question_response is None:
            return

        responses.append(('Favorite Male Support Character', twenty_fifth_question_response))

        twenty_sixth_question_title = 'Favorite Female Support Character?'
        twenty_sixth_question_response = await self.__send_message_form_query(message.author, twenty_sixth_question_title, f'Question 26/{number_of_questions}')
        if twenty_sixth_question_response is None:
            return

        responses.append(('Favorite Female Support Character', twenty_sixth_question_response))

        twenty_seventh_question_title = 'Favorite Anime Couple?'
        twenty_seventh_question_response = await self.__send_message_form_query(message.author, twenty_seventh_question_title, f'Question 27/{number_of_questions}')
        if twenty_seventh_question_response is None:
            return

        responses.append(('Favorite Anime Couple', twenty_seventh_question_response))

        twenty_eigth_question_title = 'Favorite Anime Pet?'
        twenty_eigth_question_response = await self.__send_message_form_query(message.author, twenty_eigth_question_title, f'Question 28/{number_of_questions}')
        if twenty_eigth_question_response is None:
            return

        responses.append(('Favorite Anime Pet', twenty_eigth_question_response))

        image_query_title = 'Finally! Please upload an image of your favorite anime or character to include in your form.'
        image_query_description = 'Note: You mustn\'t use any non-anime related images, your embed will be deleted.\n' \
                                  'Note2: You shouldn\'t delete your uploaded image, it will be invalid.\n' \
                                  'Thank you so much for taking this survey!'
        embed = self.__create_embedded_message(message.author, image_query_title, image_query_description, 'Final question!')
        await self.form_entry_channel.send(embed=embed)

        image_url = None

        def image_query_check(msg):
            return len(msg.attachments) > 0 and msg.author == message.author

        try:
            msg = await self.bot.wait_for('message', check=image_query_check, timeout=self.timeout)
            image_url = msg.attachments[0].url
        except asyncio.TimeoutError:
            image_url = None

        responses.append(image_url)

        embed = self.__create_embedded_message(message.author, f'{message.author}\'s animanga form!')

        for title, description in responses[:-1]:
            if description == '':
                continue
            embed.add_field(name=title, value=description, inline=True)

        embed.set_image(url=responses[-1])
        await message.channel.send(embed=embed)

        roles_to_add_to_user = list()
        for role_id in role_ids_to_add:
            role = self.bot.get_role(role_id)
            if role:
                roles_to_add_to_user.append(role)

        await message.author.add_roles(*roles_to_add_to_user, reason='Animanga survey response role')
        self.taking_survey.discard(message.author.id)

    async def __send_message_form_query(self, author: discord.User, title: str, description: str = '', footer: str = '') -> Union[str, None]:
        """Sends a message form query to the user to message with a response

        Parameters
        ----------
        author: discord.User
            The user taking the survey

        title: str
            The title of the embed

        description: str [Optional] = ''
            The description of the embed

        footer: str [Optional] = ''
            The footer of the embed

        Returns
            str
                if the user responds with a message, or
            None
                if the user does not respond in time
        """

        embed = self.__create_embedded_message(author, title, description, footer)
        question = await self.form_entry_channel.send(embed=embed)

        async def will_skip():
            skip_emoji = self.bot.get_emoji(658785774258487299) or '0️⃣'

            await question.add_reaction(skip_emoji)
            skip = await self.__await_reaction_add(author, { skip_emoji })
            return '' if skip is not None else None

        async def will_write():
            return await self.__await_message_send(author)

        skip_future = asyncio.ensure_future(will_skip())
        write_future = asyncio.ensure_future(will_write())

        done, pending = await asyncio.wait(
            [skip_future, write_future],
            return_when=asyncio.FIRST_COMPLETED,
        )

        response = None

        for task in pending:
            task.cancel()

        for task in done:
            response = task.result()

        await question.delete() 
        return response
        
    async def __send_reaction_form_query(self, author: discord.User, title: str, responses: dict, footer: str = '') -> Union[discord.Emoji, str, None]:
        """Sends a reaction form query to the user to react with a response
        
        Parameters
        ----------
        author: discord.User
            The user taking the survey

        title: str
            The title of the embed

        responses: dict({ int: tuple[int, None] })
            A dictionary holding the reaction responses mapped to their description 
            and role ID if the reaction gives one

        footer: str [Optional] = ''
            The footer of the embed

        Returns
        -------
        Returns a
            discord.Emoji
                if the user reacts with a custom guild emoji,
            str
                if the user reacts with a unicode emoji, or
            None
                if the user doesn't react at all
        """
        
        description = ''
        for response in responses:
            description += f'{response} - {responses[response][0]}\n'
        
        embed = self.__create_embedded_message(author, title, description, footer)
        question = await self.form_entry_channel.send(embed=embed)
        response = None

        for response in responses:
            await question.add_reaction(response)
            await asyncio.sleep(1/4)

        response = await self.__await_reaction_add(author, responses)
        await question.delete()
        return response

    async def __await_message_send(self, author: discord.User) -> Union[str, None]:
        """Waits for the user to send a message in responce to a survey question

        Parameters
        ----------
        author
            The user taking the survey

        Returns
        -------
        Returns a
            str
                if the user responds with a message in time
            None
                if the user doesn't respond at all
        """

        def message_check(message):
            return message.author == author and message.channel == self.form_entry_channel

        try:
            response = await self.bot.wait_for('message', check=message_check, timeout=self.timeout)
            character_limit = 200

            while len(response.content) > character_limit:
                await self.form_entry_channel.send(f'Sorry, we only allow responses with >= {character_limit} characters! Please try again.')
                
                try:
                    response = await self.bot.wait_for('message', check=message_check, timeout=self.timeout)
                except asyncio.TimeoutError:
                    return None

            await response.delete()
            return response.content
        except asyncio.TimeoutError:
            return None

    async def __await_reaction_add(self, author: discord.User, responses: set) -> Union[discord.Emoji, str, None]:
        """Waits for the user to send a reaction in response to a survey question
        

        Parameters
        ----------
        author: discord.User
            The author that is taking the survey

        responses: set
            A set of emoji that is expected for the user to react

        Returns
        -------
        Returns a
            discord.Emoji
                if the emoji that the user reacted is a custom guild emoji
            str
                if the emoji that the user reacted is a unicode emoji
            None
                if the user doesn't react at all
        """
        
        def response_check(reaction, user):
            return reaction.message.channel.id == self.form_entry_channel_id and reaction.emoji in responses and user == author

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=response_check, timeout=self.timeout)
            return reaction.emoji
        except asyncio.TimeoutError:
            return None
        
    def __create_embedded_message(self, author, title, description='', footer=None):
        embed = discord.Embed(title=title, description=description, color=self.embed_color)
        embed.set_author(name=author.name, icon_url=str(author.avatar_url))
        if footer:
            embed.set_footer(text=footer, icon_url=str(author.avatar_url))
        return embed 

def setup(bot):
    bot.add_cog(AnimeFavoritesForm(bot))