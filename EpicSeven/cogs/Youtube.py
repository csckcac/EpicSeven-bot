import discord
import scrapetube
import json
from discord.ext import commands, tasks
from core.classes import Cog_Extension

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

class Youtube(Cog_Extension):
  def __init__(self, bot):
    self.bot = bot
    self.channels = {
      "第七史詩": "https://youtube.com/@EpicSevenTW"
    }
    self.videos = {}
    self.discord_channel = setdata["YouTube-Notification-Channel"]

  # Cog開始運行的時候 執行check()
  @commands.Cog.listener()
  async def on_ready(self):
    await self.check.start()

  # 偵測新影片
  @tasks.loop(seconds=20)
  async def check(self):
    channel_name = "第七史詩"
    video_ids = []
    video_titles = []
    
    # 第一次運行的時候 抓前20部影片 預防scrapetube錯誤
    if not self.videos :
      videos = scrapetube.get_channel(channel_url=self.channels[channel_name],limit=20)
    else :
      videos = scrapetube.get_channel(channel_url=self.channels[channel_name],limit=10)
    
    # 將獲取的影片資訊 存下來
    # 存影片的 ID 與 TITLE
    for video in videos:
      video_ids.append(video['videoId'])
      video_titles.append(video['title']['runs'][0]['text'])
    
    # 如果是第一次運行 將self.videos初始化
    if not self.videos :
      self.videos[channel_name] = video_ids
    
    # 檢查有沒有新影片
    for i in range(0, len(video_ids)):
      # 沒有紀錄過的ID就是新影片
      if not (video_ids[i] in self.videos[channel_name]) :
        await new_video(self, video_ids[i], video_titles[i], channel_name)

async def new_video(self, video_id, video_title, channel_name):
  # 新影片的url
  url = f"https://youtu.be/{video_id}"
  
  for channel_id in self.discord_channel :
    # discord訊息頻道
    discord.channel = self.bot.get_channel(channel_id)

    # 透過關鍵字來選擇回應的文字
    if "合作" in video_title:
      await discord.channel.send(f"**{channel_name}**有新的合作資訊!!!\n{url}")
    elif "更新" in video_title:
      await discord.channel.send(f"**{channel_name}**有新的更新資訊!!!\n{url}")
    elif "預告" in video_title:
      await discord.channel.send(f"**{channel_name}**有新的英雄資訊!!!\n{url}")
    elif "造型" in video_title :
      await discord.channel.send(f"**{channel_name}**有新的造型資訊!!!\n{url}")
    elif "特！級！信！件！" in video_title or "特級信件" in video_title:
      await discord.channel.send(f"**{channel_name}**有新的特級信件!!!\n{url}")
  
  # 將此影片記錄到self.videos[]中
  self.videos[channel_name].append(video_id)

async def setup(bot):
  await bot.add_cog(Youtube(bot))