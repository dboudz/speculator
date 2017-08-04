#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 22:54:47 2017

@author: dboudeau
"""
import exchange_krakken as kraken
import time,os
import persistenceHandler
import logging
import businessLogic

# Var initialization
CRAWLED_CURRENCIES=os.environ['CRAWLED_CURRENCIES']

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


kraken.init()
list_open_orders=kraken.get_open_orders_ids()

####################11
# Initialize traders
allowed_budget=126.0
expected_gain_by_band=0.065
number_of_traders=20
step_between_unit_sell_and_unit_price=0.002


# trader (integerId,,budget(€),buy_unit_price,sell_unit_price,is_engaged
list_trader=[
(0,7.0,0.157,False),
(1,7.0,0.155,False),
(2,7.0,0.153,False),
(3,7.0,0.151,False),
(4,7.0,0.149,False),
(5,7.0,0.147,False),
(6,7.0,0.145,False),
(7,7.0,0.143,False),
(8,6.0,0.141,False),
(9,6.0,0.139,False),
(10,6.0,0.137,False),
(11,6.0,0.135,False),
(12,6.0,0.133,False),
(13,6.0,0.131,False),
(14,6.0,0.129,False),
(15,6.0,0.127,False),
(16,6.0,0.125,False),
(17,6.0,0.123,False),
(18,5.0,0.121,False),
(19,5.0,0.119,False)
]

# Check viability of configuration
if(False==businessLogic.check_traders_configuration(list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget)):
    logger.error("Configuration of traders is not valid. Exiting")
    exit(1)
else:
    logger.info("Configuration of trader is valid [V]")


# Map current orders with traders




#while(1==1):
#    ###############
#    # Crawl data
#    ###############
#    crawled_currencies=kraken.get_currency_value(CRAWLED_CURRENCIES)
#    
#    if(crawled_currencies != None):
#        for currency in crawled_currencies.get('result').keys():
#            c=crawled_currencies.get('result').get(currency)
#            persistenceHandler.storeCurrency(currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
#    time.sleep(15)
#    
#    ###########################
#    # Notify for closed Orders
#    ###########################
#    list_open_orders=kraken.check_orders_and_notify_if_closure_detected(list_open_orders)
#    time.sleep(15)
    
    
    
    
    
    ###########################
    # Traders
    ###########################
    
    