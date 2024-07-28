import discord
from discord import app_commands
from core.classes import Cog_Extension
import json
import update

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

class Update(Cog_Extension) :
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
            await interaction.followup.send(f"更新完成! 現在版本是 {setdata["version"]}!")
        except Exception as e :
            await interaction.folloup.send(e)

async def setup(bot) :
    await bot.add_cog(Update(bot), guilds = [discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])