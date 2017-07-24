#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 22:14:05 2017

@author: dboudeau
"""

import krakenex
import time
from pushbullet import Pushbullet
import json,requests
import os
# Init parameters
api_key=os.environ['API_KEY']
api_sign=os.environ['API_SIGN']
key_pushbullet=os.environ['KEY_PUSHBULLET']
SERVER_NAME=os.environ['SERVER_NAME']

def init():
    print("(Re)Initializing")
    global k
    global pb
    global c
    time.sleep(15)
    c = krakenex.Connection()
    k= krakenex.api.API(api_key,api_sign,c)
    pb= Pushbullet(key_pushbullet)
    
def notify(title='Default Title',currency='EUR',text='Default Text'):
    global pb
    try:
        pb.push_note('['+currency+']'+title, text)
    except requests.exceptions.ConnectionError:
        init()
        print('Pushbullet TimeoutError')
        pb.push_note('['+currency+']'+title, text)

# Display all position and return position for currency
def balance(currency=""):
    currency_position=0.0
    print("****************")
    for item in k.query_private('Balance').get('result').items():
        # Hide if null
        if(float(item[1])>0):
            print("* "+str(item[0])+" "+str(item[1]))
            if(len(currency)>0 and currency==item[0]):
                currency_position=float(item[1])
    print("****************")
    return currency_position


#def openOrders():
#open_orders =k.query_private('OpenOrders' )
#for item in open_orders.get('result').get('open'):
#    key=str(item)
#    print(open_orders.get('result').get('open').get(key))

def currency_value(currency_separated_by_commas='EOSEUR,XRPEUR'):
    req_data = {'pair': currency_separated_by_commas}
    cur=None
    try:
        cur=k.query_public('Ticker',req_data)
        cur=cur.get('result')
    except json.decoder.JSONDecodeError :
        print('Error Json Decoder')
        cur=None
    except TimeoutError :
        print('To check')
        cur=None
    except ValueError:
        print('To check 2')
        cur=None
    #print("Error occurs")
    return cur
# fail at 970
# fail at 800


# Je veux que l'algorithme surveille mes ordres et les cours, et me backe quand c'est nécessaire

# Ai je des positions ouvertes ?

# Je passe un ordre d'achat

# Y a t il des ordres clos ?

# Si oui sont ils ouverts depuis plus de 2 minutes ?

# Si oui, backer l'ordre.

# Si non,



## Je veux que quand je pose un ordre, sur une descente, je  veux
# savoir quel est le cout minimal pour la revente pour ne pas faire une perte
def test():
    maker_fee=0.16
    quantity=60
    unit_price=2.811
    coast_without_fees=quantity*unit_price
    buying_fees=(coast_without_fees/100)*maker_fee
    
    cent=0.01
    unit_sell_price=0
    step=0
    selling_fees=0
    print(buying_fees)
    while(selling_fees>buying_fees):
        step=step+cent    
        unit_sell_price=unit_price+step
        print(" Testing "+str(unit_sell_price))
        coast_sell_without_fees=quantity*unit_sell_price
        selling_fees=(coast_sell_without_fees/100)*maker_fee
        print(selling_fees)


init()
    #k.query_private('OpenOrders')
    #k.query_private('AddOrder')