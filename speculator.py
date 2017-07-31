#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 22:54:47 2017

@author: dboudeau
"""
import exchange_krakken
import time
import os
from pushbullet import Pushbullet
# Init var
key_pushbullet=os.environ['KEY_PUSHBULLET']
SERVER_NAME=os.environ['SERVER_NAME']

exchange_krakken.init()
list_open_orders=exchange_krakken.get_open_orders_ids()

def notify(title='Default Title',currency='EUR',text='Default Text'):
    global pb
    pb=Pushbullet(key_pushbullet)
    try:
        pb.push_note('['+currency+']'+title, text)
    except :
        print('Pushbullet TimeoutError')
        pb.push_note('['+currency+']'+title, text)

def check_orders():
    global list_open_orders
    fresh_open_orders_list=exchange_krakken.get_open_orders_ids()
    
    for oe in list_open_orders:
        if oe not in fresh_open_orders_list:
            # Get details about closed orders
            closed_orders=exchange_krakken.get_closed_orders()
            coe=closed_orders.get(oe)
            status=str(coe.get('status'))
            descr=str(coe.get('descr'))
            #TODO DISGUSTING
            if(SERVER_NAME!='MBP-David-'):
                notify('Order '+status,oe,descr)
            else:
                print('Order '+status+" "+oe+" "+descr)
    list_open_orders=fresh_open_orders_list
               
while(1==1):
    # Check for closed Orders
    check_orders()
    time.sleep(300)