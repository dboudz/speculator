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


def get_buying_order_with_same_pattern_posterior_to(volume,price,timing,persistenceHandler,current_step_between_buy_and_sell,currency_order_name):
    # Searching order with same characteristics on open order /!\ created after timing
    logger.info(" Getting eventual open buying orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
    open_orders=get_single_open_orders(currency_order_name)
    time.sleep(5)
    oe_parameters=[]
    # Getting orders vol,price
    for item in open_orders:
        if(item.get('type')=='buy' and volume==item.get('vol') and price==item.get('price') and item.get('opentm') > timing ):
            oe_parameters.append((item.get('order_id'),item.get('vol'),item.get('price')))
    if(len(oe_parameters)>0):
        logger.info(" Founded buying orders with same characteristics in open order list:"+str(oe_parameters))
    else:
        logger.info(" No buying orders founded same characteristics  in open order list:"+str(oe_parameters))
 
    # Search on closed orders only if search on buying orders return nothing
    if(len(oe_parameters)==0):
        logger.info(" Getting eventual closed buying orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
        close_orders=get_closed_orders(persistenceHandler,current_step_between_buy_and_sell)
        time.sleep(5)
        # Getting orders vol,price
        for oeid in close_orders.keys():
            if(close_orders.get(oeid).get('status')=='closed' and close_orders.get(oeid).get('descr').get('type')=='buy' and volume==float(close_orders.get(oeid).get('vol')) and price==float(close_orders.get(oeid).get('descr').get('price')) and (close_orders.get(oeid).get('opentm') > timing )):
                oe_parameters.append((oeid,float(close_orders.get(oeid).get('vol')),float(close_orders.get(oeid).get('descr').get('price'))))
        if(len(oe_parameters)>0):
            logger.info(" Founded buying orders with same characteristics  in closed order list:"+str(oe_parameters))
        else:
            logger.info(" No buying orders founded same characteristics  in closed order list :"+str(oe_parameters))
    return oe_parameters

def get_selling_order_with_same_pattern_posterior_to(volume,price,timing,persistenceHandler,current_step_between_buy_and_sell,currency_order_name):
    # Searching order with same characteristics on open order /!\ created after timing
    logger.info(" Getting eventual open selling orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
    open_orders=get_single_open_orders(currency_order_name)
    time.sleep(5)
    oe_parameters=[]
    # Getting orders vol,price
    for item in open_orders:
        if(item.get('type')=='sell' and volume==item.get('vol') and price==item.get('price') and item.get('opentm') > timing ):
            oe_parameters.append((item.get('order_id'),item.get('vol'),item.get('price')))
    if(len(oe_parameters)>0):
        logger.info(" Founded selling orders with same characteristics in open order list:"+str(oe_parameters))
    else:
        logger.info(" No selling orders founded same characteristics  in open order list:"+str(oe_parameters))
 
    # Search on closed orders only if search on buying orders return nothing
    if(len(oe_parameters)==0):
        logger.info(" Getting eventual closed selling orders with same parameters (vol:"+str(volume)+" price"+str(price)+")")
        close_orders=get_closed_orders(persistenceHandler,current_step_between_buy_and_sell)
        time.sleep(5)
        # Getting orders vol,price
        for oeid in close_orders.keys():
            if(close_orders.get(oeid).get('status')=='closed' and close_orders.get(oeid).get('descr').get('type')=='sell' and volume==float(close_orders.get(oeid).get('vol')) and price==float(close_orders.get(oeid).get('descr').get('price')) and (close_orders.get(oeid).get('opentm') > timing )):
                oe_parameters.append((oeid,float(close_orders.get(oeid).get('vol')),float(close_orders.get(oeid).get('descr').get('price'))))
        if(len(oe_parameters)>0):
            logger.info(" Founded selling orders with same characteristics  in closed order list:"+str(oe_parameters))
        else:
            logger.info(" No selling orders founded same characteristics  in closed order list :"+str(oe_parameters))
    return oe_parameters

def secure_buy(volume,price,currency_crawling_name,persistenceHandler,current_step_between_buy_and_sell,currency_order_name):
    status=NOT_DONE
    # Get unix time
    time_before_buy=get_server_unixtime()
    time.sleep(120)
    logger.info("Secure buy stat at unix time "+str(time_before_buy))
    
    # Check for existing open orders
    existing_open_orders=get_single_open_orders(currency_order_name)
    flag_existing_oe=False
    new_buying_order=''
    
    for oe in existing_open_orders:
        if(oe.get('type')=='buy'):
            flag_existing_oe=True
            
    # If no existing open ordres, create order and wait until confirmation
    if(flag_existing_oe==False):
        req_data = {'pair': currency_crawling_name,'type':'buy','ordertype':'limit','price':price,'volume':volume}
        req_result={}
        
        try:
            logger.info("Lets go for the creation of buying order. Send request to the exchange.")
            time.sleep(1)
            req_result=krakken_connection.query_private('AddOrder',req_data)
            #{'error': [], 'result': {'descr': {'order': 'buy 30.00000000 XRPEUR @ limit 0.120000'}, 'txid': ['O55YD2-UXKMI-PPPXYP']}}
            validation=req_result.get('error')
            if(len(validation)>0):
                if(str(validation)=="['EService:Unavailable']"):
                    logger.warn("111 Error message "+str(validation)+ " was encoutered re-do the secure buy call")
                    return secure_buy(volume,price,currency_crawling_name,persistenceHandler,current_step_between_buy_and_sell,currency_order_name)
                else:
                    logger.error("Buying Order creation failed. Here is the req_result "+str(req_result))
                    notifier.notify("Fatal Error","Buying Order creation failed. Exiting "+str(validation))
                    exit(1)
            else:
                new_buying_order=req_result.get('result').get('txid')[0]
                logger.info("Buying Order creation success : "+str(new_buying_order))
        except Exception as e:
            logger.info("Exception was caught when trying to create buying order.")
            logger.info("104 Else, exception was "+str(e))                                
            if(str.strip(str(e)) =='The read operation timed out' or str.strip(str(e)) =='EService:Unavailable' ):
                 logger.warn(" Creation of buying order return error "+str(e))
                 logger.warn(" We will 1/ try rest kraken api, and  2/check 10 times to get the order id "+str(e))
                 reset()
                 cmpt=0
                 while(status==NOT_DONE):
                     logger.warn(" Try "+str(cmpt)+" for getting open order")
                     oeid_char=get_buying_order_with_same_pattern_posterior_to(volume,price,time_before_buy,persistenceHandler,current_step_between_buy_and_sell,currency_order_name)
                     if(len(oeid_char)>0):
                         if(len(oeid_char))>1:
                             logger.error("More than 1 buying order with same parameters : "+str(oeid_char))
                             notifier.notify("Fatal Error","More than 1 buying order with same parameters : "+str(oeid_char))
                             exit(1)
                         else:
                             status=DONE
                             new_buying_order=oeid_char[0][0]
                             logger.info("1 Open buying order with same characteristics found, it's our order created ! : "+str(oeid_char))
                     else:
                         logger.warn(" sleep 3 second before next try")
                         time.sleep(3)
                         cmpt=cmpt+1
                         
                     # Manage infinite loop
                     if(cmpt>0 and cmpt%15==0):
                         save_time_before_buy=time_before_buy
                         time_before_buy=time_before_buy-30
                         logger.info("time_before_buy is going to be changed by 30s "+str(save_time_before_buy)+" -> "+str(time_before_buy))
                         notifier.notify("Risk of infinite loop","time_before_buy is going to be changed by 30s "+str(save_time_before_buy)+" -> "+str(time_before_buy))
                     if(cmpt==115):
                         logger.info("time_before_buy is going to be changed by 30s "+str(save_time_before_buy)+" -> "+str(time_before_buy))
                         notifier.notify("Risk of infinite loop","Exiting to avoid to be stuck in failed secure buy loop")

                    
            else:
                logger.error("107 Unmanaged case. shutdown.")
                notifier.notify("Fatal Error","Unmanaged case "+str(e)+" Exiting.")
                exit(1)
    else:
        logger.error("Existing buying open orders already present, Exiting "+str(existing_open_orders))
        notifier.notify("Fatal Error","Existing buying open orders already present, Exiting "+str(existing_open_orders))
        exit(1)
    
    if(len(new_buying_order)<19):
        logger.error("Buying open orders id feels wrong ("+new_buying_order+")  Exiting ")
        notifier.notify("Fatal Error","Buying open orders id feels wrong ("+new_buying_order+")  Exiting ")
        exit(1)
    
    
    # Creating open_order dict object. (Few columns are wrong, but there is no impact)
    new_buying_order_dict={}
    new_buying_order_dict['order_id']=new_buying_order
    new_buying_order_dict['status']='open'
    new_buying_order_dict['opentm']=time_before_buy
    new_buying_order_dict['vol']=volume
    new_buying_order_dict['vol_exec']=0.0
    new_buying_order_dict['price']=price
    new_buying_order_dict['type']='buy'
    new_buying_order_dict['flag_buying_order_partially_executed']=False
    logger.debug("Returned buying order is "+str(new_buying_order_dict))
    return new_buying_order_dict

    

def secure_sell(volume,price,currency_crawling_name,persistenceHandler,current_step_between_buy_and_sell,currency_order_name):
    status=NOT_DONE
    # Get unix time
    time_before_sell=get_server_unixtime()
    logger.info("Secure sell stat at unix time "+str(time_before_sell))
    time.sleep(120)
    req_data = {'pair': currency_crawling_name,'type':'sell','ordertype':'limit','price':price,'volume':volume}
    req_result={}
    new_selling_order=''
    
    try:
        time.sleep(1)
        req_result=krakken_connection.query_private('AddOrder',req_data)
        validation=req_result.get('error')
        if(len(validation)>0):
            if(str(validation)=="['EService:Unavailable']"):
                logger.warn("111 Error message "+str(validation)+ " was encoutered re-do the secure buy call")
                return secure_sell(volume,price,currency_crawling_name,persistenceHandler,current_step_between_buy_and_sell,currency_order_name)
            else:
                logger.error("Selling Order creation failed. Here is the req_result "+str(req_result))
                notifier.notify("Fatal Error","Selling Order creation failed. Exiting")
                exit(1)
        else:
            new_selling_order=req_result.get('result').get('txid')[0]
            logger.info("Selling Order creation success : "+str(new_selling_order))
    except Exception as e:
        logger.info("Exception was caught when trying to create selling order.")
        logger.info("105 Else, exception was "+str(e))
        if(str.strip(str(e)) =='The read operation timed out'  or str.strip(str(e)) =='EService:Unavailable'):
             logger.warn(" Creation of selling order return error "+str(e))
             logger.warn(" We will 1/ try rest kraken api, and  2/check 10 times to get the order id "+str(e))
             reset()
             cmpt=0
             while(status==NOT_DONE):
                 logger.warn(" Try "+str(cmpt)+" for getting open order")
                 oeid_char=get_selling_order_with_same_pattern_posterior_to(volume,price,time_before_sell,persistenceHandler,current_step_between_buy_and_sell,currency_order_name)
                 if(len(oeid_char)>0):
                     if(len(oeid_char))>1:
                         logger.error("More than 1 selling order with same parameters : "+str(oeid_char))
                         notifier.notify("Fatal Error","More than 1 selling order with same parameters : "+str(oeid_char))
                         exit(1)
                     else:
                         status=DONE
                         new_selling_order=oeid_char[0][0]
                         logger.info("1 Open selling order with same characteristics found, it's our order created ! : "+str(oeid_char))
                 else:
                     logger.warn(" sleep 3 second before next try")
                     time.sleep(3)
                     cmpt=cmpt+1
        else:
            logger.error("106 Unmanaged case. shutdown.")
            notifier.notify("Fatal Error","Unmanaged case "+str(e)+" Exiting.")
            exit(1)
    if(len(new_selling_order)<19):
        logger.error("Selling open orders id feels wrong ("+new_selling_order+")  Exiting ")
        notifier.notify("Fatal Error","Buying open orders id feels wrong ("+new_selling_order+")  Exiting ")
        exit(1)
    
    # Creating open_order dict object. (Few columns are wrong, but there is no impact)
    new_selling_order_dict={}
    new_selling_order_dict['order_id']=new_selling_order
    new_selling_order_dict['status']='open'
    new_selling_order_dict['opentm']=time_before_sell
    new_selling_order_dict['vol']=volume
    new_selling_order_dict['vol_exec']=0.0
    new_selling_order_dict['price']=price
    new_selling_order_dict['type']='sell'
    new_selling_order_dict['flag_buying_order_partially_executed']=False  
    logger.debug("Returned selling order is "+str(new_selling_order_dict))
    return new_selling_order_dict


   
def private_call(function,parameters,logs=False):
    status=NOT_DONE
    cmpt=1
    result=None
    while(status!=DONE):
        try:
            time.sleep(1)
            result=krakken_connection.query_private(function,parameters)
            #logger.debug(str(result))
        except Exception as e:
            logger.info(function+' private faced an error at try number '+str(cmpt)+ ' : Error '+str(e))
            logger.info('Resetting exchange & retrying the request')
            reset()
            time.sleep(2)
        if(result is not None):
            status=DONE
            if(logs==True):
                logger.info('Succes on request '+str(function))
        cmpt=cmpt+1
    if(result==None or result=="{'error': ['EService:Unavailable']}"):
        return private_call(function,parameters,logs)
    else:
        return result

def public_call(function,parameters,logs=False):
    status=NOT_DONE
    cmpt=1
    result=None
    while(status!=DONE):
        try:
            time.sleep(1)
            result=krakken_connection.query_public(function,parameters)
            status=DONE
        except Exception as e:
            logger.info(function+' public faced an error at try number '+str(cmpt)+ ' : Error '+str(e))
            logger.info('Resetting exchange & retrying the request')
            reset()
            time.sleep(2)
        if(result is not None):
            status=DONE
            if(logs==True):
                logger.info('Succes on request '+str(function))
        cmpt=cmpt+1
    if(result==None or result=="{'error': ['EService:Unavailable']}"):
        return private_call(function,parameters,logs)
    else:
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

def get_balance_for_traded_currency(currency_balance_name):
    return get_balance_for_currency(currency_balance_name)

def get_balance_EUR():
    return get_balance_for_currency('ZEUR')

def get_balance_for_currency(currency):
    values=exchange_call(PRIVACY_PRIVATE,'Balance')
    for cur in list(values.get('result').keys()):
        if(cur==currency):
            return round(float(values.get('result').get(currency)),5)
 

# Single Method for Buying orders
def get_single_open_orders(TRADED_CURRENCY):
    dict_open_orders=exchange_call(PRIVACY_PRIVATE,'OpenOrders')
    list_open_orders=[]
    
    # Check if something goes wrong
    if dict_open_orders==None:
        logger.warn("get_single_open_orders, dict_open_orders is None. Recall")
        return get_single_open_orders()
    else:
        # Create dict with attributes of the order, only if the currency match to the traded one
        for oe in list(dict_open_orders.get('result').get('open').keys()):
            if(dict_open_orders.get('result').get('open').get(oe).get('descr').get('pair')==TRADED_CURRENCY):
                elem={}
                elem['order_id']=oe
                elem['status']=dict_open_orders.get('result').get('open').get(oe).get('status')
                elem['opentm']=float(dict_open_orders.get('result').get('open').get(oe).get('opentm'))
                elem['vol']=float(dict_open_orders.get('result').get('open').get(oe).get('vol'))
                elem['vol_exec']=float(dict_open_orders.get('result').get('open').get(oe).get('vol_exec'))
                elem['price']=float(dict_open_orders.get('result').get('open').get(oe).get('descr').get('price'))
                elem['type']=dict_open_orders.get('result').get('open').get(oe).get('descr').get('type')
                # create an attribute to help identify buying order partially executed
                if( elem.get('vol_exec') > 0.0 and elem.get('type')=='buy'):
                    elem['flag_buying_order_partially_executed']=True
                else:
                    elem['flag_buying_order_partially_executed']=False
            list_open_orders.append(elem)
    return list_open_orders
            
            
def get_closed_order_volume_by_id(id_order,persistenceHandler,current_step_between_buy_and_sell):
    dict_closed_orders=get_closed_orders(persistenceHandler,current_step_between_buy_and_sell)
    for oe in list(dict_closed_orders.keys()):
        if(oe==id_order):
            return float(dict_closed_orders.get(oe).get('vol_exec'))
    return 0.0

def get_closed_orders(persistenceHandler,current_step_between_buy_and_sell):
    dict_closed_orders=exchange_call(PRIVACY_PRIVATE,'ClosedOrders')
    
    # Persist closed selling order
    for coe in list(dict_closed_orders.get('result').get('closed')):
        # StoreClosedOrder(order_id,opening_date,closing_date,price,volume,order_type,,current_step_between_buy_and_sell)
        opening_date=dict_closed_orders.get('result').get('closed').get(coe).get('opentm')
        closing_date=dict_closed_orders.get('result').get('closed').get(coe).get('closetm')
        price=float(dict_closed_orders.get('result').get('closed').get(coe).get('price'))
        executed_volume=float(dict_closed_orders.get('result').get('closed').get(coe).get('vol_exec'))
        order_type=dict_closed_orders.get('result').get('closed').get(coe).get('descr').get('type')
        # Persist only selling order with a volume executed
        if(executed_volume>0.0 and order_type=='sell'):
            persistenceHandler.storeClosedOrder(coe,opening_date,closing_date,price,executed_volume,order_type,current_step_between_buy_and_sell)
    
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


def get_currency_value(currency_crawling_name):
    req_data = {'pair': currency_crawling_name}
    cur=exchange_call(PRIVACY_PUBLIC,'Ticker',req_data)
    return cur
