import time
import schedule
import requests
import json
import re
import mariadb
from config import *

database = mariadb.connect(
    user=dbusername,
    password=dbpassword,
    host = dbhost,
    port = 3306,
    database = dbname
)
dbCur = database.cursor()

waitingcheck = "https://meta.wikimedia.org/w/api.php?action=query&format=json&prop=revisions&titles=Wikimedian's_Group_of_Mainland_China/New&formatversion=2"
waitingclist = requests.get(waitingcheck)
waitinglist = waitingclist.json()
revid = waitinglist["query"]["pages"]["revisions"]["revid"]

def autocheck() -> bool:
    if revid != waitinglist["query"]["pages"]["revisions"]["revid"] :
        revid = waitinglist["query"]["pages"]["revisions"]["revid"]
        return True
    else:
        return False
    
def getInformations() -> str:
    username = waitinglist["query"]["pages"]["revisions"]["user"]
    timestamp = waitinglist["query"]["pages"]["revisions"]["timestamp"]
    return username, timestamp

def writeDB(username, timestamp, pollTime):
    

def sendPoll(username, timestamp):
    time = time.time()
    writeDB(username, timestamp, time)
    api = "https://api.telegram.org/bot{token}/sendPoll".format(token=token)
    paras = {
        'chat_id': targetid,
        'questions': "您是否赞成{username}加入本用户组？".format(username = username),
        'options': json.dumps(['Support','Oppose']),
        'is_anonymous': False
    }
    sentPoll = requests.get(api, params=paras)

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

def requestApprove():
    gapi = 'https://api.telegram.org/bot{token}/getUpdates'.format(token)
    sapi = 'https://api.telegram.org/bot{token}/sendMessage'.format(token)
    grantapi = "https://api.telegram.org/bot{token}/createChatInviteLink"
    toGetUpdates = requests.get(gapi)
    gettingUpdates = toGetUpdates.json()
    getUpdates = gettingUpdates["result"]
    length = (len(getUpdates) - 1)
    match = re.match("^/auth (.+)$", getUpdates[length]["message"]["text"])
    if match:
        if getUpdates[length]["from"]["id"] == confirmuserid:
            who = match.group(1)
            paras = {
                'chat_id' : targetid,
                'text' : '{username}已被批准加入本用户组！'.format(username=who),
                'reply_parameters' : {
                    'message_id' : getUpdates[length]["update_id"]
                }
            }
            messageSent = requests.get(sapi, params=paras)
            print(messageSent)
            payload = {
                'chat_id': targetid,
                'name': who,
                'member_limit' : '1'
            }
            inviteSent = requests.get(grantapi, params=payload)
            invitePreLink = inviteSent.json()
            inviteLink = invitePreLink["invite_link"]
            approve(who, inviteLink)

def dbReader(ids, type):
    pass
    return username

def pollCheck() -> str:
    
    return ids

def stopPoll():
    pass

def main():
    if autocheck() == True:
        sendPoll(getInformations())
    else:
        if pollCheck():
            stopPoll(dbReader(pollCheck(), 'pollID'))
            requestApprove(dbReader(pollCheck(), 'Username'))
            time.sleep(120)
        else:
            print("No more work")
            time.sleep(120)




