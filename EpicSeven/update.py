import os
import zipfile
import shutil
import aiohttp
import asyncio
import subprocess
import json

async def download_file(session : aiohttp.ClientSession, url : str, target_path : str) :
    async with session.get(url) as r :
        try :
            with open(target_path, "wb") as f :
                while True :
                    chunk = await r.content.read(1024)
                    if not chunk :
                        break
                    f.write(chunk)
        except Exception as e :
            print(e)

async def download_and_extract_zip(url, target_dir) :
    async with aiohttp.ClientSession() as session :
        zip_file_path = os.path.join(target_dir, "patch.zip")
        await download_file(session, url, zip_file_path)
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref :
        zip_ref.extractall(target_dir)
    
    os.remove(zip_file_path)

def install_requirements(requirements_file) :
    subprocess.run(["pip", "install", "-r", requirements_file])

async def update_files(update_json_path, patch_path) :
    with open(update_json_path, 'r') as f :
        files_to_update = json.load(f)
        
    for item in files_to_update :
        source = os.path.join(patch_path, item["path"])
        des = os.path.join(os.getcwd(), "EpicSeven", item["path"])
        
        if item["type"] == "directory" :
            if os.path.exists(des) :
                shutil.rmtree(des)
            shutil.copytree(source, des)
        else :
            if os.path.exists(des) :
                os.remove(des)
            shutil.copy2(source, des)

async def update_bot() :
    try :
        github_zip_url = 'https://github.com/Lyuuwu/EpicSeven-bot/raw/master/EpicSeven/patch.zip'
        target_dir = os.path.join(os.getcwd(), "EpicSeven")
        patch_path = os.path.join(target_dir, 'patch')
        
        check = await download_and_extract_zip(github_zip_url, target_dir)
        
        if check != 0 :
            return check
        
        json_file = os.path.join(patch_path, "update.json")
        await update_files(json_file, patch_path)
        
        requirements_file = os.path.join(patch_path, "requirements.txt")
        if os.path.exists(requirements_file) :
            install_requirements(requirements_file)
        
        if os.path.exists(patch_path) :
            shutil.rmtree(patch_path)
    except Exception as e :
        print(e)
        
if __name__ == "__main__" :
    asyncio.run(update_bot())
