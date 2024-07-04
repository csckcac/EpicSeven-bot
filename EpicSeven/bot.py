import discord
import asyncio
import os
import json
from discord.ext import commands

with open("EpicSeven/data/BasicSetting/setting.json", encoding="utf-8") as jset :
    setdata = json.load(jset)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

async def load_cog():
    for filename in os.listdir("D:\EpicSeven_bot\EpicSeven\cogs") :
        if filename.endswith(".py") :
            try:
                await bot.reload_extension(f"cogs.{filename[:-3]}")
                print(f"Reload {filename[:-3]} successfully!")
            except commands.ExtensionNotLoaded :
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Load {filename[:-3]} successfully!")

def is_me() :
    def predicate(ctx) :
        return ctx.message.author.id in setdata["Author-Id"]
    return commands.check(predicate)

@bot.command()
@is_me()
async def load(ctx, extension) :
    if extension[-3:] == ".py" :
        extension = extension[:-3]

    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Load {extension} done.")

@bot.command()
@is_me()
async def unload(ctx, extension) :
    if extension[-3:] == ".py" :
        extension = extension[:-3]

    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Unload {extension} done.")

@bot.command()
@is_me()
async def reload(ctx, extension) :
    if extension[-3:] == ".py" :
        extension = extension[:-3]

    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"Reload {extension} done.")

@bot.command()
@is_me()
async def reload_all(ctx) :
    await load_cog()
    await ctx.send("reload_all done")

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")

async def main():
    async with bot:
        await load_cog()
        await bot.start(setdata["TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())