import discord
import aiohttp
import json
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from core.classes import Cog_Extension

info_path = "EpicSeven/data/GvgSolver/info.json"
name_dic_path = "EpicSeven/data/GvgSolver/name-to-code.json"

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)
   
with open(info_path, encoding="utf-8") as fp :
    info = json.load(fp)
        
with open(name_dic_path, encoding="utf-8") as fp :
    name_dic = json.load(fp)

# 將角色的icon放到名字前面 並組合三個角色的字串
def make_team(info, heroses):
    return "  ".join(f"<:{hero}:{info[hero]['IconId']}> {info[hero]['DisplayName']}" for hero in heroses)

def is_author() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return commands.check(predicate)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

class GvgSolver(Cog_Extension) :
    def __init__(self, bot):
        self.bot = bot
        self.info = info
        self.name_dic = name_dic
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
        return [Choice(name = f"{self.ElementIcon[self.info[val]['element'] ]} {self.info[val]['OptionName']} ({self.info[val]['rarity']})", value = val) for val in matching_val]
    
    @app_commands.command(description="GVG進攻解陣(支援遊戲內名稱、角色簡稱、英文名稱)")
    @app_commands.autocomplete(hero1 = name_autocomplete, hero2 = name_autocomplete, hero3 = name_autocomplete)
    async def solve_gvg(self, interaction : discord.Interaction, hero1 : str, hero2 : str, hero3 : str) :
        await interaction.response.defer()
        # 發生重複選擇
        if (hero1 == hero2) or (hero1 == hero3) or (hero2 == hero3) :
            await interaction.followup.send("不能有重複的選項!! 請再試一次!")
            return
        
        # 選擇錯誤: 直接輸入
        if (hero1 not in self.info) or (hero2 not in self.info) or (hero3 not in self.info) :
            await interaction.followup.send("發生錯誤!! 請再試一次! 請注意要用選的") 
            return
        
        # 向目標伺服器請求
        async with aiohttp.ClientSession() as session :
            async with session.post(self.target_url, headers=self.headers, data=f"{hero1},{hero2},{hero3}") as r :
                if r.status == 200 :
                    data_dic = await r.json(encoding="utf-8")
                else :
                    await interaction.followup.send("發生錯誤! 請再試一次 >.<")
                    return
        
        try :
            # 沒有數據
            if "status" in data_dic and data_dic["status"] == "ERROR" :
                await interaction.followup.send(f"目前紀錄沒有 {make_team(self.info, [hero1, hero2, hero3])} 的解法")
                return
            
            # 排序 : 勝利場數降冪 取前20個
            teams = sorted(data_dic["data"].items(), key=lambda item: (-item[1]['w'], -item[1]['d'], item[1]['l']))[:20]
            
            # 創建 embed
            embed = discord.Embed(title=f"勝利場數最多的前{len(teams)}種組合", color=0x00ffff)
            embed.add_field(name=f"敵方陣容 :  {make_team(self.info, [hero1, hero2, hero3])}", value="\u200B", inline=False)
            embed.add_field(name="進攻陣容 :", value="", inline=False)
            
            for team in teams :
                # 將隊伍中的角色拆開
                heroes = team[0].split(",")
                embed.add_field(name=f"{make_team(self.info, heroes)}   {self.win} {team[1]['w']}  {self.lose} {team[1]['l']}", value="", inline=False)
                
            await interaction.followup.send(embed=embed)
            
        except Exception as e :
            await interaction.followup.send(e)
    
    @bot.tree.command(
        name = "solve_gvg_helper",
        description = "solve_gvg 指令使用說明",
        guild = discord.Object(id=setdata["Discord-Server-Id"]["main"])
    )
    async def help_(self, interaction) :
        await interaction.response.send_message("請去看 <#1256273173414940743>")
    
    
    @bot.tree.command(
        name = "modify_hero_info",
        description = "新增或修改英雄資訊",
    )
    @is_author()
    async def modify_hero_info(self, interaction, code : str, optionname : str, displayname : str, iconid : str, rarity : int, element : str) :
        await interaction.response.defer()
        
        try :
            self.info[code] = {
                "OptionName" : optionname,
                "DisplayName" : displayname,
                "IconId" : iconid,
                "rarity" : rarity,
                "element" : element
            }
            
            await self.save_json(info_path, self.info)
            
            await interaction.followup.send("完成變更!!")
        except Exception as e :
            await interaction.followup.send(f"發生 {e} 的錯誤!\n請再試一次 >.<")
    
    @bot.tree.command(
        name="remove_hero_info",
        description="刪除英雄資訊"
    )
    @is_author()
    async def remove_hero_info(self, interaction, code : str) :
        await interaction.response.defer()

        try :
            if code in self.info :
                self.info.pop(code)
                await self.save_json(info_path, self.info)
                await interaction.followup.send(f"完成刪除{code}!")
            else :
                await interaction.followup.send(f"找不到 {code} ! 請再試一次 >.<")
        except Exception as e :
            await interaction.followup.send(f"發生 {e} 的錯誤!\n請再試一次 >.<")
            
    @bot.tree.command(
        name="add_name",
        description="增加選項可接受的名稱 names 支援多組名稱 請用空格隔開 code為該英雄的編碼"
    )
    @is_author()
    async def add_name(self, interaction, names : str, code : str) :
        await interaction.response.defer()
        
        try :
            if code not in self.info :
                await interaction.followup.send(f"目前的英雄資訊沒有 {code} 請先更新英雄資訊!")
                return

            split = names.split(' ')
            self.name_dic.update({name : code for name in split})
            await self.save_json(name_dic_path, self.name_dic)
            await interaction.followup.send(f"完成 {code} 的更新!")
        except Exception as e :
            await interaction.followup.send(f"發生 {e} 的錯誤!\n請再試一次 >.<")
            
    @bot.tree.command(
        name="remove_name",
        description="刪除選項可接受的名稱 names 支援多組名稱 請用空格隔開"
    )
    @is_author()
    async def remove_name(self, interaction, names : str) :
        await interaction.response.defer()
        
        try :
            split = names.split()
            unvalid = [name for name in split if self.name_dic.pop(name, None) is None]
            
            await self.save_json(name_dic_path, self.name_dic)
            
            if len(unvalid) == 0 :
                await interaction.followup.send("完成刪除!!")
            else :
                await interaction.followup.send(f"{unvalid} 刪除失敗，原因為不在資料中，請再試一次!")   
        except Exception as e :
            await interaction.followup.send(f"發生 {e} 的錯誤!\n請再試一次 >.<")
            
    @bot.tree.command(
        name="remove_all_name",
        description="刪除全部編碼為code的名稱 支援多組code刪除 多組code請用空格隔開"
    )
    @is_author()
    async def remove_all_name(self, interaction, code : str) :
        await interaction.response.defer()
        
        try :
            split = code.split()
            self.name_dic = {n : c for n, c in self.name_dic.items() if c not in split}
            
            await self.save_json(name_dic_path, self.name_dic)
            await interaction.followup.send(f"完成刪除!!")
        except Exception as e :
            await interaction.followup.send(f"發生 {e} 的錯誤!\n請再試一次 >.<")
    
    
async def setup(bot) :
    await bot.add_cog(GvgSolver(bot), guilds=[discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])