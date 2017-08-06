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
TRADING_CURRENCY='XXRPZEUR'

allowed_budget=150.0
expected_gain_by_band=0.065
number_of_traders=23
step_between_unit_sell_and_unit_price=0.002

sequence_number=-1
def increment_sequence():
    global sequence_number
    sequence_number=sequence_number+1
    return sequence_number


# trader (integerId,,budget(€),buy_unit_price,buying_order,Status,available_budget
list_trader=[]
list_trader.append([increment_sequence(),8.0,0.163,None,WAITING,0.0])
list_trader.append([increment_sequence(),8.0,0.161,None,WAITING,0.0])
list_trader.append([increment_sequence(),8.0,0.159,None,WAITING,0.0])
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
    # Get current exchange time
    kraken_time=kraken.get_server_unixtime()
    
    ######################
    # Crawl and store data
    ######################
    crawled_currencies=kraken.get_currency_value(CRAWLED_CURRENCIES)
    currency_actual_ask_price=float(crawled_currencies.get('result').get(TRADING_CURRENCY).get('a')[0])
    if(crawled_currencies != None):
        for currency in crawled_currencies.get('result').keys():
            c=crawled_currencies.get('result').get(currency)
            persistenceHandler.storeCurrency(kraken_time,currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
    logger.info("Crawled values "+str(currency_actual_ask_price)+" for currency "+str(CRAWLED_CURRENCIES))
    time.sleep(15)
    
    ###########################
    # Notify for closed Orders
    ###########################
    list_open_orders=kraken.check_orders_and_notify_if_closure_detected(list_open_orders)
    time.sleep(15)
    
    ##########################
    #Traders
    ##########################
    
    CAN_LAUNCH_BUYING_ORDER=False
    CURRENT_BUYING_ORDER_ID=-1
    # Check if a trader is buying, else set up to buy
    EXISTS_OPEN_BUYING_ORDERS=False
    BUYING_TRADER_ID=-1
    for index in range(0,number_of_traders):
        if list_trader[index][4]==BUYING:
            EXISTS_OPEN_BUYING_ORDERS=True
            BUYING_TRADER_ID=list_trader[index][0]
            CURRENT_BUYING_ORDER_ID=list_trader[index][3]
    
    # Get trading informations only if no other speculators are buying
    IS_TREND_GROWING=False
    if(EXISTS_OPEN_BUYING_ORDERS==False):
        trends2_is_growing=businessLogic.it_market_increasing(persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,2))
        trends5_is_growing=businessLogic.it_market_increasing(persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,5))
        trends10_is_growing=businessLogic.it_market_increasing(persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,10))
        trends15_is_growing=businessLogic.it_market_increasing(persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,15))
        if(trends2_is_growing and trends5_is_growing and trends10_is_growing and trends15_is_growing):
            IS_TREND_GROWING=True
    
    
    # If market is growing and no one is buying, check bugdet
    if(IS_TREND_GROWING==True and EXISTS_OPEN_BUYING_ORDERS==False):
        logger.info("Market is OK, and no buying orders open : time to shop a little bit ! ")
        # get the right trader, and launch buying
        logger.info("------Begin calculating the budget for each trader before buying----")
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
        logger.info("------End of Budget Calculation----")
        
        # /!\ check from lowest trader to higher trader is essential
        SELECTED_TRADER_ID_FOR_BUYING=-1
        for index in range(number_of_traders-1,-1,-1):
            # If trader's buy price is higher than value price we have the right trader
            if(list_trader[index][2]>=currency_actual_ask_price):
                # index of selected trader is index-1
                SELECTED_TRADER_ID_FOR_BUYING=index-1
                text1="Trader "+str(SELECTED_TRADER_ID_FOR_BUYING)+' was selected to buy at '+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][2])+" because market price is "+str(currency_actual_ask_price)
                text2="          budget is going to be "+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][5])+"€"
                logger.info(text1)
                logger.info(text2)
                # TO DELETE
                #kraken.notify('BUYING ORDER IS GONNA BE CREATED !!!!',text=text1+"\n"+text2)
                # create buying order
                # TODO
                # setup buying mode to avoir other buy attempt
                EXISTS_OPEN_BUYING_ORDERS=True
                #TODO
                break;
    else:
        if(IS_TREND_GROWING==False):  
            logger.info("Market is not good at this time ")
        if(EXISTS_OPEN_BUYING_ORDERS==True):
            # On ne verifie pas l'ordre du top trader (on ne peut rien faire de toute manière)
            if(BUYING_TRADER_ID>0):
                logger.info("Check if Trader "+str(BUYING_TRADER_ID)+" buying order has still potential to reach ")
                # check if order is ok
                buying_trader=list_trader[BUYING_TRADER_ID]
                upper_buying_trader=list_trader[BUYING_TRADER_ID-1]
                if(buying_trader[0]==BUYING_TRADER_ID and upper_buying_trader[0]==BUYING_TRADER_ID-1):
                    # Technical security : get open order details  and check them
                    # Control is : market price has to be - upper or  equals to buyer unit price
                    #                                     - below upper trader buy price
                    if(buying_trader[2]<= currency_actual_ask_price  and currency_actual_ask_price<upper_buying_trader[2] ):
                        logger.info('Order is still rightly placed : (buyer price  '+str(buying_trader[2])+') <= (market price '+str(currency_actual_ask_price)+') < ( upper buyer price '+str(upper_buying_trader[2])+')')
                    else:
                        logger.info('Order no more smartly placed : following condition is not true anymore:\n (buyer price  '+str(buying_trader[2])+') <= (market price '+str(currency_actual_ask_price)+') < ( upper buyer price '+str(upper_buying_trader[2])+')')
                        result=kraken.cancel_order(CURRENT_BUYING_ORDER_ID)
                        if(result!=DONE):
                            logger.error('Cant cancel order '+str(CURRENT_BUYING_ORDER_ID))
                            exit(1)
                else:
                    logger.error("Technical Issue, trader tab is corrupted")


    
    