#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 21:07:16 2017

@author: dboudeau
"""

import krakenex_dev
import persistenceHandler
import time
import datetime
import socket,http
from configobj import ConfigObj
import sys

# Init parameters
config = config = ConfigObj('./config')
STEP_WAIT=int(config['STEP_WAIT'])
STEP_NOTIFY=int(config['STEP_NOTIFY'])
CRAWLED_CURRENCIES=config['CRAWLED_CURRENCIES']
SERVER_NAME=config['SERVER_NAME']
sys.stdout.flush()


cmpt=0
while(1==1):
    if(cmpt%STEP_NOTIFY==0 and cmpt>0):
        krakenex_dev.notify("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) ,SERVER_NAME+"CRAWLER OK","Crawler still on")
    cmpt=cmpt+STEP_WAIT
    
    
#    a = ask array(<price>, <whole lot volume>, <lot volume>),
#    b = bid array(<price>, <whole lot volume>, <lot volume>),
#    c = last trade closed array(<price>, <lot volume>),
#    v = volume array(<today>, <last 24 hours>),
#    p = volume weighted average price array(<today>, <last 24 hours>),
#    t = number of trades array(<today>, <last 24 hours>),
#    l = low array(<today>, <last 24 hours>),
#    h = high array(<today>, <last 24 hours>),
#    o = today's opening price
    actual_currencies_value=None    
    try:
        actual_currencies_values=krakenex_dev.currency_value(CRAWLED_CURRENCIES)
    except socket.timeout:
        time.sleep(STEP_WAIT)
        print("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) +" Time out "+"to watch")
        krakenex_dev.init()
    except http.client.CannotSendRequest:
        time.sleep(STEP_WAIT)
        print("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) +" CannotSendRequest "+"to watch")
        krakenex_dev.init()
    except AttributeError:
        time.sleep(STEP_WAIT)
        print("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) +" AttributeError"+"to watch")
        krakenex_dev.init()
    if(actual_currencies_values != None):
        for currency in actual_currencies_values.keys():
            c=actual_currencies_values.get(currency)
            persistenceHandler.storeCurrency(currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
    else:
        print("One currency scrap failed. Trying to reset API ")
        krakenex_dev.init()
        #krakenex_dev.notify("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) ,"API reseted","to watch")

    time.sleep(STEP_WAIT)