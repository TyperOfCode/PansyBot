import datetime
import discord
import mysql.connector

from discord.ext import commands

from utils.essentials.checks import check

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def apply(self, ctx):
        emojis = ["✖️", "✔️"]
        UID = str(ctx.author.id)
        category_emojis = []
        if ctx.message.guild.id == 540784184470274069 and ctx.channel.id == 660474909339680788:
            if not self.has_applied(UID):
                user = ctx.message.author
                guild = ctx.guild
                await ctx.message.delete()
                double_check = await user.send(embed=func.ENoFooter("Hey!", "Just to double check, you wish to apply for Helper in **My Anime Land**?"))
                await double_check.add_reaction(emojis[0])
                await double_check.add_reaction(emojis[1])

                def EmojisCheck(reaction, user):
                    return ctx.author == user and str(reaction.emoji) == emojis[0] or ctx.author == user and str(reaction.emoji) == emojis[1]
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=EmojisCheck)
                except asyncio.TimeoutError:
                    await start.delete()
                    await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                else:
                    if str(reaction.emoji) == emojis[0]:
                        await double_check.delete()
                        await user.send(embed=func.Editable_E("Application Cancelled", "Thanks for your participation", "Cancelled"))
                    elif str(reaction.emoji) == emojis[1]:
                        await double_check.delete()
                        await user.send("Ok perfect, you should get a notification about your application shortly.")
                        overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False), ctx.author: discord.PermissionOverwrite(read_messages=True)}
                        channel = await guild.create_text_channel(name=f"application-{user.id}", overwrites=overwrites)
                        mention = await channel.send(user.mention)
                        await mention.delete()
                        main = await channel.send(embed=func.ENoFooter("Alright Cool. Lets begin with some questions", f"{user.mention} How old are you?"))
                        try:
                            age = await self.bot.wait_for("message", timeout=300, check=lambda message: message.author == user)
                            await age.delete()
                        except asyncio.TimeoutError:
                            await msg.edit(embed=timeoutEmbed, delete_after=60)
                            await channel.delete()
                        else:
                            if age.content.isdigit() and int(age.content) > 12:
                                pass
                            else:
                                 await main.edit(embed=discord.Embed(title="Invalid Age", color=0xff0000, description="Age must be a number, and above 12."))
                    await main.edit(embed=func.ENoFooter("Which timezone are you in?", "This question is optional. Type 'N/A' if you do not wish to answer"))
                    try:
                        timezone = await self.bot.wait_for("message", timeout=500, check=lambda message: message.author == user)
                        await timezone.delete()
                    except asyncio.TimeoutError:
                        await msg.edit(embed=timeoutEmbed, delete_after=60)
                        await channel.delete()
                    else:
                        await main.edit(embed=func.ENoFooter("Why do you want to become Helper?", "Please give detail in your answer. You'll have a better chance, I promise."))
                        try:
                            reason = await self.bot.wait_for("message", timeout=300, check=lambda message: message.author == user)
                            await reason.delete()
                        except asyncio.TimeoutError:
                            await msg.edit(embed=timeoutEmbed, delete_after=60)
                            await channel.delete()
                        else:
                            await main.edit(embed=func.ENoFooter("Can you work as a team?", "You may be required to cover for another helper during their downtime.\n\nGive us a few reasons behind your answer"))
                            try:
                                teamwork = await self.bot.wait_for("message", timeout=300, check=lambda message: message.author == user)
                                await teamwork.delete()
                            except asyncio.TimeoutError:
                                await msg.edit(embed=timeoutEmbed, delete_after=60)
                                await channel.delete()
                            else:
                                await main.edit(embed=func.ENoFooter("Activity", "We take activity seriously. How active can you be throughout the week on average?"))
                                try:
                                    activity = await self.bot.wait_for("message", timeout=300, check=lambda message: message.author == user)
                                    await activity.delete()
                                except asyncio.TimeoutError:
                                    await msg.edit(embed=timeoutEmbed, delete_after=60)
                                    await channel.delete()
                                else:
                                    await main.edit(embed=func.ENoFooter("Your Tasks", "Helpers main task is to keep the activity, revive channels and to clean them. Are you capable of that?"))
                                    await main.add_reaction(emojis[0])
                                    await main.add_reaction(emojis[1])
                                    try:
                                        reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=EmojisCheck)
                                    except asyncio.TimeoutError:
                                        await start.delete()
                                        await ctx.author.send(embed=timeoutEmbed, delete_after=60)
                                    else:
                                        if str(reaction.emoji) == emojis[0]:
                                            await channel.delete()
                                            await user.send(embed=func.Editable_E("Application Cancelled", "Thanks for your participation", "Cancelled"))
                                        elif str(reaction.emoji) == emojis[1]:
                                            capable = "Yes"
                                            await main.clear_reactions()

                                            final = discord.Embed(
                                                title=f"{user.name}'s Helper Application ({age.content})",
                                                colour=0xf7d17,
                                                )
                                            final.add_field(name="Your Timezone", value=timezone.content, inline=True)
                                            final.add_field(name="Activity", value=activity.content, inline=True)
                                            final.add_field(name="Manage Tasks", value=capable, inline=True)
                                            final.add_field(name="Reasoning", value=reason.content, inline=False)
                                            final.add_field(name="Teamwork", value=teamwork.content, inline=False)
                                            await main.edit(embed=final)
                                            await channel.send(f"Congratulations {user.mention} you're one step closer to becoming a helper here at **My Anime Land**\n\nPlease leave us upto 7 days to review your application, please refrain from pinging staff.\n\nThis channel will be deleted in 60 seconds")
                                            self.add_id(user)
                                            await asyncio.sleep(60)
                                            await channel.delete()
                                            applog = self.bot.get_channel(657965850057506827)
                                            await applog.send(embed=final)
            else:
                await ctx.message.delete()
                user = ctx.author
                await user.send(embed=func.ENoFooter("Hey!", "You've already created an application in **My Anime Land**, so you cannot create another until that one has been completed."))

    def has_applied(self, UID):
        UID = str(UID)
        if sql.Entry_Check(UID, "userid", "applications"):
            return True

    def add_id(self, user):
        UID = (user.id)
        if not self.has_applied(UID):
            mydb = sql.createConnection()
            cur = mydb.cursor()
            cur.execute(f"INSERT into `applications` VALUES ('{UID}')")
            mydb.commit()
            return True
        else:
            return False

def setup(bot):
    bot.add_cog(Applications(bot))
