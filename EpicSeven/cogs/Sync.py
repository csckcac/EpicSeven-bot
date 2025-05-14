from core.classes import Cog_Extension
from discord.ext import commands
import discord
import json

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

def is_author() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return commands.check(predicate)

class Sync(Cog_Extension) :
    def __init__(self, bot):
        super().__init__(bot=bot)
    
    @is_author()
    @commands.command(help = "連結slash command到伺服器")
    async def sync(self, ctx) :
        try :
            fmt = await ctx.bot.tree.sync(guild = ctx.guild)
            await ctx.send(f"Synced {len(fmt)} commands.")
        except Exception as e :
            await ctx.send(e)
        
async def setup(bot) :
    await bot.add_cog(Sync(bot), guilds=[discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])