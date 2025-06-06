import discord
import json
import random
from discord.ext import commands
from discord import app_commands
from core.classes import Cog_Extension

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

class Draw_img(Cog_Extension) :
    def __init__(self, bot):
        super().__init__(bot=bot)
        self.file = "EpicSeven/data/Draw_img/image.json"
        self.log = "EpicSeven/data/Draw_img/log.json"

    @app_commands.command(
        name = "draw",
        description = "抽老婆",
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
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
    
    @app_commands.command(
        name = "add_image",
        description = "加圖片 多個連結請以空格分開 連結不要用pixiv的",
    )
    @app_commands.describe(image_links="圖片連結 多個連結請以空格隔開 (目前技術不足 無法用pixiv的圖片)")
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
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

    @app_commands.command(
        name = "remove_image",
        description = "將圖片從bot中移除 多個連結請以空格分開",
    )
    @app_commands.describe(image_links="圖片連結 多個連結請以空格隔開")
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def remove(self, interaction, image_links : str) :
        await interaction.response.defer()
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
            return
        
        await interaction.followup.send("刪除完畢!")
    
    @app_commands.command(
        name="check_image_num",
        description="查詢圖庫中圖片的數量"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def check(self, interaction) :
        await interaction.response.defer()
        images_data = await self.load_json(self.file)
        await interaction.followup.send(f"現在圖庫總共有 {len(images_data['images'])} 張圖片")

    @app_commands.command(
        name="check_image_drawn_num",
        description="查詢已抽過圖片的數量"
    )
    @app_commands.guilds(setdata["Discord-Server-Id"]["main"], setdata["Discord-Server-Id"]["test"])
    async def check_drawn(self, interaction) :
        await interaction.response.defer()
        logs = await self.load_json(self.log)
        await interaction.followup.send(f"現在已經抽了 {len(logs['images'])} 張圖片")

async def setup(bot):
  await bot.add_cog(Draw_img(bot), guilds = [discord.Object(id = setdata["Discord-Server-Id"]["main"]), discord.Object(id = setdata["Discord-Server-Id"]["test"])])