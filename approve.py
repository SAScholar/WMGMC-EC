import re
import time
import os
import json
import requests
import asyncio
from pyrogram import Client, filters, utils, idle
from mwbot import Bot
from config import *
import logging
logging.basicConfig(level=logging.INFO)

app = Client("ec", api_id=APID, api_hash=APIPASSWD, bot_token=Token)
bot = Bot(
        sitename="meta.wikimedia", # 替换为你所在的Wiki名，便于参考
        api="https://meta.wikimedia.org/w/api.php", # 替换为对应Wiki的api.php路径
        index="https://meta.wikimedia.org/wiki/Main_Page", #替换为对应Wiki的index.php路径
        username=Botusername,
        password=Botpassword)
TargetGroup = int(TargetGroup)
ReviewGroup = int(ReviewGroup)

async def getInviteLink(username):
    response = await bot.create_chat_invite_link(chat_id=TargetGroup, name=username, member_limit=1)
    return response.invite_link

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Bot is running.")

@app.on_message(filters.command("approve"))
async def approve(client, message):
    pattern = r'/approve(.*?)(?=\n|$)'
    matches = re.findall(pattern, message.text, re.DOTALL)
    matches = [match.strip() for match in matches]
    if message.from_user == JudegeUser:
        username = matches
        invitelink = getInviteLink(username)
        csrf = bot.fetch_token(csrf)
        emailPayload = {
            "action": "emailuser",
            "format": "json",
            "target": username,
            "subject": "您的加入申请已被批准",
            "text": f"如题，我谨代表中国大陆维基媒体用户组理事会，批准您的入组申请。感谢您的耐心等待和对我们的支持，如果您有Telegram账户，还可以加入我们的Telegram群组，加入链接附在文末，再次感谢您的耐心等待！%0A{invitelink}",
            "ccme": "1",
            "token": csrf,
            "formatversion": "2"
        }
        requests.post("https://meta.wikimedia.org/w/api.php", params=emailPayload)
        await message.reply("已批准。")
    elif message.from_user != JudegeUser:
        await message.reply("您没有权限执行此操作。")
    else:
        await message.reply("未知错误。")
        print("未知错误。")

app.run()
