import time
import schedule
import requests
import json
import re
from pyrogram import Client, filters
from config import *

app = Client(
    "ECBot",
    api_id=api_id, api_hash=api_hash,
    bot_token=token
)

waitingcheck = "https://meta.wikimedia.org/w/api.php?action=query&format=json&prop=revisions&titles=Wikimedian's_Group_of_Mainland_China/New&formatversion=2"
waitingclist = requests.get(waitingcheck)
waitinglist = waitingclist.json()
revid = waitinglist["query"]["pages"][0]["revisions"][0]["revid"]

def autocheck() -> bool:
    global revid
    if revid != waitinglist["query"]["pages"][0]["revisions"][0]["revid"] :
        revid = waitinglist["query"]["pages"][0]["revisions"][0]["revid"]
        return True
    else:
        return False
    
def getInformations() -> str:
    username = waitinglist["query"]["pages"][0]["revisions"][0]["user"]
    timestamp = waitinglist["query"]["pages"][0]["revisions"][0]["timestamp"]
    return username, timestamp

def stopPoll(cid, mid):
    api = 'https://api.telegram.org/bot{token}/stopPoll'.format(token=token)
    payload = {
        'chat_id': cid,
        'message_id': mid
    }
    sent = requests.get(api, params=payload)
    return schedule.CancelJob

def sendPoll(username):
    api = "https://api.telegram.org/bot{token}/sendPoll".format(token=token)
    opt = json.dumps(['Support','Oppose'])
    paras = {
        'chat_id': targetid,
        'question': "您是否赞成{username}加入本用户组？".format(username = username),
        'options': opt,
        'is_anonymous': False
    }
    sentPoll = requests.get(api, params=paras)
    informations = sentPoll.json()
    print(informations)
    schedule.every(3).days.do(stopPoll(informations["result"]["chat"]["id"], informations["result"]["poll"]["id"]))

def approve(username, invitelink):
    session = requests.Session()
    URL = 'https://meta.wikimedia.org/w/api.php'
    paras0 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    resons = session.get(URL, params=paras0)
    data = resons.json()
    loginToken = data['query']['tokens']['logintoken']
    paras1 = {
        "action": "login",
        "lgname": f'{botwpusername}',
        "lgpassword": f'{botwppassword}',
        "lgtoken": loginToken,
        "format": "json"
    }
    resons = session.post(URL, params=paras1)
    paras2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }
    resons = session.get(URL, params=paras2)
    data = resons.json()

    CSRFToken1 = data['query']['tokens']['csrftoken']
    CSRFToken = CSRFToken1.replace('+', '%2B')

    #Finally, we are startting to edit page.
    payload = {
        "action": "edit",
        "title": "Wikimedian's_Group_of_Mainland_China/New",
        "token": CSRFToken,
        "format": "json",
        "section": "1",
        "summary": "Bot: Remove the requests which has been handled.",
        "text": "<!--- 欢迎！请以#~~~~来签名。 --->"
    }
    emailPayload = {
        "action": "emailuser",
        "format": "json",
        "target": username,
        "subject": "您的加入申请已被批准",
        "text": f"如题，我谨代表中国大陆维基媒体用户组理事会，批准您的入组申请。感谢您的耐心等待和对我们的支持，如果您有Telegram账户，还可以加入我们的Telegram群组，加入链接附在文末，再次感谢您的耐心等待！%0A{invitelink}",
        "ccme": "1",
        "token": CSRFToken,
        "formatversion": "2"
    }

@app.on_message(filters.command(["confirm"]))
def requestApprove(client, message):
    sapi = 'https://api.telegram.org/bot{token}/sendMessage'.format(token=token)
    grantapi = "https://api.telegram.org/bot{token}/createChatInviteLink".format(token=token)
    if str(message.from_user.id) == confirmuserid:
        it = message.text.split()[1:]
        who = it[0]
        client.send_message(chat_id=message.chat.id, text=f'根据投票结果，{who}已被批准加入用户组。')
        payload = {
            'chat_id': targetid,
            'name': who,
            'member_limit': '1'
        }
        inviteSent = requests.get(grantapi, params=payload)
        invitePreLink = inviteSent.json()
        inviteLink = invitePreLink.get("invite_link", "")
        approve(who, inviteLink)
    else:
        print("No more command waiting handle")

def main():
    if autocheck() == True:
        sendPoll(getInformations())
    else:
        app.run()
        schedule.run_pending()
        time.sleep(10)

while True:
    main()
