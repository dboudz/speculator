#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 18:48:18 2017

@author: dboudeau
"""

import time
import datetime
import socket,http
import sys,os
import krakenex
import time
import json,requests
import logging

from sqlalchemy import create_engine
import pandas
import numpy as np
from pushbullet import Pushbullet

# Init var
key_pushbullet=os.environ['KEY_PUSHBULLET']
SERVER_NAME=os.environ['SERVER_NAME']

# Init parameters
api_key=os.environ['API_KEY']
api_sign=os.environ['API_SIGN']
SERVER_NAME=os.environ['SERVER_NAME']
DATABASE_URL=os.environ['DATABASE_URL']
FEE_PERCENTAGE=0.16

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


def get_open_orders_ids():
    return list(get_open_orders().keys())

def get_open_orders():
    dict_open_orders=exchange_call(PRIVACY_PRIVATE,'OpenOrders')
    return (dict_open_orders.get('result').get('open'))
        
def get_closed_orders():
    dict_closed_orders=exchange_call(PRIVACY_PRIVATE,'ClosedOrders')
    return (dict_closed_orders.get('result').get('closed'))
  

def cancel_order(order_id):
    req_data={'txid':order_id}
    cancel_order=exchange_call(PRIVACY_PRIVATE,'CancelOrder',req_data)
    return cancel_order
    #{'error': [], 'result': {'count': 1}}
      
def get_currency_ask_price(currency='XXRPZEUR'):
    ask_price=-1.0
    dict_currency_valuation_informations=get_currency_value(currency)
    ask_price=float(dict_currency_valuation_informations.get('result').get(currency).get('a')[0])

    return ask_price


def get_server_unixtime():
    unix_time_integer=-1    
    time_krakken=exchange_call(PRIVACY_PUBLIC,'Time')    
    unix_time_integer=time_krakken.get('result').get('unixtime')
    #Tips for SQL to Timestamp postgres = select to_timestamp(1501523090);
    return unix_time_integer
    
# return (ask_price:float,slope:float)
# If slope + increasing, if slope <0 then decreasing
def get_trend(currency='XXRPZEUR'):
    # Get server time
    unix_time_integer=get_server_unixtime()
    # test increasing
    #unix_time_integer=1501523931
    
    # Get crawled values from 10 last mins
    sql_get_last_minutes_currency_values="""
    select ask_price,currency_date from crawling where 
    currency_date between (to_timestamp("""+str(unix_time_integer)+""") - INTERVAL '10 minutes') and to_timestamp("""+str(unix_time_integer)+""")
    and currency='"""+currency+"""' 
    order by currency_date asc;
    """
    # TODO : PAS NORMAL DE FAIRE CA ICI
    # Init db parameters
    engine = create_engine(DATABASE_URL)    
    conn_crawling = engine.connect()
    df_last_minutes=pandas.read_sql(sql_get_last_minutes_currency_values,conn_crawling)
    ts_last_minutes=(df_last_minutes.set_index('currency_date')['ask_price'])
    
    #http://www.emilkhatib.com/analyzing-trends-in-data-with-pandas/
    coefficients, residuals, _, _, _ = np.polyfit(range(len(ts_last_minutes.index)),ts_last_minutes.values,1,full=True)
    mse = residuals[0]/(len(ts_last_minutes.index))
    nrmse = np.sqrt(mse)/(ts_last_minutes.max() - ts_last_minutes.min())
    logger.info('Slope ' + str(coefficients[0]))
    logger.info('NRMSE: ' + str(nrmse))
    
    #TODO tester plus tard la régression linéaire
    #model = pd.ols(y=ts,x=ts.index,intercept=True)
    return coefficients[0]

def sell(volume,price,currency='XXRPZEUR'):
    req_data = {'pair': currency,'type':'sell','ordertype':'limit','price':price,'volume':volume}
    result=exchange_call(PRIVACY_PRIVATE,'AddOrder',req_data)
    logger.debug(result) 
    return result     

def calculate_minimum_sell_price_to(volume,unit_price,objective=1.0):
    volume=float(volume)
    buy_unit_price=float(unit_price)
    buy_price=round(volume*buy_unit_price,5)
    buy_fee=round((buy_price/100)*FEE_PERCENTAGE,5)
    
    #Init var
    potential_gain=0
    STEP=0.0001
    sell_price=buy_price+(buy_fee*2)
    
    while(potential_gain<objective):
        sell_price=sell_price+STEP
        sell_fee=(sell_price/100)*FEE_PERCENTAGE
        potential_gain=sell_price-buy_price-buy_fee-sell_fee
        #logger.debug('potential_gain :'+str(potential_gain)+' at sell_price :'+str(sell_price))
        
    unit_sell_price=sell_price/volume
    return round(unit_sell_price,5)
   

def buy(volume,price,currency='XXRPZEUR'):
    req_data = {'pair': currency,'type':'buy','ordertype':'limit','price':price,'volume':volume}
    result=exchange_call(PRIVACY_PRIVATE,'AddOrder',req_data)
    logger.debug(result)
    return result
    #{'error': [], 'result': {'descr': {'order': 'buy 100.00000000 XRPEUR @ limit 0.100000'}, 'txid': ['OHLVH2-GYDQ5-YQM6GP']}}

def get_currency_value(currency_separated_by_commas='XXRPZEUR'):
    req_data = {'pair': currency_separated_by_commas}
    cur=exchange_call(PRIVACY_PUBLIC,'Ticker',req_data)
    return cur


def notify(title='Default Title',text='Default Text'):
    global pb
    pb=Pushbullet(key_pushbullet)
    
    #TODO DISGUSTING
    if(SERVER_NAME!='MBP-David-'):
        try:
            pb.push_note('['+title+']'+ "At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))+"\n"+text)
        except Exception as e:
            #TODO
            logger.error('Pushbullet Error '+str(e))
    else:
        logger.debug('['+title+']', "At "+str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'))+"\n"+text)


def check_orders_and_notify_if_closure_detected(list_knowned_open_orders):
    fresh_open_orders_list=get_open_orders_ids()
    
    for oe in list_knowned_open_orders:
        if oe not in fresh_open_orders_list:
            # Get details about closed orders
            closed_orders=get_closed_orders()
            coe=closed_orders.get(oe)
            status=str(coe.get('status'))
            descr=str(coe.get('descr'))
            notify('Order '+status,descr)
    return fresh_open_orders_list


