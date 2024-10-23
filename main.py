import os
import time
import pythontelegrambot
import mwparserfromhell
import requests
import mysql.connector
from telegram import (Update,
    Poll,
    ParseMode)
from telegram.ext import (ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    PollHandler)
from config import (
    token,
    targetid,
    confirmuserid,
    botun,
    botpass,
    dbun,
    dbpass
)

waitingcheck = "https://meta.wikimedia.org/w/api.php?action=query&format=json&prop=revisions&titles=Wikimedian's_Group_of_Mainland_China/New&formatversion=2"
waitingclist = requests.get(waitingcheck)
waitinglist = waitingclist.json()
revid = waitinglist["query"]["pages"]["revisions"]["revid"]
connection = mysql.connector.connect(
    host = '',
    user = dbun,
    password = dbpass,
    database = 'wmgmcec'
)
dbCursor = connection.cursor() # New a database cursor
polls = {} # Save the polls status

def check():
    if revid != waitinglist["query"]["pages"]["revisions"]["revid"] :
        revid = waitinglist["query"]["pages"]["revisions"]["revid"]
        return True
    else:
        return False
    
def writeInfomation():
    requester = waitinglist["query"]["pages"]["revisions"]["user"]
    timestamp = waitinglist["query"]["pages"]["revisions"]["timestamp"]
    query = """ INSERT INTO request (username, timestamp, status, telegram)
                           VALUES (%s, %s, %s, %s) """
    insert = (requester, timestamp, 'new', 'none')
    dbCursor.execute(query, insert)
    connection.commit()

async def startPoll(update: Update, context: ContextTypes.DEFAULT_TYPE, username):
    question = '{username}希望加入本组，请问您觉得如何？'.format(username)
    options = ['Support','Oppose']

    message = await context.bot.send_poll(
        chat_id = targetid,
        question = question,
        options = options,
        is_anonymous = False
    )
    polls[message.poll.id] = message.poll
    context.job_queue.run_once(finish, 259200, chat_id=targetid, poll_id=message.poll.id)

async def finish()