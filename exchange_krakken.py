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


def get_buying_order_with_same_pattern(volume,price):
    # Before buying, check that there is no order with same characteristics
    logger.info(" Getting eventual buying orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
    open_orders=get_open_orders()
    time.sleep(5)
    oe_parameters=[]
    # Getting orders vol,price
    for oeid in open_orders.keys():
        if(open_orders.get(oeid).get('descr').get('type')=='buy' and volume==float(open_orders.get(oeid).get('vol')) and price==float(open_orders.get(oeid).get('descr').get('price'))):
            oe_parameters.append((oeid,float(open_orders.get(oeid).get('vol')),float(open_orders.get(oeid).get('descr').get('price'))))
    if(len(oe_parameters)>0):
        logger.info(" Founded buying orders with same characteristics :"+str(oe_parameters))
    else:
        logger.info(" No buying orders founded same characteristics :"+str(oe_parameters))
    return oe_parameters

def get_selling_order_with_same_pattern(volume,price):
    # Before buying, check that there is no order with same characteristics
    logger.info(" Getting eventual selling orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
    open_orders=get_open_orders()
    time.sleep(5)
    oe_parameters=[]
    # Getting orders vol,price
    for oeid in open_orders.keys():
        if(open_orders.get(oeid).get('descr').get('type')=='sell' and volume==float(open_orders.get(oeid).get('vol')) and price==float(open_orders.get(oeid).get('descr').get('price'))):
            oe_parameters.append((oeid,float(open_orders.get(oeid).get('vol')),float(open_orders.get(oeid).get('descr').get('price'))))
    if(len(oe_parameters)>0):
        logger.info(" Founded selling orders with same characteristics :"+str(oe_parameters))
    else:
        logger.info(" No selling orders founded same characteristics :"+str(oe_parameters))
    return oe_parameters

def secure_buy(volume,price,currency='XXRPZEUR'):
    # Check for existing open orders
    existing_open_orders=get_open_orders_ids_and_type()
    flag_existing_oe=False
    new_buying_order=''
    
    for oe in existing_open_orders:
        if(oe[1]=='buy'):
            flag_existing_oe=True
    # If no existing open ordres, create order and wait until confirmation
    if(flag_existing_oe==False):
        req_data = {'pair': currency,'type':'buy','ordertype':'limit','price':price,'volume':volume}
        req_result={}
        
        try:
            time.sleep(1)
            req_result=krakken_connection.query_private('AddOrder',req_data)
            #{'error': [], 'result': {'descr': {'order': 'buy 30.00000000 XRPEUR @ limit 0.120000'}, 'txid': ['O55YD2-UXKMI-PPPXYP']}}
            validation=req_result.get('error')
            if(len(validation)>0):
                logger.error("Buying Order creation failed. Here is the req_result "+str(req_result))
                notifier.notify("Fatal Error","Buying Order creation failed. Exiting")
                exit(1)
            else:
                new_buying_order=req_result.get('result').get('txid')[0]
                logger.info("Buying Order creation success : "+str(new_buying_order))
        except Exception as e:
            if(str.strip(str(e)) =='The read operation timed out' or str.strip(str(e)) =='EService:Unavailable' ):
                 logger.warn(" Creation of buying order return error "+str(e))
                 logger.warn(" We will 1/ try rest kraken api, and  2/check 10 times to get the order id "+str(e))
                 reset()
                 cmpt=0
                 while(cmpt<10):
                     logger.warn(" Try "+str(cmpt)+" for getting open order")
                     oeid_char=get_buying_order_with_same_pattern(volume,price)
                     if(len(oeid_char)>0):
                         if(len(oeid_char))>1:
                             logger.error("More than 1 buying order with same parameters : "+str(oeid_char))
                             notifier.notify("Fatal Error","More than 1 buying order with same parameters : "+str(oeid_char))
                             exit(1)
                         else:
                             cmpt=10000
                             new_buying_order=oeid_char[0][0]
                             logger.info("1 Open buying order with same characteristics found, it's our order created ! : "+str(oeid_char))
                     else:
                         logger.warn(" sleep 3 second before next try")
                         time.sleep(3)
                         cmpt=cmpt+1
    else:
        logger.error("Existing buying open orders already present, Exiting "+str(existing_open_orders))
        notifier.notify("Fatal Error","Existing buying open orders already present, Exiting "+str(existing_open_orders))
        exit(1)
    return new_buying_order

    

def secure_sell(volume,price,currency='XXRPZEUR'):
    
    req_data = {'pair': currency,'type':'sell','ordertype':'limit','price':price,'volume':volume}
    req_result={}
    new_selling_order=''
    
    try:
        time.sleep(1)
        req_result=krakken_connection.query_private('AddOrder',req_data)
        validation=req_result.get('error')
        if(len(validation)>0):
            logger.error("Selling Order creation failed. Here is the req_result "+str(req_result))
            notifier.notify("Fatal Error","Selling Order creation failed. Exiting")
            exit(1)
        else:
            new_selling_order=req_result.get('result').get('txid')[0]
            logger.info("Selling Order creation success : "+str(new_selling_order))
    except Exception as e:
        if(str.strip(str(e)) =='The read operation timed out'  or str.strip(str(e)) =='EService:Unavailable'):
             logger.warn(" Creation of selling order return error "+str(e))
             logger.warn(" We will 1/ try rest kraken api, and  2/check 10 times to get the order id "+str(e))
             reset()
             cmpt=0
             while(cmpt<10):
                 logger.warn(" Try "+str(cmpt)+" for getting open order")
                 oeid_char=get_selling_order_with_same_pattern(volume,price)
                 if(len(oeid_char)>0):
                     if(len(oeid_char))>1:
                         logger.error("More than 1 selling order with same parameters : "+str(oeid_char))
                         notifier.notify("Fatal Error","More than 1 selling order with same parameters : "+str(oeid_char))
                         exit(1)
                     else:
                         cmpt=10000
                         new_selling_order=oeid_char[0][0]
                         logger.info("1 Open selling order with same characteristics found, it's our order created ! : "+str(oeid_char))
                 else:
                     logger.warn(" sleep 3 second before next try")
                     time.sleep(3)
                     cmpt=cmpt+1

    return new_selling_order


   
def private_call(function,parameters):
    status=NOT_DONE
    cmpt=1
    result=None
    while(status!=DONE):
        try:
            time.sleep(1)
            result=krakken_connection.query_private(function,parameters)
            logger.debug(str(result))
        except Exception as e:
            logger.info(function+' private faced an error at try number '+str(cmpt)+ ' : Error '+str(e))
            logger.info('Resetting exchange & retrying the request')
            reset()
            time.sleep(2)
        if(result is not None):
            status=DONE
            logger.info('Succes on request '+str(function))
        cmpt=cmpt+1
    return result

def public_call(function,parameters):
    status=NOT_DONE
    cmpt=1
    result=None
    while(status!=DONE):
        try:
            time.sleep(1)
            result=krakken_connection.query_public(function,parameters)
            logger.debug(str(result))
            status=DONE
        except Exception as e:
            logger.info(function+' public faced an error at try number '+str(cmpt)+ ' : Error '+str(e))
            logger.info('Resetting exchange & retrying the request')
            reset()
            time.sleep(2)
        if(result is not None):
            status=DONE
            logger.info('Succes on request '+str(function))
        cmpt=cmpt+1
    return result

def exchange_call(privacy,function,parameters={}):
    if(privacy==PRIVACY_PRIVATE):
        return private_call(function,parameters)
    if(privacy==PRIVACY_PUBLIC):
        return public_call(function,parameters)


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


def get_open_orders_ids_and_type():
    list_open_orders=[]
    dict_open_orders=get_open_orders()
    for orderId in list(dict_open_orders.keys()):
        list_open_orders.append( [orderId,dict_open_orders.get(orderId).get('descr').get('type')])
    return list_open_orders

def get_open_orders():
    dict_open_orders=exchange_call(PRIVACY_PRIVATE,'OpenOrders')
    return (dict_open_orders.get('result').get('open'))
  
def get_open_orders_selling_with_unit_sell_price_and_volume():
    list_open_orders_with_unit_sell_price=[]
    open_orders=get_open_orders()
    for oe in list(open_orders.keys()):
        oe_currency=open_orders.get(oe).get('descr').get('pair')
        oe_order_type=open_orders.get(oe).get('descr').get('type')
        oe_unit_sell_price=float(open_orders.get(oe).get('descr').get('price'))
        oe_volume=float(open_orders.get(oe).get('vol'))
        if(oe_currency=='XRPEUR' and oe_order_type=='sell'):
            list_open_orders_with_unit_sell_price.append((oe,oe_unit_sell_price,oe_volume))
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

def secure_cancel_order(order_id):
    req_data={'txid':order_id}
    function='CancelOrder'
    cmpt=1
    status_of_function=NOT_DONE
    while(status_of_function!=DONE):
        try:
            logger.info(function+' :try number '+str(cmpt)+' for '+str(function))
            result=krakken_connection.query_private('CancelOrder',req_data)
            print(result)
            if(len(result.get('error'))>0):
                #{'error': [], 'result': {'count': 1}}
                error_type=result.get('error')[0]
                if( (error_type == 'EOrder:Invalid order') or ('EOrder:Unknown order' in error_type)):
                    logger.warn(function+' :Order '+str(order_id)+' not found (EOrder:Invalid order), but it seems to be ok ')
                    status_of_function=DONE
                else:
                    logger.warn(function+' :Cant handle error '+str(result)+ 'cancel order will be re-processed' )
            else:
                status_of_function=DONE
            if(cmpt>10  and cmpt%10==0):
                logger.info(function+' :'+str(cmpt)+' fail ! notifying ...')
                notifier.notify('Need You',str(cmpt)+' fail  on cancel order\n ! cant handle error'+str(result))
        except Exception as e:
            logger.info(function+' : private faced an error. Resetting exchange & retrying the request')
            logger.info(function+' : Exception was :'+str(e))
            logger.info(function+' : Resetting & waiting :'+str(e))
            reset()
        cmpt=cmpt+1
    logger.info(function+' OK for '+str(function))
    return DONE
    
      

def get_server_unixtime():
    unix_time_integer=-1    
    time_krakken=exchange_call(PRIVACY_PUBLIC,'Time')    
    unix_time_integer=time_krakken.get('result').get('unixtime')
    #Tips for SQL to Timestamp postgres = select to_timestamp(1501523090);
    return unix_time_integer


def get_currency_value(currency_separated_by_commas='XXRPZEUR'):
    req_data = {'pair': currency_separated_by_commas}
    cur=exchange_call(PRIVACY_PUBLIC,'Ticker',req_data)
    return cur
