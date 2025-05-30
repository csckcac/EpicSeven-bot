import discord
from discord import app_commands
from discord.ext import commands
import json
import aiofiles
import aiosqlite
import os
import asyncio
from core.classes import Cog_Extension
from core.Hero import Hero

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as f :
    setdata = json.load(f)

db_path = 'EpicSeven/data/GvGData/data.db'
user_log_path = 'EpicSeven/data/GvGData/user_log.json'

# turn list to str for display in embed message
def make_team(info, heroses):
    return "  ".join(f"<:{hero}:{info[hero]['IconId']}> {info[hero]['DisplayName']}" for hero in heroses if hero)

# check input if is valid
def input_checker(*args):
    try:
        nums = list(map(int, args))
        if any(x < 0 for x in nums):
            return 0
        return 1
    except ValueError:
        return -1

class ManageModal(discord.ui.Modal):
    def __init__(self,def_team : str,
                 atk_team : str,
                 embed : discord.Embed,
                 user_log : dict,
                 UserLogLock : asyncio.Lock, DBLock : asyncio.Lock,
                 msg : discord.Interaction,
                 title : str):
        super().__init__(title=title)
        
        # input field (3 textinput)
        self.add_item(discord.ui.TextInput(
            label="勝利場數",
            placeholder="請輸入愈增加或刪除的場數",
            custom_id="w",
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="平手場數",
            placeholder="請輸入愈增加或刪除的場數",
            custom_id="t",
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="戰敗場數",
            placeholder="請輸入愈增加或刪除的場數",
            custom_id="l",
            required=True
        ))
        self.def_team = def_team
        self.atk_team = atk_team
        self.embed = embed
        self.embed.title = "操作報告"
        self.user_log = user_log
        self.UserLogLock = UserLogLock
        self.DBLock = DBLock
        self.msg = msg

    # fetch input
    def GetNum(self) :
        for child in self.children :
            if child.custom_id == 'w':
                w_cnt = child.value
            elif child.custom_id == 't':
                t_cnt = child.value
            else:
                l_cnt = child.value
        return w_cnt, t_cnt, l_cnt

# add data
class ModifyModal(ManageModal) :
    def __init__(self, def_team: str, atk_team: str, embed : discord.Embed, user_log : dict, UserLogLock : asyncio.Lock, DBLock : asyncio.Lock, msg: discord.Interaction):
        super().__init__(def_team, atk_team, embed, user_log, UserLogLock, DBLock, msg, title="請輸入欲增加的場數")
    
    async def on_submit(self, interaction: discord.Interaction):
        # fetch input
        w_cnt, t_cnt, l_cnt = self.GetNum()
        res = input_checker(w_cnt, t_cnt, l_cnt)

        # error detect
        if res == -1:
            await interaction.response.send_message("輸入只能是整數!", ephemeral=True)
            return
        elif res == 0:
            await interaction.response.send_message("輸入不能是負數!", ephemeral=True)
            return
        
        async with self.DBLock:
            async with aiosqlite.connect(db_path) as db:
                # update db
                async with db.execute(
                    '''
                    INSERT INTO items (def, atk, w, t, l)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(def, atk) DO UPDATE SET
                        w = w + excluded.w,
                        t = t + excluded.t,
                        l = l + excluded.l
                    RETURNING w, t, l
                    ''', (self.def_team, self.atk_team, w_cnt, t_cnt, l_cnt)) as cursor:
                    row = await cursor.fetchone()
                await db.commit()
                        
        id = str(self.msg.user.id)
        team = self.def_team + ',' + self.atk_team
        if id not in self.user_log :
            self.user_log[id] = {}
        if team not in self.user_log[id]:
            self.user_log[id][team] = [int(w_cnt), int(t_cnt), int(l_cnt)]
        else:
            self.user_log[id][team] = [x + y for x, y in zip(self.user_log[id][team], [int(w_cnt), int(t_cnt), int(l_cnt)])]
        
        async with self.UserLogLock:
            async with aiofiles.open(user_log_path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(self.user_log, ensure_ascii=False, indent=4))
        
        # send operation report to user
              
        w_new, t_new, l_new = row
        self.embed.add_field(name="", value="\u200B", inline=False)
        self.embed.add_field(name="增加數值 : ", value=f"勝利:{w_cnt}, 平手:{t_cnt}, 戰敗:{l_cnt}", inline=False)
        self.embed.add_field(name="操作結果 : ", value=f"勝利:{w_new}, 平手:{t_new}, 戰敗:{l_new}", inline=False)
        
        await self.msg.delete_original_response()
        await interaction.response.send_message(embed=self.embed, ephemeral=True)

# for delete data
class DeleteModal(ManageModal):
    def __init__(self, def_team: str, atk_team: str, embed : discord.Embed, user_log : dict, UserLogLock : asyncio.Lock, DBLock : asyncio.Lock, msg: discord.Interaction):
        super().__init__(def_team, atk_team, embed, user_log, UserLogLock, DBLock, msg, title="請輸入欲刪除的場數")
    
    async def on_submit(self, interaction: discord.Interaction):
        # fetch input
        w_cnt, t_cnt, l_cnt = self.GetNum()
        res = input_checker(w_cnt, t_cnt, l_cnt)
        
        # error detect
        if res == -1:
            await interaction.response.send_message("輸入只能是整數!", ephemeral=True)
            return
        elif res == 0:
            await interaction.response.send_message("輸入不能是負數!", ephemeral=True)
            return 

        # for updating user's log
        team = self.def_team + ',' + self.atk_team
        id = str(self.msg.user.id)

        # user has no modify log or user has deleted
        if (
            (self.user_log is None) or
            (id not in self.user_log) or
            (team not in self.user_log[id]) or
            (sum(self.user_log[id][team]) == 0)
        ):
            await interaction.response.send_message("沒有紀錄可以刪減", ephemeral=True)
            return

        # if the input is bigger than use's total update, then choose the smaller one (not allow user delete too much data)
        w_cnt, t_cnt, l_cnt = [str(min(x, y)) for x, y in zip(self.user_log[id][team], [int(w_cnt), int(t_cnt), int(l_cnt)])]
        
        async with self.DBLock:
            async with aiosqlite.connect(db_path) as db:
                # update db
                async with db.execute(
                    '''
                    UPDATE items
                    SET w = w - ?, t = t- ?, l = l -?
                    WHERE def = ? AND atk = ?
                    RETURNING w, t, l
                    ''', (w_cnt, t_cnt, l_cnt, self.def_team, self.atk_team)) as cursor:
                    row = await cursor.fetchone()   
        
        # build/update log
        self.user_log[id][team] = [x - y for x, y in zip(self.user_log[id][team], [int(w_cnt), int(t_cnt), int(l_cnt)])]
        
        async with self.UserLogLock:
            async with aiofiles.open(user_log_path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(self.user_log, ensure_ascii=False, indent=4))
        
        # send operation report to user    
        w_new, t_new, l_new = row
        self.embed.add_field(name="", value="\u200B", inline=False)
        self.embed.add_field(name="刪減數值 : ", value=f"勝利:{w_cnt}, 平手:{t_cnt}, 戰敗:{l_cnt}", inline=False)
        self.embed.add_field(name="操作結果 : ", value=f"勝利:{w_new}, 平手:{t_new}, 戰敗:{l_new}", inline=False)
        
        await self.msg.delete_original_response()
        await interaction.response.send_message(embed=self.embed, ephemeral=True)

class ManageView(discord.ui.View):
    def __init__(self, def_team : str, atk_team : str, embed : discord.Embed, user_log : dict, UserLogLock : asyncio.Lock, DBLock : asyncio.Lock) :
        super().__init__(timeout=180)
        self.def_team = def_team
        self.atk_team = atk_team
        self.embed = embed
        self.user_log = user_log
        self.UserLogLock = UserLogLock
        self.DBLock = DBLock

    # button for increasing data
    @discord.ui.button(label="增加數據", style=discord.ButtonStyle.primary)
    async def modify(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_modal(ModifyModal(
            def_team=self.def_team,
            atk_team=self.atk_team,
            embed=self.embed,
            user_log=self.user_log,
            UserLogLock=self.UserLogLock,
            DBLock=self.DBLock,
            msg=interaction
        ))

    # button for decreasing data
    @discord.ui.button(label="刪除數據", style=discord.ButtonStyle.red)
    async def delete(self, interaction : discord.Interaction, button : discord.ui.Button):
        await interaction.response.send_modal(DeleteModal(
            def_team=self.def_team,
            atk_team=self.atk_team,
            embed=self.embed,
            user_log=self.user_log,
            UserLogLock=self.UserLogLock,
            DBLock=self.DBLock,
            msg=interaction
        ))

class GvGDataManager(Cog_Extension, Hero):
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.UserLogJsonLock = asyncio.Lock()
        self.DBLock = asyncio.Lock()
        self.user_log = {}

    async def cog_load(self):
        # load user_log        
        self.user_log = await self.load_json(user_log_path)
        if self.user_log is None:
            self.user_log = {}
        
        # init database if not exist
        async with aiosqlite.connect(db_path) as db :
            await db.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    def TEXT,
                    atk TEXT,
                    w INTEGER,
                    t INTEGER,
                    l INTEGER,
                    UNIQUE(def, atk)
                )
            ''')
            await db.commit()
        
    @app_commands.command(description="編輯資料庫",)
    @app_commands.describe(
        def_hero1 = "**選擇** 敵方防守英雄",
        def_hero2 = "**選擇** 敵方防守英雄",
        def_hero3 = "**選擇** 敵方防守英雄",

        atk_hero1 = "**選擇** 我方進攻英雄",
        atk_hero2 = "**選擇** 我方進攻英雄",
        atk_hero3 = "**選擇** 我方進攻英雄"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    @app_commands.autocomplete(
        def_hero1 = Hero.SelectHero,
        def_hero2 = Hero.SelectHero,
        def_hero3 = Hero.SelectHero,

        atk_hero1 = Hero.SelectHero,
        atk_hero2 = Hero.SelectHero,
        atk_hero3 = Hero.SelectHero
    )
    async def manage(self, interaction : discord.Interaction,
                     def_hero1 : str, def_hero2 : str, def_hero3 : str,
                     atk_hero1 : str, atk_hero2 : str, atk_hero3 : str
                    ):
        
        # error detect
        if len({def_hero1, def_hero2, def_hero3}) < 3 :
            await interaction.response.send_message("防守隊伍有重複選角")
            return
        if len({atk_hero1, atk_hero2, atk_hero3}) < 3 :
            await interaction.response.send_message("進攻隊伍有重複選角")
            return
        if (def_hero1 not in self.info) or (def_hero2 not in self.info) or (def_hero3 not in self.info) \
        or (atk_hero1 not in self.info) or (atk_hero2 not in self.info) or (atk_hero3 not in self.info):
            await interaction.response.send_message("發生錯誤!! 請再試一次! 請注意要從選項中選取")
            return

        # sort and makee str
        def_heroes = sorted([def_hero1, def_hero2, def_hero3])
        atk_heroes = sorted([atk_hero1, atk_hero2, atk_hero3])
        def_team = ','.join(hero for hero in def_heroes)
        atk_team = ','.join(hero for hero in atk_heroes)
        
        #build embed message
        embed = discord.Embed(title=f"操作介面")
        embed.add_field(name="", value="\u200B", inline=False)
        embed.add_field(name=f"防守陣容 :  {make_team(self.info, def_heroes)}", value="\u200B", inline=False)
        embed.add_field(name=f"進攻陣容 :  {make_team(self.info, atk_heroes)}", value="\u200B", inline=False)

        await interaction.response.send_message(
            embed=embed,
            view=ManageView(def_team=def_team, atk_team=atk_team, embed=embed, user_log=self.user_log, UserLogLock=self.UserLogJsonLock, DBLock=self.DBLock),
            ephemeral=True
        )
    
    # get attack teams based on defend team
    # let other Cog to acquire team
    async def GetData(self, hero1:str, hero2:str, hero3:str):
        teams = {"data":{}}
        def_heroes = sorted([hero1, hero2, hero3])
        def_team = ','.join(hero for hero in def_heroes)
        
        async with self.DBLock:
            async with aiosqlite.connect(db_path) as db:
                async with db.execute('SELECT atk, w, t, l FROM items WHERE def = ?', (def_team,)) as cursor:
                    async for atk, w, t, l in cursor:
                        teams["data"][atk] = {"w":int(w), "d":int(t), "l":int(l)}
        return teams

async def setup(bot : commands.Bot):
    await bot.add_cog(GvGDataManager(bot), guilds=[discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])
