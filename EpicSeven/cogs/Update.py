import discord
from discord import app_commands
from discord.ext import commands
from core.classes import Cog_Extension
import json
import update

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)
    
def is_author() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return commands.check(predicate)

class Update(Cog_Extension) :
    def __init__(self, bot):
        super().__init__(bot=bot)
    
    @is_author()
    @app_commands.command(
        name="update_bot",
        description="更新bot"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def update_bot(self, interaction) :        
        try :
            await interaction.response.defer()
            await update.update_bot()
            with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
                setdata = json.load(jset)
            await interaction.followup.send(f"更新完成! 現在版本是 {setdata['version']}!")
        except Exception as e :
            await interaction.folloup.send(e)
            
    @app_commands.command(
        name="version_check",
        description="確認bot當前的版本"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def version_check(self, interaction) :
        with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
            setdata = json.load(jset)
        await interaction.response.send_message(f"現在的版本是 {setdata['version']}!")

async def setup(bot) :
    await bot.add_cog(Update(bot), guilds = [discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])