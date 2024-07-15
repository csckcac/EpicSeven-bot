import discord
import asyncio
import os
import json
from discord.ext import commands

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), activity=discord.Game(name="宇宙神遊 - 第七史詩"))

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
        await ctx.bot.close()
    except Exception as e :
        await ctx.send(e)
        
@bot.command(help = "查看現在bot的版本")
@is_author()
async def version(ctx) :
    try : 
        await ctx.send(f"現在版本是 {setdata['version']}")
    except Exception as e :
        await ctx.send(e)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")

async def main():
    async with bot:
        await load_cog()
        await bot.start(setdata["TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())