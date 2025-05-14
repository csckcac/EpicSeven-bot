import discord
import aiohttp
import json
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from core.classes import Cog_Extension
from core.Hero import Hero

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

# 將角色的icon放到名字前面 並組合三個角色的字串
def make_team(info, heroses):
    return "  ".join(f"<:{hero}:{info[hero]['IconId']}> {info[hero]['DisplayName']}" for hero in heroses if hero)

def is_author() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return app_commands.check(predicate)

def extract_Eng(name : str) :
    split = name.split('|')
    return split[1].strip() if len(split) > 1 else name.strip()

class GvgSolver(Cog_Extension, Hero) :
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.win = "<:battle_pvp_icon_win:1255810029857013871>"
        self.lose = "<:battle_pvp_icon_lose:1255810014120251462>"
        self.target_url = "https://z4tfy2r5kc.execute-api.us-west-2.amazonaws.com/dev/getDef"
        self.headers = {
                        "Sec-Ch-Ua" : '"Not;A=Brand";v="24", "Chromium";v="128"',
                        "Accept" : "text/plain, */*; q=0.01",
                        "Sec-Ch-Ua-Platform": "Windows",
                        "Accept-Language" : "zh-TW,zh;q=0.9",
                        "Sec-Ch-Ua-Mobile" : "?0",
                        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36",
                        "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin" : "https://fribbels.github.io",
                        "Sec-Fetch-Site" : "cross-site",
                        "Sec-Fetch-Mode" : "cors",
                        "Sec-Fetch-Dest" : "empty",
                        "Referer" : "https://fribbels.github.io/",
                        "Accept-Encoding" : "gzip, deflate, br",
                        "Priority" : "u=1, i"
                    }

    @app_commands.command(description="GVG進攻解陣(支援遊戲內名稱、角色簡稱、英文名稱)")
    @app_commands.describe(hero1 = "選擇 一個英雄(使用滑鼠左鍵 或 鍵盤ENTER鍵，手機的話用點的)", hero2 = "選擇 一個英雄(使用滑鼠左鍵 或 鍵盤ENTER鍵，手機的話用點的)", hero3 = "選擇 一個英雄(使用滑鼠左鍵 或 鍵盤ENTER鍵，手機的話用點的)")
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"])
    @app_commands.autocomplete(hero1 = Hero.SelectHero, hero2 = Hero.SelectHero, hero3 = Hero.SelectHero)
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
                heroes = [hero for hero in team[0].split(",") if hero in self.info]
                total = (team[1]['w'] + team[1]['d'] + team[1]['l']) * 2
                wins = team[1]['w'] * 2 + team[1]['d']
                rate = float(wins / total)
                embed.add_field(name=f"{make_team(self.info, heroes)}   {self.win} {team[1]['w']}  {self.lose} {team[1]['l']}  |  {rate:.1%}", value="", inline=False)
            
            
            EngName = [ self.info[hero1]["OptionName"], self.info[hero2]["OptionName"], self.info[hero3]["OptionName"] ]
            EngName = [ extract_Eng(hero) for hero in EngName ]
            EngName = [ name.replace(" ", "%20") for name in EngName]
            
            link = "https://fribbels.github.io/e7/gw-meta.html?def=" + ','.join(EngName)
            
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="更多進攻陣容:", value=link, inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e :
            await interaction.followup.send(e)    
    
    @app_commands.command(
        name="gvg_helper",
        description="GVG進攻解陣指令 - 使用說明"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"])
    async def gvg_helper(self, interaction) :
        try :
            embed1 = discord.Embed(title="GVG進攻陣容指令 - 使用說明")
            
            embed2 = discord.Embed(title="1. 在<#1256260728894001193> 輸入 '/' (不用輸入')")
            
            embed3 = discord.Embed(title='2. 點選左側 "第七史詩" 圖示')
            embed3.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259512664686854214/2024-07-07_221150.png?ex=668bf413&is=668aa293&hm=3d37ed7e76db4318d66ccbe2bcb73d7d39645c9ac38f4f22cb8144a1c34e54a6&=&format=webp&quality=lossless")
            
            embed4 = discord.Embed(title="3. 點選右方 /solve_gvg (也可以直接輸入/solve_gvg 就可以跳過2.)")
            embed4.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259513240116006932/2024-07-07_221505.png?ex=668bf49d&is=668aa31d&hm=ed2f327b0a85c4f4bdd2a9268c3a958a04e86bb7b7a3fb2b2753aabda65736dc&=&format=webp&quality=lossless")
            
            embed5 = discord.Embed(title="4. 輸入英雄名稱(支援遊戲內的名稱、玩家間的簡稱、英文名稱) 均不用輸入完整", description="但是因為discord API 的限制，選項至多只能顯示25個，因此建議輸入完整一點，例如: 光賽(O) 光(X)")
            embed5.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259513459683622952/image.png?ex=668bf4d1&is=668aa351&hm=ecfedd9ab6c7349cca23b5c68297691ddeedf0641647e1cb11eb181ae3f70df3&=&format=webp&quality=lossless")
            
            embed6 = discord.Embed(title="5. 重複 4. 直到選完三個英雄")
            embed6.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259517164470145114/image.png?ex=668bf844&is=668aa6c4&hm=f214d4902a43336cd6b0d772c26188ce625596518ba783e6fb04221717cf575a&=&format=webp&quality=lossless&width=550&height=33")
            
            embed7 = discord.Embed(title="6. 按下鍵盤Enter鍵 或 手機的送出鍵 得到解陣陣容")
            embed7.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259517263531479140/image.png?ex=668bf85c&is=668aa6dc&hm=90694c256d238009a140ed3661872cfdc2ef6e8ded5dc551016776301e87b1d6&=&format=webp&quality=lossless&width=486&height=671")
            
            embed8 = discord.Embed(title="7-1. 錯誤訊息: 重複選擇")
            embed8.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259675328125603840/2024-07-07_225056.png?ex=668c8b91&is=668b3a11&hm=f1d9b80ea040ef91df0416bf50b7b086fe56b1254a00a238cc304245a83dd32b&=&format=webp&quality=lossless")
            
            embed9 = discord.Embed(title="7-2. 錯誤訊息: 直接輸入(沒有選擇)")
            embed9.set_image(url="https://media.discordapp.net/attachments/1259512583623278673/1259675328318804070/2024-07-07_225214.png?ex=668c8b91&is=668b3a11&hm=5e30c8f751d08860194a84cc3283db5118f08610be540ab3031afb158ee37fb0&=&format=webp&quality=lossless")
            
            embed10 = discord.Embed(title="8. 注意事項")
            embed10.add_field(name="a. 不能選擇重複的角色，bot會回傳錯誤訊息。", value="", inline=False)
            embed10.add_field(name="b. 三個選項都要選，不能空著。", value="", inline=False)
            embed10.add_field(name="c. 僅支援繁體中文與英文", value="", inline=False)
            embed10.add_field(name="d. 不支援同音不同字的搜尋，如: 光賽納(X) 光賽娜(O)，請特別注意。", value="", inline=False)
            embed10.add_field(name="e. 這個指令(/solve_gvg) 只能在 <#1256260728894001193> 使用。", value="", inline=False)
            embed10.add_field(name="f. 此bot是基於此網頁 https://fribbels.github.io/e7/gw-meta.html", value="", inline=False)
            
            await interaction.response.send_message(embeds=(embed1, embed2, embed3, embed4, embed5, embed6, embed7, embed8, embed9, embed10))
        except Exception as e :
            await interaction.response.send_message(e)
            
    @app_commands.command(
        name="update_info",
        description="更新英雄資訊"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"])
    async def update_info(self, interaction) :
        await interaction.response.defer()
        
        async with aiohttp.ClientSession() as session :
            async with session.get("https://raw.githubusercontent.com/Lyuuwu/EpicSeven-bot/master/EpicSeven/data/GvgSolver/info.json") as r :
                try :
                    if r.status == 200 :
                        self.info = await r.json(content_type='text/plain', encoding="utf-8")
                    else :
                        await interaction.followup.send("發生錯誤! 請再試一次 >.<")
                        return
                except Exception as e :
                    await interaction.followup.send(e)
                    
            async with session.get("https://raw.githubusercontent.com/Lyuuwu/EpicSeven-bot/master/EpicSeven/data/GvgSolver/name-to-code.json") as r :
                try :
                    if r.status == 200 :
                        self.name_dic = await r.json(content_type='text/plain', encoding='utf-8')
                    else :
                        await interaction.followup.send("發生錯誤! 請再試一次 >.<")
                        return
                except Exception as e :
                    await interaction.followup.send(e)
                        
        await interaction.followup.send("更新完成!")
    
async def setup(bot) :
    await bot.add_cog(GvgSolver(bot), guilds=[discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])