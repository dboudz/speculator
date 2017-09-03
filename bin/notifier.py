#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 22:44:06 2017

@author: dboudeau
"""
import datetime
import os,logging
import telepot

# Init vars
SERVER_NAME=os.environ['SERVER_NAME']
KEY_TELEGRAM=os.environ['KEY_TELEGRAM']
CHAT_TELEGRAM=os.environ['CHAT_TELEGRAM']

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

bot = telepot.Bot(KEY_TELEGRAM)


def notify(title='Default Title',text='Default Text'):
    global bot
    
    try:
        bot.sendMessage(CHAT_TELEGRAM, str(SERVER_NAME)+"\n"+str(title)+'\n'+str(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S'))+"\n\n"+text)
    except Exception as e:
        logger.error('Telegram Error '+str(e))