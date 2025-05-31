from discord.ext import commands
from discord.app_commands import Choice
import discord
import requests

class Hero(commands.Cog) :
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ElementIcon = { "fire" : "🔥", "water" : "💧", "wind" : "🌳", "light" : "✨", "dark" : "⚫"}
        self.info = requests.get(url="https://raw.githubusercontent.com/Lyuuwu/EpicSeven-bot/master/EpicSeven/data/GvgSolver/info.json").json()
        self.name_dic = requests.get(url="https://raw.githubusercontent.com/Lyuuwu/EpicSeven-bot/master/EpicSeven/data/GvgSolver/name-to-code.json").json()

    async def SelectHero(self, interaction : discord.Interaction, input : str) -> list[Choice[str]] :       
        matching_val = {val for input_val, val in self.name_dic.items() if input.lower() in input_val.lower()}
        matching_val = list(matching_val)[:10] # up to 25 heroes
        
        # return option
        return [
            Choice(
                name = f"{self.ElementIcon[self.info[val]['element'] ]} {self.info[val]['OptionName']} ({self.info[val]['rarity']})",
                value = val
            )
            for val in matching_val
        ]
