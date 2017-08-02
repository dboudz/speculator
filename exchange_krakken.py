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

# Init parameters
api_key=os.environ['API_KEY']
api_sign=os.environ['API_SIGN']
SERVER_NAME=os.environ['SERVER_NAME']
DATABASE_URL=os.environ['DATABASE_URL']
FEE_PERCENTAGE=0.16

logger = logging.getLogger('EXCHANGE_KRAKKEN')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

sys.stdout.flush()
krakken_connection=None


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
    dict_open_orders={}
    try:
        dict_open_orders=krakken_connection.query_private('OpenOrders')
    except:
        logger.info('get_open_orders : faced an error. Resetting exchange & retrying the request')
        reset()
        dict_open_orders=krakken_connection.query_private('OpenOrders')
    return (dict_open_orders.get('result').get('open'))
        
def get_closed_orders():
    dict_closed_orders={}
    try:
        dict_closed_orders=krakken_connection.query_private('ClosedOrders')
    except:
        logger.info('get_closed_orders : faced an error. Resetting exchange & retrying the request')
        reset()
        dict_closed_orders=krakken_connection.query_private('ClosedOrders')
    return (dict_closed_orders.get('result').get('closed'))
  

def cancel_order(order_id):
    print("todo")
    req_data={'txid':order_id}
    cancel_order=None
    try:
        cancel_order=krakken_connection.query_private('CancelOrder',req_data)
    except:
        logger.info('cancel_order : faced an error. Resetting exchange & retrying the request')
        reset()
        cancel_order=krakken_connection.query_private('CancelOrder',req_data)
    return cancel_order
    #{'error': [], 'result': {'count': 1}}
      
def get_currency_ask_price(currency='XXRPZEUR'):
    ask_price=-1.0
    try:
        dict_currency_valuation_informations=get_currency_value(currency)
        print(dict_currency_valuation_informations)
        ask_price=float(dict_currency_valuation_informations.get(currency).get('a')[0])
    except socket.timeout:
        logger.info('get_currency_ask_price : faced a timeout. Resetting exchange & retrying the request')
        reset()
        dict_currency_valuation_informations=get_currency_value(currency)
        ask_price=float(dict_currency_valuation_informations.get(currency).get('a')[0])
    except http.client.RemoteDisconnected:
        logger.info('get_currency_ask_price : faced a server RemoteDisconnected. Resetting exchange & retrying the request')
        reset()
        dict_currency_valuation_informations=get_currency_value(currency)
        ask_price=float(dict_currency_valuation_informations.get(currency).get('a')[0])

    return ask_price


def get_server_unixtime():
    unix_time_integer=-1
    try:
        time_krakken=krakken_connection.query_public('Time')
    except:
        logger.info('get_server_time : faced an error.Resetting connector')
        reset()
        time_krakken=krakken_connection.query_public('Time')
    
    unix_time_integer=time_krakken.get('result').get('unixtime')
    #SQL to Timestamp postgres = select to_timestamp(1501523090);
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
    result=None
    try:
        result=krakken_connection.query_private('AddOrder',req_data)
    except:
        logger.info('sell : faced an error.Resetting connector')
        reset()
        result=krakken_connection.query_private('AddOrder',req_data)
    print(result)      

def calculate_minimum_sell_price_to(volume,buy_price,objective=1.0):
    volume=float(volume)
    price=float(buy_price)
    amount=round(volume*price,5)
    fee=round((amount/100)*FEE_PERCENTAGE,5)
        
    gain=0
    STEP=0.0001
    sell_price=amount+(fee*2)
    
    while(gain<1):
        print("*****")
        sell_amount=sell_price
        sell_fee=(sell_amount/100)*FEE_PERCENTAGE
        print(sell_amount)
        
        gain=(sell_amount+sell_fee)-(amount+fee)
        print(gain)
        
        sell_price=sell_price+STEP
        
    return sell_price
   




def buy(volume,price,currency='XXRPZEUR'):
    req_data = {'pair': currency,'type':'buy','ordertype':'limit','price':price,'volume':volume}
    result=None
    try:
        result=krakken_connection.query_private('AddOrder',req_data)
    except:
        logger.info('buy : faced an error.Resetting connector')
        reset()
        result=krakken_connection.query_private('AddOrder',req_data)
    print(result)
    #{'error': [], 'result': {'descr': {'order': 'buy 100.00000000 XRPEUR @ limit 0.100000'}, 'txid': ['OHLVH2-GYDQ5-YQM6GP']}}

def get_currency_value(currency_separated_by_commas='EOSEUR,XRPEUR'):
    req_data = {'pair': currency_separated_by_commas}
    cur=None
    try:
        cur=krakken_connection.query_public('Ticker',req_data)
        cur=cur.get('result')
    except json.decoder.JSONDecodeError :
        logger.error('Error Json Decoder')
        cur=None
    except TimeoutError :
        logger.error('To check')
        cur=None
    except ValueError:
        logger.error('To check 2')
        cur=None
    return cur


