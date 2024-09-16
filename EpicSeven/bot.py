import discord
import asyncio
import os
import json
import time
from discord.ext import commands

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

Activity = discord.Activity(
    name = f"宇宙神遊 - 第七史詩",
    type = discord.ActivityType.playing,
    details = f"現在版本: {setdata['version']}",
)
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), activity=Activity)

async def load_cog():
    for filename in os.listdir("EpicSeven/cogs") :
        if filename.endswith(".py") :
            try:
                await bot.reload_extension(f"cogs.{filename[:-3]}")
                print(f"Reload {filename[:-3]} successfully!")
            except commands.ExtensionNotLoaded :
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Load {filename[:-3]} successfully!")

def is_author() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return commands.check(predicate)

@bot.command(help = "將指定的Cog載入")
@is_author()
async def load(ctx, extension) :
    try :
        if extension.endswith(".py") :
            extension = extension[:-3]

        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Load {extension} done.") 
    except Exception as e :
        await ctx.send(e)

@bot.command(help = "將特定的Cog卸載")
@is_author()
async def unload(ctx, extension) :
    try :
        if extension.endswith(".py") :
            extension = extension[:-3]

        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Unload {extension} done.")
    except Exception as e :
        await ctx.send(e)

@bot.command(help = "將特定的Cog重新載入")
@is_author()
async def reload(ctx, extension) :
    try :
        if extension.endswith(".py") :
            extension = extension[:-3]

        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Reload {extension} done.")
    
    except Exception as e :
        await ctx.send(e)

@bot.command(help = "將所有的Cog重新載入")
@is_author()
async def reload_all(ctx) :
    try :
        await load_cog()
        await ctx.send("reload_all done")
    except Exception as e :
        await ctx.send(e)
        
@bot.command(help = "將bot關閉")
@is_author()
async def quit(ctx) :
    try :
        await ctx.send("bot已下線")
        print(f"{RED}使用指令下線{RESET}")
        await ctx.bot.close()
    except Exception as e :
        await ctx.send(e)

@bot.event
async def on_ready():
    print(f"{GREEN}目前登入身份 --> {bot.user}{RESET}")

@bot.event
async def on_connect() :
    print(f"{GREEN}BOT 已連線{RESET}")

@bot.event
async def on_disconnect() :
    print(f"{RED}BOT 已斷線{RESET}")
    
async def main():
    async with bot:
        await load_cog()
        try:
            await bot.start(setdata["TOKEN-TEST"])
        except discord.errors.LoginFailure:
            print(f"{RED}登錄失敗：請檢查您的 TOKEN 是否正確{RESET}")
        except discord.errors.HTTPException as e:
            print(f"{RED}HTTP 錯誤：無法連接到 Discord 服務器 (錯誤代碼: {e.status}){RESET}")
        except asyncio.exceptions.TimeoutError:
            print(f"{RED}連接超時：無法在指定時間內連接到 Discord 服務器{RESET}")
        except Exception as e:
            print(f"{RED}發生未知錯誤：{str(e)}{RESET}")
        finally:
            if bot.is_closed():
                print(f"{RED}BOT 已關閉{RESET}")
        

if __name__ == "__main__":
    asyncio.run(main())