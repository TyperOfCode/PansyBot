import discord
from discord.ext import commands
import sqlite3

class DatabaseFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def dbupdate(db, sql, variables):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(sql, variables)
    conn.commit()
    return

def dbselect(db, sql, variables):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(sql, variables)
    results = c.fetchone()
    if results is None:
        pass
    elif len(results) == 1:
        try:
            results = int(results[0])
        except TypeError:
            results = str(results[0])
        except ValueError:
            results = str(results[0])
    else:
        results = list(results)
    return results

def setup(bot):
    bot.add_cog(DatabaseFunctions(bot))
