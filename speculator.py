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
import notifier
import math


# TODO Creer des classes traders/order car la c'est de la pure MERDE
# TODO Unifier les differentes methodes qui appellent open and close orders. Il y en a plein ca sert à rien
# TODO SI N ORDRE DE VENTE MANQUE IL FAUT GERER CA ! cf requete unclosed trade
# TODO Chaque appel de open ou closed order devrait amener a un update de la table close

# Var initialization
AUTHORIZATION_OF_BUYING=bool(os.environ['AUTHORIZATION_OF_BUYING']=='True')
# XRP -> XXRPZEUR       LTC -> XLTCZEUR   ETC -> XETCZEUR
CURRENCY_CRAWLED_NAME=os.environ['CURRENCY_CRAWLED_NAME']
# XRP -> XRPEUR         LTC -> LTCEUR     ETC -> ETCEUR
CURRENCY_ORDER_NAME=os.environ['CURRENCY_ORDER_NAME']
# XRP -> XXRP           LTC -> XLTC       ETC -> XETC
CURRENCY_BALANCE_NAME=os.environ['CURRENCY_BALANCE_NAME']

NOTIFY_ON_CLOSED_ORDERS=bool(os.environ['NOTIFY_ON_CLOSED_ORDERS']=='True')

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


kraken.init()
list_open_orders=kraken.get_single_open_orders(CURRENCY_ORDER_NAME)
DONE=0
NOT_DONE=1

####################11
# Initialize traders
WAITING='wait'
SELLING='sell'
BUYING='buy'
CLOSED='closed'
CANCELED='canceled'

sequence_number=-1
def increment_sequence():
    global sequence_number
    sequence_number=sequence_number+1
    return sequence_number

##################
# TRADING SETUP  #
##################
allowed_budget=1051.0
expected_gain_by_band=0.08
number_of_traders=50
# NEVER CHANGE THIS ONE IF EXISTING SELLING ORDER
step_between_unit_sell_and_unit_price=0.10
minimum_buying_price=11.0
# project(48,0.28,0.067,46,1035)
  # trader (integerId,budget(€),buy_unit_price,buying_order,Status,available_budget,engaged_budget
     
list_trader=[]
list_trader.append([increment_sequence(),28.0,15.90,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),28.0,15.80,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),27.0,15.70,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),27.0,15.60,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),27.0,15.50,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,15.40,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,15.30,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,15.20,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,15.10,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,15.00,None,WAITING,0.0,0.0])
                                                  
list_trader.append([increment_sequence(),25.0,14.90,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,14.80,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,14.70,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,14.60,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,14.50,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,14.40,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,14.30,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,14.20,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,14.10,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,14.00,None,WAITING,0.0,0.0])
                                                  
list_trader.append([increment_sequence(),22.0,13.90,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.80,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.70,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.60,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.50,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.40,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),21.0,13.30,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),19.0,13.20,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),19.0,13.10,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),19.0,13.00,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,12.90,None,WAITING,0.0,0.0])
                                                  
list_trader.append([increment_sequence(),25.0,12.80,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),22.0,12.70,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.60,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.50,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.40,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.30,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.20,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),18.0,12.10,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,12.00,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,11.90,None,WAITING,0.0,0.0])
                                                  
list_trader.append([increment_sequence(),16.0,11.80,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,11.70,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,11.60,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,11.50,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,11.40,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,11.30,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,11.20,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,11.10,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,11.00,None,WAITING,0.0,0.0])


def safetyCheckOnTradingCurrencySellingOrder(open_orders,owned_volume_of_traded_money):
    logger.info('On initizalization or after cancel order, check if there is no missing selling order')
    sold_volume=0.0
    for order in open_orders:
        if(order.get('type')==SELLING):
            sold_volume=sold_volume+order.get('vol')
    if(abs(owned_volume_of_traded_money - (sold_volume+0.1))>=0.5):
        
        # Particular case : If there is a buying/selling order partially processed, amount can be slightly different:
        logger.info("88 Checking for partial orders ")
        sum_buying_partial=0.0
        for item in open_orders:
            logger.debug(str(item))
            if (item.get('vol_exec')>0.0):
                logger.info("89 Adding "+str(item.get('vol_exec'))+" from order "+item.get('order_id'))
                sum_buying_partial=sum_buying_partial+item.get('vol_exec')
        logger.info("90 Sum partial order  "+str(sum_buying_partial))
        if(sum_buying_partial>0):
            logger.info(CURRENCY_BALANCE_NAME+" Sanity check detect open order partially executed")
        else:
            logger.error(CURRENCY_BALANCE_NAME+" owned volume on exchange ("+str(owned_volume_of_traded_money)+") are not all in sell mode ("+str(sold_volume)+"). Probably a missing sell order")
            notifier.notify('Safety Check failed',CURRENCY_BALANCE_NAME+" owned volume on exchange ("+str(owned_volume_of_traded_money)+") are not all in sell mode ("+str(sold_volume)+"). Probably a missing sell order")
            exit(1)
    else:
        logger.info(CURRENCY_BALANCE_NAME+" owned volume on exchange ("+str(owned_volume_of_traded_money)+") are all in sell mode ("+str(sold_volume)+").Good to go.")
        
    # Checking number of open buying orders :
    counter_open_buying_order=0
    for open_order in open_orders:
        if(open_order.get('type')==BUYING):
            counter_open_buying_order=counter_open_buying_order+1
            
    # Test number of buying orders
    if(counter_open_buying_order>1):
        logger.error("More than 1 buying order detected")
        notifier.notify("Fatal Error","More than 1 buying order detected"+str(open_order))
        logger.error("Exiting")
        exit(1)    
        

def calculatedEngagedMoney(volume,unit_sell_price,step_between_unit_sell_and_unit_price):
    buy_trade=volume * round(unit_sell_price-step_between_unit_sell_and_unit_price,2)
    fees=businessLogic.calculate_fee(volume * round(unit_sell_price-step_between_unit_sell_and_unit_price,2))
    engaged_money=math.ceil(buy_trade + fees)
    logger.info("Volume buyed was "+str(volume) +" at "+str(round(unit_sell_price-step_between_unit_sell_and_unit_price,2) ))
    logger.info("             fees were "+str(fees) )
    logger.info("             so (ceiled) engaged money was "+str(float(round(buy_trade + fees,2))) )
    return float(engaged_money)

# Ratio should be different
def budgetCalculation(list_trader,number_of_traders,logs=False):
    logger.info("------Begin calculating the budget for each trader before buying----")
    available_budget=0
    for index in range(0,number_of_traders):
        # Define the ratio of the above(s) free traders which is allowed by below traders
        RATIO_OF_ABOVE_BUDGET_ALLOCATED=round((index+1)/number_of_traders,2)
        
        if(list_trader[index][4]==WAITING):
            list_trader[index][5]=round( (available_budget * RATIO_OF_ABOVE_BUDGET_ALLOCATED ) + list_trader[index][1] ,2)
            available_budget=available_budget+list_trader[index][1]
        else:
            list_trader[index][5]=0.0

            # Engaged money
            if(list_trader[index][6]>0 and list_trader[index][6]<available_budget):
                logger.info(" * Engaged Budget is "+str(list_trader[index][6])+" and available budget is "+str(available_budget))
                logger.info(" * available budget will be increased of  "+str(available_budget-list_trader[index][6]))
                available_budget=available_budget-list_trader[index][6]
            else:
                logger.info(" Budget will be 0")
                available_budget=0
            
            logger.debug('Trader '+str(index)+' is in '+list_trader[index][4]+' mode and has no budget to provide ')
            logger.debug('Budget for above traders is going to be removed !')
            for index_above_trader in range(index,-1,-1):
                list_trader[index_above_trader][5]=0.0
                logger.debug('Trader '+str(index_above_trader)+' budget removed because  below Trader '+str(index)+' is in '+str(list_trader[index][4])+' mode')

    # Display budget
    if (logs==True):
        logger.info("------Display of Final budget ----")
        for index in range(0,number_of_traders):
            logger.info('Trader '+str(index)+', buyer at '+str(list_trader[index][2])+' is in '+str.upper(list_trader[index][4])+' mode with a budget of '+str(list_trader[index][5])+" engaged money is "+str(list_trader[index][6]))
        logger.info("------End of Budget Calculation----")
    return list_trader


# Check viability of configuration
if(False==businessLogic.check_traders_configuration(kraken.get_balance_EUR(),number_of_traders,list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget)):
    logger.error("Configuration of traders is not valid. Exiting")
    notifier.notify('Fatal Error',"Configuration of traders is not valid. Exiting")
    exit(1)
else:
    logger.info("[V] Configuration of trader is valid [V]")


## Closing All buying orders (security)
for open_order in list_open_orders:
    if(open_order.get('type')==BUYING):
        logger.info("Buying Order "+str(open_order.get('order_id'))+" is going to be cancel by speculator initialization")
        if(kraken.secure_cancel_order(open_order.get('order_id'))==DONE):
            logger.info("Buying Order "+str(open_order.get('order_id'))+" was closed at initialization of speculator")
        else:
            logger.error("Buying Order "+str(open_order.get('order_id'))+" coundn't be closed at initialization of speculator")
            notifier.notify('Fatal Error',"Buying Order "+str(open_order.get('order_id'))+" was closed at initialization of speculator")
            exit(1)
            
## Reinitializing buying list:
list_open_orders=kraken.get_single_open_orders(CURRENCY_ORDER_NAME)

# Map current orders with traders.
for open_selling_order in list_open_orders:
    is_order_mapped=False
    # Map selling order only if it fits with a trader
    for index in range(0,number_of_traders):
        # checking if selling price in between buy and sell price
        if(open_selling_order.get('price')>list_trader[index][2] and open_selling_order.get('price')<=round(list_trader[index][2]+step_between_unit_sell_and_unit_price,2)):
            logger.info('Mapping order '+open_selling_order.get('order_id')+' - '+str(open_selling_order.get('price'))+' to trader '+str(list_trader[index][0]))
            logger.info('Trader '+str(index)+' ( '+str(list_trader[index][2])+' -> '+str(round(list_trader[index][2]+step_between_unit_sell_and_unit_price,2))+')') 
            is_order_mapped=True
            # Set up the trader with new status
            list_trader[index][3]=open_selling_order.get('order_id')
            list_trader[index][4]=SELLING
            list_trader[index][5]=0.0
            # Engaged money is selling volume*unit buy_price + fees
            list_trader[index][6]=calculatedEngagedMoney(open_selling_order.get('vol'),list_trader[index][2],step_between_unit_sell_and_unit_price)
        if(is_order_mapped):
            break;
    if is_order_mapped==False:
        logger.info('Order '+open_selling_order.get('order_id')+' is NOT MAPPED')

# Calculate budget for further tests
list_trader=budgetCalculation(list_trader,number_of_traders,logs=True)


# Check that budget available on exchange is compliant 
test_required_budget=list_trader[number_of_traders-1][5]
test_available_budget=kraken.get_balance_EUR()

if(test_available_budget<test_required_budget):
    logger.error("Euros available on exchange ("+str(test_available_budget)+") are not enough to match configuration ("+str(test_required_budget)+")")
    notifier.notify('Fatal Error',"Euros available on exchange ("+str(test_available_budget)+") are not enough to match configuration ("+str(test_required_budget)+")")
    exit(1)
else:
    logger.info("Euros available on exchange ("+str(test_available_budget)+") are enough to match actual configuration("+str(test_required_budget)+")")

# Check if every unit of trading money are to sold
owned_volume_of_traded_money=kraken.get_balance_for_traded_currency(CURRENCY_BALANCE_NAME)
safetyCheckOnTradingCurrencySellingOrder(list_open_orders,owned_volume_of_traded_money)


logger.info("---------------------------------------------------")
logger.info("------- Let's Trade Baby------------------------ ;)")
logger.info("------- Speculator AUTHORIZATION_OF_BUYING mode is :"+str(AUTHORIZATION_OF_BUYING)+" ")
logger.info("---------------------------------------------------")
    
while(1==1):
    # Get current exchange time
    kraken_time=kraken.get_server_unixtime()
    # Check if buying authorization is still active
    AUTHORIZATION_OF_BUYING=bool(os.environ['AUTHORIZATION_OF_BUYING']=='True')
    
    #############################
    # STEP 0 Crawl and store data
    #############################
    crawled_currencies=kraken.get_currency_value(CURRENCY_CRAWLED_NAME)
    currency_actual_ask_price=float(crawled_currencies.get('result').get(CURRENCY_CRAWLED_NAME).get('a')[0])
    if(crawled_currencies != None):
        for currency in crawled_currencies.get('result').keys():
            c=crawled_currencies.get('result').get(currency)
            persistenceHandler.storeCurrency(kraken_time,currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
    logger.info("Crawled values "+str(currency_actual_ask_price)+" for currency "+str(CURRENCY_CRAWLED_NAME))
    time.sleep(15)
    
    ##################################################################
    # STEP 1 Check for closed Orders and perform corresponding actions
    ##################################################################
    # Getting fresh version of the list and compare
    owned_volume=-1.0
    owned_volume_time1=kraken.get_balance_for_traded_currency(CURRENCY_BALANCE_NAME)
    fresh_open_orders=kraken.get_single_open_orders(CURRENCY_ORDER_NAME)
    owned_volume_time2=kraken.get_balance_for_traded_currency(CURRENCY_BALANCE_NAME)
    
    # Getting volume of traded money before and after getting orders. If this value is the same, safety check can be performed.
    if(owned_volume_time1==owned_volume_time2):
        owned_volume=owned_volume_time1
    
    fresh_oe_id_list=[]
    for item in fresh_open_orders:
        fresh_oe_id_list.append(item.get('order_id'))

    DO_STEP2=True
    for oe in list_open_orders:
        if oe.get('order_id') not in fresh_oe_id_list:
            logger.info('Order '+oe.get('order_id')+' is not in fresh open order list')
            DO_STEP2=False
            # Get details about closed orders for notification
            closed_orders=kraken.get_closed_orders(persistenceHandler,step_between_unit_sell_and_unit_price)
            coe=closed_orders.get(oe.get('order_id'))
            price=float(coe.get('price'))
            volume=float(coe.get('vol'))
            status=str(coe.get('status'))
            descr=str(coe.get('descr'))
            order_type=str(coe.get('descr').get('type'))
            executed_volume=float(coe.get('vol_exec'))
            is_buying_order_canceled_and_partially_executed=False
            # Creating flag for buying order canceled but partially executed
            if(order_type==BUYING and status==CANCELED and executed_volume>0):
                is_buying_order_canceled_and_partially_executed=True
                
            opening_date=str(coe.get('opentm'))
            closing_date=str(coe.get('closetm'))

            # Don't send notification and dont store  cancel order
            if(status!=CANCELED or is_buying_order_canceled_and_partially_executed==True):
                # Notify
                if(NOTIFY_ON_CLOSED_ORDERS==True):
                    specific_text=""
                    if(is_buying_order_canceled_and_partially_executed==True):
                        specific_text="PARTIALLY EXECUTED CANCEL "
                    notifier.notify(specific_text+'Order '+oe.get('order_id')+' '+str.upper(status),descr)

            logger.info('Order '+oe.get('order_id')+' '+str.upper(status)+" "+descr)
            
            # If an BUY order was CLOSED( or CANCELED but partially processed), search the concerned speculator to create sell order
            if(oe.get('type')==BUYING or oe.get('type')==SELLING):
                logger.info("order "+str(oe.get('order_id'))+" just closed, searching trader")
                for index in range(0,number_of_traders):
                    if(list_trader[index][4]==BUYING and list_trader[index][3]==oe.get('order_id') and (status==CLOSED or is_buying_order_canceled_and_partially_executed==True) ):
                        logger.info("1/ "+str(BUYING)+" order "+oe.get('order_id')+" was originally created by trader "+str(index)+".")
                        if(is_buying_order_canceled_and_partially_executed==True):
                            logger.info("- Specific case of selling order creation after cancelation of partially executed buying order")
                        ########################
                        # CREATING SELLING ORDER
                        ########################
                        # Get available amount of currency
                        volume_buyed_to_sell=kraken.get_closed_order_volume_by_id(oe.get('order_id'),persistenceHandler,step_between_unit_sell_and_unit_price)
                        logger.info("Volume to sell is :"+str(volume_buyed_to_sell))
                        if(volume_buyed_to_sell>0.0):
                            unit_selling_price=round(list_trader[index][2]+step_between_unit_sell_and_unit_price,2)
                            logger.info("Unit sell price is:"+str(unit_selling_price))
                            # Selling order:
                            created_selling_order=kraken.secure_sell(volume_buyed_to_sell,unit_selling_price,CURRENCY_CRAWLED_NAME,persistenceHandler,step_between_unit_sell_and_unit_price,CURRENCY_ORDER_NAME)
                            fresh_open_orders.append([str(created_selling_order),SELLING])
                            list_trader[index][3]=str(created_selling_order)
                            list_trader[index][4]=SELLING
                            list_trader[index][5]=0.0
                            # Setting engaged money
                            list_trader[index][6]=calculatedEngagedMoney(volume_buyed_to_sell,unit_selling_price,step_between_unit_sell_and_unit_price)
                            logger.info("Trader "+str(list_trader[index][0])+" is now in mode"+str(list_trader[index][4])+" with order "+str(list_trader[index][3])+". Budget is :"+str(list_trader[index][5]))
                            break;
                    if(list_trader[index][3]==oe.get('order_id') and ((list_trader[index][4]==SELLING) or ((list_trader[index][4]==BUYING) and (status==CANCELED)))):
                        logger.info("2/ "+str(list_trader[index][4])+" order "+oe.get('order_id')+" was originally created by trader "+str(index)+".")
                        ####################################################
                        # MANAGE SELL ENJOYMENT, OR BUY CANCELATION
                        ####################################################
                        flag_benefit=False
                        if(list_trader[index][4]==SELLING):
                            flag_benefit=True
                            
                        list_trader[index][3]=None
                        list_trader[index][4]=WAITING
                        # Budget will be calculated in the iteration
                        list_trader[index][5]=0.0
                        list_trader[index][6]=0.0
                        logger.info("Trader "+str(list_trader[index][0])+" is now in mode"+str(WAITING))
                        
                        # Special notification if to give you benefits
                        if(flag_benefit):
                            try:
                                benefits=businessLogic.estimate_benefits(list_trader[index][2],volume,round(list_trader[index][2]+step_between_unit_sell_and_unit_price,2))
                                todays_benefits=businessLogic.calculate_today_benefits(persistenceHandler.get_todays_benefits())
                                logger.info("Todays Benefits are "+str(todays_benefits))
                                notifier.notify(";) Congrats","If configuration did t change, Benefits are little bit under "+str(benefits)+"€\nTotal for today :"+str(todays_benefits[1])+"€ (in "+str(todays_benefits[0])+" trades)")
                                logger.info("CONGRATULATIONS !!! Benefits are little bit under "+str(benefits)+"€")
                                logger.info("---------------------Total for today-> "+str(todays_benefits[1])+"€ ("+str(todays_benefits[0])+" trades)")
                            except Exception as e:
                                logger.info("fail to send Special notification for benefit. error was "+str(e))
                        break;

    # Finally setup open order to freshest list
    list_open_orders=fresh_open_orders
    time.sleep(15)

    
    if(DO_STEP2==True):
        
        # Safety check (only if owned_value > 0 (if =-1 it means that it change during time when we get open orders))
        if(owned_volume>0.0):
            safetyCheckOnTradingCurrencySellingOrder(list_open_orders,owned_volume)
        else:
            logger.info("Safety check is not going to be performed ( owned_volume="+str(owned_volume)+")")
        
        ##########################
        # Traders
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
            df2=persistenceHandler.get_Trends_time_series(kraken_time,CURRENCY_CRAWLED_NAME,2)
            df5=persistenceHandler.get_Trends_time_series(kraken_time,CURRENCY_CRAWLED_NAME,5)
            df10=persistenceHandler.get_Trends_time_series(kraken_time,CURRENCY_CRAWLED_NAME,10)
            # I take 16 mins to be sure having at least 14.5 mins
            df15=persistenceHandler.get_Trends_time_series(kraken_time,CURRENCY_CRAWLED_NAME,16)
            
            trends2_is_growing=businessLogic.it_market_increasing(df2)
            trends5_is_growing=businessLogic.it_market_increasing(df5)
            trends10_is_growing=businessLogic.it_market_increasing(df10)
            trends15_is_growing=businessLogic.it_market_increasing(df15)
            
            delay_covered=(max(df15.index) - min(df15.index)).seconds
            logger.info('Covered delay = '+str(round( (delay_covered/60) ,2))+' mins / Trend data:  (T2:'+str(len(df2))+' elems),(T5:'+str(len(df5))+' elems),(T10:'+str(len(df10))+' elems),(T15='+str(len(df15))+' elems)')
            
            # Checking if trend is reliable
            if(len(df2)>2 and len(df5)>5 and len(df10)>10 and len(df15)>15 and (delay_covered/60.0)>=14.5):
                if(trends2_is_growing and trends5_is_growing and trends10_is_growing and trends15_is_growing):
                # Checking that trends number is enough:
                    logger.info("Market is good right now ")
                    IS_TREND_GROWING=True
                else:
                    logger.info("Market is not good at this time ")
            else:
                logger.warn("Number of data for trends is not reliable")
      
        # If market is growing and no one is buying, check bugdet
        if(IS_TREND_GROWING==True and EXISTS_OPEN_BUYING_ORDERS==False):
            logger.info("Market is OK, and no buying orders open : time to shop a little bit ! ")
            # calculate budget, get the right trader  and launch buying
            list_trader=budgetCalculation(list_trader,number_of_traders,logs=True)
            
            #Check if the speculator has right to buy:
            if AUTHORIZATION_OF_BUYING==True and currency_actual_ask_price>=minimum_buying_price:
                logger.info("Remember : Speculator is allowed to trade")
                # /!\ check from lowest trader to higher trader is essential
                SELECTED_TRADER_ID_FOR_BUYING=-1
                for index in range(number_of_traders-1,-1,-1):
                    # If trader's buy price is higher than value price we have the right trader
                    if(list_trader[index][2]>=currency_actual_ask_price):
                        # index of selected trader is index+1 (lower )
                        ###################
                        # SET BUYING ORDER
                        ##################
                        SELECTED_TRADER_ID_FOR_BUYING=index+1
                        # Checking it trader is available:
                        if(list_trader[SELECTED_TRADER_ID_FOR_BUYING][4]==WAITING):
                            # Calculate volume to buy
                            volume_to_buy=businessLogic.get_maximum_volume_to_buy_with_budget( round( list_trader[SELECTED_TRADER_ID_FOR_BUYING][5],2),list_trader[SELECTED_TRADER_ID_FOR_BUYING][2] )
                            logger.info("Trader "+str(SELECTED_TRADER_ID_FOR_BUYING)+' was selected to buy at '+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][2])+" because market price is "+str(currency_actual_ask_price))
                            logger.info("          budget is going to be "+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][5])+"€")
                            logger.info("          buying volume :"+str(volume_to_buy))
                            logger.info("          For further analysis, unix time is "+str(kraken_time))
                        
                            # create buying order
                            created_buying_order=kraken.secure_buy(volume_to_buy,list_trader[SELECTED_TRADER_ID_FOR_BUYING][2],CURRENCY_CRAWLED_NAME,persistenceHandler,step_between_unit_sell_and_unit_price,CURRENCY_ORDER_NAME)
                            logger.info("Buying order "+created_buying_order.get('order_id')+" was created")
                            list_open_orders.append(created_buying_order)
                            # /!\set up right status and cut budget setup selling order 
                            list_trader[SELECTED_TRADER_ID_FOR_BUYING][3]=created_buying_order.get('order_id')
                            list_trader[SELECTED_TRADER_ID_FOR_BUYING][4]=BUYING
                            list_trader[SELECTED_TRADER_ID_FOR_BUYING][5]=0.0
                            # setup buying mode to avoir other buy attempt
                            EXISTS_OPEN_BUYING_ORDERS=True
                        else:
                            logger.info("Speculator wanted with trader "+str(SELECTED_TRADER_ID_FOR_BUYING)+" is already in "+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][4])+" mode")
                        break;
            else:
                logger.info("Speculator is actually in mode AUTHORIZATION_OF_BUYING==False")
        else:
            if(EXISTS_OPEN_BUYING_ORDERS==True):
                # On ne verifie pas l'ordre du top trader (on ne peut rien faire de toute manière)
                if(BUYING_TRADER_ID>0):
                    logger.info("Check if Trader "+str(BUYING_TRADER_ID)+" buying order has still potential to reach ")
                    # check if order is ok
                    buying_trader=list_trader[BUYING_TRADER_ID]
                    upper_buying_trader=list_trader[BUYING_TRADER_ID-1]
                    if(buying_trader[0]==BUYING_TRADER_ID and upper_buying_trader[0]==BUYING_TRADER_ID-1):
                        # Control is : market price has to be - upper or  equals to buyer unit price
                        if(buying_trader[2]<= currency_actual_ask_price  and currency_actual_ask_price<upper_buying_trader[2] ):
                            logger.info('Order is still rightly placed : (buyer price  '+str(buying_trader[2])+') <= (market price '+str(currency_actual_ask_price)+') < ( upper buyer price '+str(upper_buying_trader[2])+')')
                        else:
                            #############################
                            # CANCEL MISPLACED ORDER
                            #############################
                            logger.info('Order no more smartly placed : following condition is not true anymore:\n (buyer price  '+str(buying_trader[2])+') <= (market price '+str(currency_actual_ask_price)+') < ( upper buyer price '+str(upper_buying_trader[2])+')')
                            result=kraken.secure_cancel_order(CURRENT_BUYING_ORDER_ID)
                            if(result!=DONE):
                                logger.error('Can t cancel order '+str(CURRENT_BUYING_ORDER_ID))
                                notifier.notify('Fatal Error','Can t cancel order '+str(CURRENT_BUYING_ORDER_ID))
                                exit(1)
                            else:
                                logger.info('Setting EXISTS_OPEN_BUYING_ORDERS to False')
                                EXISTS_OPEN_BUYING_ORDERS=False
                    else:
                        logger.error("Technical Issue, trader tab is corrupted")

