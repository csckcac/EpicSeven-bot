from discord.ext import commands
import json
import aiofiles

class Cog_Extension(commands.Cog) :
    def __init__(self, bot) :
        self.bot = bot
        
    async def load_json(self, file_path) :
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f :
            return json.loads(await f.read())
    
    async def save_json(self, file_path, data) :
        async with aiofiles.open(file_path, mode='w', encoding="utf-8") as f :
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))