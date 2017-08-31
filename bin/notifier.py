#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 22:44:06 2017

@author: dboudeau
"""
import datetime
import os,logging
from pushbullet import Pushbullet

# Init vars
SERVER_NAME=os.environ['SERVER_NAME']
key_pushbullet=os.environ['KEY_PUSHBULLET']

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def notify(title='Default Title',text='Default Text'):
    global pb
    pb=Pushbullet(key_pushbullet)
    
    if(SERVER_NAME!='MBP-David-'):
        try:
            pb.push_note('['+title+']',"At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))+"\n"+text)
        except Exception as e:
            logger.error('Pushbullet Error '+str(e))
    else:
        logger.debug('['+title+']'+ "At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))+" (server time)\n"+text)
