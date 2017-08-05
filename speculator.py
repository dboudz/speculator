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
list_open_orders=kraken.get_open_orders_ids_and_type()
DONE=0
NOT_DONE=1


####################11
# Initialize traders
WAITING='wait'
SELLING='sell'
BUYING='buy'


allowed_budget=126.0
expected_gain_by_band=0.065
number_of_traders=20
step_between_unit_sell_and_unit_price=0.002

sequence_number=0
def increment_sequence():
    global sequence_number
    sequence_number=sequence_number+1
    return sequence_number


# trader (integerId,,budget(€),buy_unit_price,sell_unit_price,is_engaged,open_orders,Status,available_budget
list_trader=[]
list_trader.append([increment_sequence(),7.0,0.157,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.155,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.153,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.151,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.149,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.147,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.145,None,WAITING,0.0])
list_trader.append([increment_sequence(),7.0,0.143,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.141,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.139,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.137,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.135,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.133,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.131,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.129,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.127,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.125,None,WAITING,0.0])
list_trader.append([increment_sequence(),6.0,0.123,None,WAITING,0.0])
list_trader.append([increment_sequence(),5.0,0.121,None,WAITING,0.0])
list_trader.append([increment_sequence(),5.0,0.119,None,WAITING,0.0])


# Check viability of configuration
if(False==businessLogic.check_traders_configuration(number_of_traders,list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget)):
    logger.error("Configuration of traders is not valid. Exiting")
    exit(1)
else:
    logger.info("Configuration of trader is valid [V]")


# Closing All buying orders (security)
for order_with_type in list_open_orders:
    if(order_with_type[1]==BUYING):
        logger.info("Buying Order "+str(order_with_type[0])+" is going to be cancel by speculator initialization")
        if(kraken.cancel_order(order_with_type[0])==DONE):
            logger.info("Buying Order "+str(order_with_type[0])+" was closed at initialization of speculator")
        else:
            logger.error("Buying Order "+str(order_with_type[0])+" was closed at initialization of speculator")
            exit(1)

# Map current orders with traders.
for open_selling_order in kraken.get_open_orders_selling_with_unit_sell_price():
    is_order_mapped=False
    # Map selling order only if it fits with a trader
    for index in range(0,number_of_traders):
        # checking if selling price in between buy and sell price
        if(open_selling_order[1]>list_trader[index][2] and open_selling_order[1]<=list_trader[index][2]+step_between_unit_sell_and_unit_price):
            logger.info('Mapping order '+str(open_selling_order[0])+' - '+str(open_selling_order[1])+' to trader '+str(list_trader[index][0]))
            logger.info('Trader '+str(index)+' ( '+str(list_trader[index][2])+' -> '+str(list_trader[index][2]+step_between_unit_sell_and_unit_price)+')') 
            is_order_mapped=True
            # Set up the trader with new status
            list_trader[index][3]=str(open_selling_order[0])
            list_trader[index][4]=SELLING
            list_trader[index][5]=0.0
            #TODO Ajouter une securite pour ne pas mapper 2 fois l'ordre break ????
    if is_order_mapped==False:
        logger.info('Order '+str(open_selling_order[0])+' is NOT MAPPED')

################ TODO TODO
#TODO## TEST IF THE BUDGET IS COMPLIANT WITH MONEY DEPOSIT ON EXCHANGE

logger.info("------- Let's Trade Baby------------------- ;)")
while(1==1):
    ######################
    # Crawl and store data
    ######################
    crawled_currencies=kraken.get_currency_value(CRAWLED_CURRENCIES)
    
#    if(crawled_currencies != None):
#        for currency in crawled_currencies.get('result').keys():
#            c=crawled_currencies.get('result').get(currency)
#            persistenceHandler.storeCurrency(currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
#    time.sleep(15)
    
    ###########################
    # Notify for closed Orders
    ###########################
    list_open_orders=kraken.check_orders_and_notify_if_closure_detected(list_open_orders)
    time.sleep(15)
    
    ##########################
    #Traders
    ##########################
    # Get trading informations
    
    # Check if a trader is buying, else set up to buy
    
    #TODO IF BUYING
    if(1==1):
        # Verifier si l'ordre d'achat est toujours bien placé par rapport au maché
        # ,c'est à dire juste en dessous mais le marché ne doit pas être supérieur à l'ordre de vente du palier au dessus
        # si c'est le cas, annuler l'ordre
        print('lol')
    
    #TODO IF NO BUYING IN PROGRESS
    if(1==1):
        # Setting budget for traders
        logger.info("----------------------------------------")
        available_budget=0
        for index in range(0,number_of_traders):
            # Define budget available for current trader 
            if(list_trader[index][4]==WAITING):
                available_budget=available_budget+list_trader[index][1]
                list_trader[index][5]=available_budget
                logger.debug('Trader '+str(index)+' has a budget of '+str(available_budget)+' €')
                
            else:
                list_trader[index][5]=0.0
                logger.debug('Trader '+str(index)+' is in '+list_trader[index][4]+' mode and has no budget to provide ')
        # Try to add a buying order (cf critere au dessus)
    
    
    
    