import discord
from discord import app_commands
import random
import json
from core.classes import Cog_Extension

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

class Banner(Cog_Extension) :
    def __init__(self, bot) :
        super().__init__(bot=bot)
    
    @app_commands.command(name="summon", description="抽卡! 誰出彩誰是狗")
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def summon(self, interaction : discord.Interaction) :
        r_cnt = 0
        res = []
        output = ""
        
        for _ in range(10) :
            ran_int = random.randint(1, 1000)
            
            if ran_int <= 20 :
                res.append("ssr")
            elif ran_int <= 200 :
                res.append("sr")
            else :
                res.append("r")
                r_cnt += 1
        
        if r_cnt == 10 :
            res[9] = "sr"
            
        for r in res :
            if r == "r" :
                output += "<:r:1078650392218447912>"
            elif r == "sr" :
                output += "<:sr:1009113698763296858>"
            else :
                output += "<:ssr:1205865912167571506>"

        await interaction.response.send_message(output)
        
    @app_commands.command(name="epic_summon", description="E7抽卡! 誰出彩誰是狗")
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def epic_summon(self, interaction : discord.Interaction) :
        r_cnt = 0
        res = []
        output = ""
        
        for _ in range(10) :
            ran_int = random.randint(1, 1000)
            
            if ran_int <= 20 :
                res.append("ssr")
            elif ran_int <= 200 :
                res.append("sr")
            else :
                res.append("r")
                r_cnt += 1
        
        if r_cnt == 10 :
            res[9] = "sr"
            
        for r in res :
            if r == "r" :
                output += "<:r:1255810106126368768>"
            elif r == "sr" :
                output += "<:sr:1256157022836097085>"
            else :
                output += "<:ssr:1256177377680035860>"

        await interaction.response.send_message(output)

async def setup(bot) :
    await bot.add_cog(Banner(bot), guilds = [discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])