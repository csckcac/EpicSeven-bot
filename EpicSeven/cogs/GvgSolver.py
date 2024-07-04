import discord
import requests
import json
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from core.classes import Cog_Extension

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)
    
with open("EpicSeven/data/GvgSolver/info.json", encoding="utf-8") as fp :
        info = json.load(fp)
        
with open("EpicSeven/data/GvgSolver/name-to-code.json", encoding="utf-8") as fp :
    name_dic = json.load(fp)

# 將角色的icon放到名字前面 並組合三個角色的字串
def make_team(info, heroses):
    return "  ".join(f"<:{hero}:{info[hero]['IconId']}> {info[hero]['DisplayName']}" for hero in heroses)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

class GvgSolver(Cog_Extension) :
    def __init__(self, bot):
        self.bot = bot
        self.ElementIcon = { "fire" : "🔥", "water" : "💧", "wind" : "🌳", "light" : "✨", "dark" : "⚫"}
        self.win = "<:battle_pvp_icon_win:1255810029857013871>"
        self.lose = "<:battle_pvp_icon_lose:1255810014120251462>"
        self.target_url = "https://krivpfvxi0.execute-api.us-west-2.amazonaws.com/dev/getDef"
        self.headers = {
                        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
                        "Accept": "text/plain, */*; q=0.01",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Accept-Language": "zh-TW",
                        "Sec-Ch-Ua-Mobile": "?0",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.57 Safari/537.36",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Origin": "https://fribbels.github.io",
                        "Sec-Fetch-Site": "cross-site",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                        "Referer": "https://fribbels.github.io/",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Priority": "u=1, i"
                    }

    # autocomplete篩選
    async def name_autocomplete(self, interaction : discord.Interaction, input : str) :       
        matching_val = {val for input_val, val in name_dic.items() if input.lower() in input_val.lower()}
        matching_val = list(matching_val)[:25] # 至多25個角色選擇
        
        # 回傳 顯示文字與回傳數值
        return [Choice(name = f"{self.ElementIcon[info[val]['element'] ]} {info[val]['OptionName']} ({info[val]['rarity']})", value = val) for val in matching_val]
    
    @app_commands.command(description="GVG進攻解陣(支援遊戲內名稱、角色簡稱、英文名稱)")
    @app_commands.autocomplete(hero1 = name_autocomplete, hero2 = name_autocomplete, hero3 = name_autocomplete)
    async def solve_gvg(self, interaction : discord.Interaction, hero1 : str, hero2 : str, hero3 : str) :
        # 發生重複選擇
        if (hero1 == hero2) or (hero1 == hero3) or (hero2 == hero3) :
            await interaction.response.send_message("不能有重複的選項!! 請再試一次!")
            return
        
        # 選擇錯誤: 直接輸入
        if (hero1 not in info) or (hero2 not in info) or (hero3 not in info) :
            await interaction.response.send_message("發生錯誤!! 請再試一次! 請注意要用選的") 
        
        # 向目標伺服器請求
        data_dic = requests.post(self.target_url, headers=self.headers, data=f"{hero1},{hero2},{hero3}").json()
        
        try :
            # 沒有數據
            if "status" in data_dic and data_dic["status"] == "ERROR" :
                await interaction.response.send_message(f"目前紀錄沒有 {make_team(info, [hero1, hero2, hero3])} 的解法")
                return
            
            # 排序 : 勝利場數降冪 取前20個
            teams = sorted(data_dic["data"].items(), key=lambda item: (-item[1]['w'], -item[1]['d'], item[1]['l']))[:20]
            
            # 創建 embed
            embed = discord.Embed(title=f"勝利場數最多的前{len(teams)}種組合", color=0x00ffff)
            embed.add_field(name=f"敵方陣容 :  {make_team(info, [hero1, hero2, hero3])}", value="\u200B", inline=False)
            embed.add_field(name="進攻陣容 :", value="", inline=False)
            
            for team in teams :
                # 將隊伍中的角色拆開
                heroes = team[0].split(",")
                embed.add_field(name=f"{make_team(info, heroes)}   {self.win} {team[1]['w']}  {self.lose} {team[1]['l']}", value="", inline=False)
                
            await interaction.response.send_message(embed=embed)
            
        except Exception as e :
            await interaction.response.send_message(e)
    
    @bot.tree.command(
        name = "solve_gvg_helper",
        description = "solve_gvg 指令使用說明",
        guild = discord.Object(id=setdata["Discord-Server-Id"]["main"])
    )
    async def help_(self, interaction) :
        await interaction.response.send_message("請去看 <#1256273173414940743>")
    
async def setup(bot) :
    await bot.add_cog(GvgSolver(bot), guilds=[discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])