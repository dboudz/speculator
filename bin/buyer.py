#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 12:43:52 2017

@author: dboudeau
"""
import persistenceHandler
import numpy as np
import datetime
from dateutil import parser
from configobj import ConfigObj
import krakenex_dev
import sys
import pandas
import time

# Init parameters
config = config = ConfigObj('./config')
SEEKING_CURRENCIES=config['SEEKING_CURRENCIES']
STEP_WAIT_BUYER=int(config['STEP_WAIT_BUYER'])
STEP_NOTIFY_BUYER=int(config['STEP_NOTIFY_BUYER'])
SHOULD_DRAW=bool(config['SHOULD_DRAW'])
SERVER_NAME=config['SERVER_NAME']
sys.stdout.flush()
    
cmpt=0
#if(1==1):
while(1==1):
    if(cmpt%STEP_NOTIFY_BUYER==0 and cmpt>0):
        krakenex_dev.init()
        krakenex_dev.notify("At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')) ,SERVER_NAME+"BUYER OK","Buyer still on")
    cmpt=cmpt+STEP_WAIT_BUYER
    print(cmpt)
    for currency in (SEEKING_CURRENCIES).split(","):
    
        df_currency=persistenceHandler.getCrawling(currency)
        ts=(df_currency.set_index('currency_date')['ask_price'])

        ma180=pandas.rolling_mean(ts,window=180)
        ma3600=pandas.rolling_mean(ts,window=3600)
        difference= ma3600 - ma180
        buyingsignal=np.sign(difference.shift(1))!=np.sign(difference)
#    
#        if(SHOULD_DRAW==True):
#            ts.plot(color="blue", linewidth=1, linestyle="-",label=currency)
#            ma180.plot(color="red", linewidth=1, linestyle="-",label='MA180')
#            ma3600.plot(color="green", linewidth=1, linestyle="-",label='MA3600')
#            buyingsignal.plot()
            
        momentum=ts.ix[buyingsignal.values == True].index
        values=ts.values[buyingsignal.values == True]
        index=0
                
        while index< len(momentum):
            dt = parser.parse(momentum[index])
            #print(str(currency))
            if(dt.date() >=datetime.datetime.today().date() ):
                nb_record_inserted=persistenceHandler.storeBuyingSignal(dt.strftime("%Y-%m-%d %H:%M:%S"),currency,values[index])
                if(nb_record_inserted>0):
                    krakenex_dev.notify('NEW BUYING SIGNAL',SERVER_NAME+currency,'SOMETHING IS HAPPENING')
            index=index+1
        time.sleep(STEP_WAIT_BUYER)