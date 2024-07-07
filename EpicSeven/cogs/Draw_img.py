import discord
import json
import random
import aiofiles
from discord.ext import commands
from core.classes import Cog_Extension

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

class Draw_img(Cog_Extension) :
    def __init__(self, bot):
        self.bot = bot
        self.file = "EpicSeven/data/Draw_img/image.json"
        self.log = "EpicSeven/data/Draw_img/log.json"

    async def load_json(self, file_path) :
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f :
            return json.loads(await f.read())
    
    async def save_json(self, file_path, data) :
        async with aiofiles.open(file_path, mode='w', encoding="utf-8") as f :
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    @bot.tree.command(
        name = "draw",
        description = "抽老婆",
        guild = discord.Object(id=setdata["Discord-Server-Id"]["main"])
    )
    async def draw(self, interaction) :
        try :
            await interaction.response.defer()
            # 載入 圖庫&抽取紀錄
            links = await self.load_json(self.file)
            logs = await self.load_json(self.log)

            # 產生亂數
            length = len(links["images"])
            draw_num = random.randint(0, length-1)

            # 直到是沒抽到過的
            while links["images"][draw_num] in logs["images"] :
                draw_num = (draw_num + 1) % length

            # 加到紀錄中
            logs["images"].append(links["images"][draw_num])
            
            # 檢查是否抽過一輪
            reset = False

            # 抽過一輪則把紀錄清空
            if len(logs["images"]) >= length :
                logs["images"] = []
                reset = True
            
            await self.save_json(self.log, logs)

            if reset :
                await interaction.followup.send(f"|| {links['images'][draw_num]} ||\n抽完一輪!! 抽圖記錄重置!!")
            else :
                await interaction.followup.send(f"|| {links['images'][draw_num]} ||")
        except Exception as e :
            await interaction.followup.send(f"發生錯誤 >.< 請再試一次\n{e}")
    
    @bot.tree.command(
        name = "add",
        description = "加圖片 多個連結請以空格分開 連結不要用pixiv的",
        guild = discord.Object(id=setdata["Discord-Server-Id"]["main"])
    )
    async def add(self, interaction, image_links : str) :
        await interaction.response.defer() 
        # 打開圖庫
        images_data = await self.load_json(self.file)

        # 分割圖片連結字串
        links = image_links.split(' ')
        
        # 計算圖片數量 並把圖片加入倒圖庫中
        cnt = 0
        for link in links :
            if link not in images_data["images"] :
                images_data["images"].append(link)
                cnt += 1
        
        # 寫入圖庫
        await self.save_json(self.file, images_data)
        
        await interaction.followup.send(f"{cnt}張圖片加入成功!")

    @bot.tree.command(
        name = "remove",
        description = "將圖片從bot中移除 多個連結請以空格分開",
        guild = discord.Object(id=setdata["Discord-Server-Id"]["main"])
    )
    async def remove(self, interaction, image_links : str) :
        interaction.response.defer()
        # 打開圖庫
        images_data = await self.load_json(self.file)
        
        # 分割圖片連結字串
        links = image_links.split(' ')
        
        not_find = []
        
        for link in links :
            try :
                # 如果連結存在於圖庫 則從圖庫移除
                images_data["images"].remove(link)
            except :
                # 如果連結不存在於圖庫 記錄下此連結
                not_find.append("<" + link + ">")
        
        # 修改圖庫
        await self.save_json(self.file, images_data)

        # 如果有連結不存在 通知使用者連結錯誤
        if not_find :
            await interaction.followup.send(f"刪除完畢!\nbot 沒有找到以下圖片 {not_find} 請檢查連結是否正確")
        
        await interaction.followup.send("刪除完畢!")
    
    @commands.command(help = "查詢圖庫中圖片的數量")
    async def check(self, ctx) :
        images_data = await self.load_json(self.file)
        await ctx.send(f"現在圖庫總共有 {len(images_data['images'])} 張圖片")

    @commands.command(help = "查看已經抽了多少張")
    async def check_drawn(self, ctx) :
        logs = await self.load_json(self.log)
        await ctx.send(f"現在已經抽了 {len(logs['images'])} 張圖片")

async def setup(bot):
  await bot.add_cog(Draw_img(bot), guilds = [discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])