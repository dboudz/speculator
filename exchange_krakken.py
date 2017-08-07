#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 18:48:18 2017

@author: dboudeau
"""

import time
import sys,os
import krakenex
import logging
import notifier


# Init var

SERVER_NAME=os.environ['SERVER_NAME']

# Init parameters
api_key=os.environ['API_KEY']
api_sign=os.environ['API_SIGN']
SERVER_NAME=os.environ['SERVER_NAME']
DATABASE_URL=os.environ['DATABASE_URL']

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


sys.stdout.flush()
krakken_connection=None
PRIVACY_PRIVATE='private'
PRIVACY_PUBLIC='public'
DONE=0
NOT_DONE=1


# TODO SEPARER EXCHANGE ET BUSINESS LOGIC
def exchange_call(privacy,function,parameters={}):
    result=None
    if(privacy==PRIVACY_PRIVATE):
        try:
            result=krakken_connection.query_private(function,parameters)
        except:
            logger.info(function+' private faced an error. Resetting exchange & retrying the request')
            reset()
            result=krakken_connection.query_private(function,parameters)
    if(privacy==PRIVACY_PUBLIC):
        try:
            result=krakken_connection.query_public(function,parameters)
        except:
            logger.info(function+' public faced an error. Resetting exchange & retrying the request')
            reset()
            result=krakken_connection.query_public(function,parameters)
    return result


def init():
    global krakken_connection
    logger.info('Initializing krakken exchange')
    c = krakenex.Connection()
    krakken_connection= krakenex.api.API(api_key,api_sign,c)
    
def reset():
    time.sleep(5)
    init()
    time.sleep(5)

def get_balance_XRP():
    return get_balance_for_currency('XXRP')

def get_balance_EUR():
    return get_balance_for_currency('ZEUR')

def get_balance_for_currency(currency):
    values=exchange_call(PRIVACY_PRIVATE,'Balance')
    for cur in list(values.get('result').keys()):
        if(cur==currency):
            return round(float(values.get('result').get(currency)),3)
        
def get_open_orders_ids():
    return list(get_open_orders().keys())

# return [['id', 'type']]
def get_open_orders_ids_and_type():
    list_open_orders=[]
    dict_open_orders=get_open_orders()
    for orderId in list(dict_open_orders.keys()):
        list_open_orders.append( [orderId,dict_open_orders.get(orderId).get('descr').get('type')])
    return list_open_orders

def get_open_orders():
    dict_open_orders=exchange_call(PRIVACY_PRIVATE,'OpenOrders')
    return (dict_open_orders.get('result').get('open'))
  
def get_open_orders_selling_with_unit_sell_price():
    list_open_orders_with_unit_sell_price=[]
    open_orders=get_open_orders()
    for oe in list(open_orders.keys()):
        oe_currency=open_orders.get(oe).get('descr').get('pair')
        oe_order_type=open_orders.get(oe).get('descr').get('type')
        oe_unit_sell_price=float(open_orders.get(oe).get('descr').get('price'))
        if(oe_currency=='XRPEUR' and oe_order_type=='sell'):
            list_open_orders_with_unit_sell_price.append((oe,oe_unit_sell_price))
    return list_open_orders_with_unit_sell_price

def get_closed_order_volume_by_id(id_order):
    dict_closed_orders=exchange_call(PRIVACY_PRIVATE,'ClosedOrders')
    for oe in list(dict_closed_orders.get('result').get('closed')):
        if(oe==id_order):
            return float(dict_closed_orders.get('result').get('closed').get(oe).get('vol'))
    return 0.0


def get_closed_orders():
    dict_closed_orders=exchange_call(PRIVACY_PRIVATE,'ClosedOrders')
    return (dict_closed_orders.get('result').get('closed'))
  
def cancel_order(order_id):
    req_data={'txid':order_id}
    cancel_order=exchange_call(PRIVACY_PRIVATE,'CancelOrder',req_data)
    logger.debug(cancel_order)
    validation=cancel_order.get('error')
    if(len(validation)>0):
        logger.error("Cancel Order  failed. Exiting")
        return NOT_DONE
    else:
        logger.info("Cancel Order success ")
    return DONE 
    #{'error': [], 'result': {'count': 1}}
      

def get_server_unixtime():
    unix_time_integer=-1    
    time_krakken=exchange_call(PRIVACY_PUBLIC,'Time')    
    unix_time_integer=time_krakken.get('result').get('unixtime')
    #Tips for SQL to Timestamp postgres = select to_timestamp(1501523090);
    return unix_time_integer

def sell(volume,price,currency='XXRPZEUR'):
    req_data = {'pair': currency,'type':'sell','ordertype':'limit','price':price,'volume':volume}
    result=exchange_call(PRIVACY_PRIVATE,'AddOrder',req_data)
    logger.debug(result) 
    
    validation=result.get('error')
    if(len(validation)>0):
        logger.error("Selling Order creation failed. Exiting")
        exit(1)
    else:
        new_selling_order=result.get('result').get('txid')[0]
        logger.info("Selling Order creation success : "+str(new_selling_order))
    return new_selling_order 

def buy(volume,price,currency='XXRPZEUR'):
    req_data = {'pair': currency,'type':'buy','ordertype':'limit','price':price,'volume':volume}
    result=exchange_call(PRIVACY_PRIVATE,'AddOrder',req_data)
    logger.debug(result)
    new_buying_order=''
    
    validation=result.get('error')
    if(len(validation)>0):
        logger.error("Buying Order creation failed. Exiting")
        exit(1)
    else:
        new_buying_order=result.get('result').get('txid')[0]
        logger.info("Buying Order creation success : "+str(new_buying_order))
    return new_buying_order

    logger.debug(result)
    
    #{'error': [], 'result': {'descr': {'order': 'buy 100.00000000 XRPEUR @ limit 0.100000'}, 'txid': ['OHLVH2-GYDQ5-YQM6GP']}}

def get_currency_value(currency_separated_by_commas='XXRPZEUR'):
    req_data = {'pair': currency_separated_by_commas}
    cur=exchange_call(PRIVACY_PUBLIC,'Ticker',req_data)
    return cur
