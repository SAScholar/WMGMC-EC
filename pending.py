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
TargetGroup = int(TargetGroup)
ReviewGroup = int(ReviewGroup)

def getPageUpdates():
    api = 'https://meta.wikimedia.org/w/api.php?action=query&format=json&list=recentchanges&formatversion=2&rcprop=title%7Ctimestamp%7Cids%7Cuser&rctoponly=1&rctitle={}'.format(TargetPage)
    response = requests.get(api)
    data = response.json()
    with open("dump.json", "r") as dump:
        jsondata = json.load(dump)
    if data["query"]["recentchanges"][0]["revid"] == jsondata["lastRequest"]:
        return False
    else:
        jsondata["lastRequest"] = data["query"]["recentchanges"][0]["revid"]
        with open("dump.json", "w") as dump:
            json.dump(jsondata, dump)
        return data["query"]["recentchanges"][0]["user"]

async def notifyReviewer(username):
    timestamp = int(time.time())
    with open ("dump.json", "r") as dump:
        jsondata = json.load(dump)
    abc = jsondata["pending"]
    lena = len(abc) - 1
    length = range(0, lena)
    messages = await app.send_poll(chat_id=ReviewGroup, question="{username}有意加入本用户组，您认为如何？".format(username=username), options=["赞成", "反对"], is_anonymous=False)
    id = messages.id
    jsondata["pending"].append({"user": username, "timestamp": timestamp, "pollid": id})
    with open("dump.json", "w") as dump:
        json.dump(jsondata, dump)

async def stopPoll():
    with open("dump.json", "r") as dump:
        jsondata = json.load(dump)
    abc = jsondata["pending"]
    lena = len(abc) - 1
    length = range(0, lena)
    for i in length:
        if jsondata["pending"][i]:
            if jsondata["pending"][i]["timestamp"] + 259200 < int(time.time()):
                del jsondata["pending"][i]
                await app.stop_poll(chat_id=ReviewGroup, message_id=jsondata["pending"][i]["pollid"])
                await app.send_message(chat_id=ReviewGroup, text="投票已结束，请求管理员点票。", reply_to_message_id = jsondata["pending"][i]["pollid"])
                with open("dump.json", "w") as dump:
                    json.dump(jsondata, dump)
            else:
                print("No need")
        else:
            print("No need")

async def main():
    async with app:
        while True:
            update = getPageUpdates()
            if update:
                await notifyReviewer(update)
                print("updated")
            else:
                await stopPoll()
                print("else")
                time.sleep(10)

app.run(main())