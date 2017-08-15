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

# Ajouter un consumed budget qui permettra en cas d'upgrade de bénéficier du budget sup
# Ajouter le controle de cohérence entre le portefeuille XRP 
# : sum (volume selling order) = volume xrp
# GERER LE CAS OU UN ORDRE EST CLOS QUAND LE SPECULATOR EST DOWN.
# TODO SI N ORDRE DE VENTE MANQUE IL FAUT GERER CA ! cf requete unclosed trade
# TODO Ajouter un controle pour vérfier que la position sur la monnaie tradée est ok avec les speculators
# IMPROVEMENT caculer les bénéfices pour les remettre dans le panier de trade

# Var initialization
AUTHORIZATION_OF_BUYING=bool(os.environ['AUTHORIZATION_OF_BUYING']=='True')
CRAWLED_CURRENCIES=os.environ['CRAWLED_CURRENCIES']
NOTIFY_ON_CLOSED_ORDERS=bool(os.environ['NOTIFY_ON_CLOSED_ORDERS']=='True')

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


kraken.init()
list_open_orders_with_ids=kraken.get_open_orders_ids_and_type()
DONE=0
NOT_DONE=1



####################11
# Initialize traders
WAITING='wait'
SELLING='sell'
BUYING='buy'
TRADING_CURRENCY='XXRPZEUR'
CLOSED='closed'
CANCELED='canceled'


sequence_number=-1
def increment_sequence():
    global sequence_number
    sequence_number=sequence_number+1
    return sequence_number


def budgetCalculation(list_trader):
    logger.info("------Begin calculating the budget for each trader before buying----")
    available_budget=0
    for index in range(0,number_of_traders):
        # Define budget available for current trader 
        if(list_trader[index][4]==WAITING):
            available_budget=available_budget+list_trader[index][1]
            list_trader[index][5]=available_budget
        else:
            list_trader[index][5]=0.0
            logger.debug('Trader '+str(index)+' is in '+list_trader[index][4]+' mode and has no budget to provide ')
            logger.debug('Budget for above traders is going to be removed !')
            for index_above_trader in range(index,-1,-1):
                list_trader[index_above_trader][5]=0.0
                #logger.debug('Trader '+str(index_above_trader)+' budget removed because  below Trader '+str(index)+' is in '+str(list_trader[index][4])+' mode')
                available_budget=0
    # Display budget
    logger.info("------Display of Final budget ----")
    for index in range(0,number_of_traders):
        logger.info('Trader '+str(index)+', buyer at '+str(list_trader[index][2])+' is in '+str.upper(list_trader[index][4])+' mode with a budget of '+str(list_trader[index][5])+" engaged money is "+str(list_trader[index][6]))
    logger.info("------End of Budget Calculation----")
    return list_trader

# trader (integerId,budget(€),buy_unit_price,buying_order,Status,available_budget,engaged_budget
allowed_budget=617.0
expected_gain_by_band=0.05
number_of_traders=39
# NEVER CHANGE THIS ONE IF EXISTING SELLING ORDER
step_between_unit_sell_and_unit_price=0.001
minimum_buying_price=0.124
# Available 69
       
list_trader=[]
list_trader.append([increment_sequence(),17.0,0.162,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,0.161,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,0.160,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,0.159,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),17.0,0.158,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.157,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.156,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.155,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.154,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.153,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),16.0,0.152,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),15.0,0.151,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),19.0,0.150,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),20.0,0.149,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,0.148,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),25.0,0.147,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,0.146,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,0.145,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,0.144,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),24.0,0.143,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),14.0,0.142,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),14.0,0.141,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.140,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.139,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.138,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.137,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.136,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.135,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),13.0,0.134,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.133,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.132,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.131,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.130,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.129,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.128,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),12.0,0.127,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),11.0,0.127,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),11.0,0.125,None,WAITING,0.0,0.0])
list_trader.append([increment_sequence(),11.0,0.124,None,WAITING,0.0,0.0])



# Check viability of configuration
if(False==businessLogic.check_traders_configuration(kraken.get_balance_EUR(),number_of_traders,list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget)):
    logger.error("Configuration of traders is not valid. Exiting")
    notifier.notify('Fatal Error',"Configuration of traders is not valid. Exiting")
    exit(1)
else:
    logger.info("[V] Configuration of trader is valid [V]")


## Closing All buying orders (security)
for order_with_type in list_open_orders_with_ids:
    if(order_with_type[1]==BUYING):
        logger.info("Buying Order "+str(order_with_type[0])+" is going to be cancel by speculator initialization")
        if(kraken.secure_cancel_order(order_with_type[0])==DONE):
            logger.info("Buying Order "+str(order_with_type[0])+" was closed at initialization of speculator")
        else:
            logger.error("Buying Order "+str(order_with_type[0])+" coundn't be closed at initialization of speculator")
            notifier.notify('Fatal Error',"Buying Order "+str(order_with_type[0])+" was closed at initialization of speculator")
            exit(1)
## Reinitializing buying list:
list_open_orders_with_ids=kraken.get_open_orders_ids_and_type()

# Map current orders with traders.
for open_selling_order in kraken.get_open_orders_selling_with_unit_sell_price_and_volume():
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
            # Engaged money is selling volume*unit buy_price + fees
            list_trader[index][6]=open_selling_order[2]*list_trader[index][2]+ businessLogic.calculate_fee(open_selling_order[2]*list_trader[index][2])
        if(is_order_mapped):
            break;
    if is_order_mapped==False:
        logger.info('Order '+str(open_selling_order[0])+' is NOT MAPPED')

# Calculate budget for further tests
list_trader=budgetCalculation(list_trader)


# Check that budget available on exchange is compliant 
test_required_budget=list_trader[number_of_traders-1][5]
test_available_budget=kraken.get_balance_EUR()

if(test_available_budget<test_required_budget):
    logger.error("Euros available on exchange ("+str(test_available_budget)+") are not enough to match configuration ("+str(test_required_budget)+")")
    notifier.notify('Fatal Error',"Euros available on exchange ("+str(test_available_budget)+") are not enough to match configuration ("+str(test_required_budget)+")")
    exit(1)
else:
    logger.info("Euros available on exchange ("+str(test_available_budget)+") are enough to match actual configuration("+str(test_required_budget)+")")



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
    crawled_currencies=kraken.get_currency_value(CRAWLED_CURRENCIES)
    currency_actual_ask_price=float(crawled_currencies.get('result').get(TRADING_CURRENCY).get('a')[0])
    if(crawled_currencies != None):
        for currency in crawled_currencies.get('result').keys():
            c=crawled_currencies.get('result').get(currency)
            persistenceHandler.storeCurrency(kraken_time,currency,c.get('a'),c.get('b'),c.get('c'),c.get('v'),c.get('p'),c.get('t'),c.get('l'),c.get('h'),c.get('o'))
    logger.info("Crawled values "+str(currency_actual_ask_price)+" for currency "+str(CRAWLED_CURRENCIES))
    time.sleep(15)
    
    ##################################################################
    # STEP 1 Check for closed Orders and perform corresponding actions
    ##################################################################
    # Getting fresh version of the list and compare
    fresh_open_orders_ids_list=kraken.get_open_orders_ids_and_type()
    fresh_oe_id_list=[]
    fresh_oe_buyint_id_list=[]
    for elem in fresh_open_orders_ids_list:
        fresh_oe_id_list.append(elem[0])
        if(elem[1]==BUYING):
            fresh_oe_buyint_id_list.append(elem[0])
            
    # Test number of buying orders
    if(len(fresh_oe_buyint_id_list)>1):
        logger.error("More than 1 buying order detected")
        notifier.notify("Fatal Error","More than 1 buying order detected "+str(fresh_oe_buyint_id_list))
        logger.error("Trying to cancel everything before shutdown")
        for oetc in fresh_oe_buyint_id_list:
            res=NOT_DONE
            while(res!=DONE):
                res=kraken.secure_cancel_order(oetc)
        logger.error("Exiting")
        exit(1)
    
    DO_STEP2=True
    for oe in list_open_orders_with_ids:
        if oe[0] not in fresh_oe_id_list:
            logger.info('Order '+oe[0]+' is not in fresh open order list')
            DO_STEP2=False
            # Get details about closed orders for notification
            closed_orders=kraken.get_closed_orders()
            coe=closed_orders.get(oe[0])
            price=float(coe.get('price'))
            volume=float(coe.get('vol'))
            status=str(coe.get('status'))
            descr=str(coe.get('descr'))
            opening_date=str(coe.get('opentm'))
            closing_date=str(coe.get('closetm'))

            # Don't send notification and dont store  cancel order
            if(status!=CANCELED):
                # Notify
                if(NOTIFY_ON_CLOSED_ORDERS==True):
                    notifier.notify('Order '+oe[0]+' '+str.upper(status),descr)
                # Persist closing order
                persistenceHandler.storeClosedOrder(oe[0],opening_date,closing_date,price,volume,oe[1],status)

            logger.info('Order '+oe[0]+' '+str.upper(status)+" "+descr)
            list_knowned_open_orders_with_ids=kraken.get_open_orders_ids_and_type()
            
            # If an BUY order was CLOSED( not CANCELED), search the concerned speculator to create sell order

            if(oe[1]==BUYING or oe[1]==SELLING):
                logger.info("order "+str(oe[0])+" just closed, searching trader")
                for index in range(0,number_of_traders):
                    if(list_trader[index][4]==BUYING and list_trader[index][3]==oe[0] and status==CLOSED ):
                        logger.info("1/ "+str(BUYING)+" order "+str(oe[0])+" was originally created by trader "+str(index)+".")
                        ########################
                        # CREATING SELLING ORDER
                        ########################
                        # Get available amount of currency
                        volume_buyed_to_sell=kraken.get_closed_order_volume_by_id(oe[0])
                        logger.info("Volume to sell is :"+str(volume_buyed_to_sell))
                        if(volume_buyed_to_sell>0.0):
                            unit_selling_price=list_trader[index][2]+step_between_unit_sell_and_unit_price
                            logger.info("Unit sell price is:"+str(unit_selling_price))
                            # Selling order:
                            created_selling_order=kraken.secure_sell(volume_buyed_to_sell,unit_selling_price)
                            fresh_open_orders_ids_list.append([str(created_selling_order),SELLING])
                            list_trader[index][3]=str(created_selling_order)
                            list_trader[index][4]=SELLING
                            list_trader[index][5]=0.0
                            logger.info("Trader "+str(list_trader[index][0])+" is now in mode"+str(list_trader[index][4])+" with order "+str(list_trader[index][3])+". Budget is :"+str(list_trader[index][5]))
                            # persist link between buying order & selling order
                            logger.info("Persisting the link between buying order "+str(oe[0])+" and selling order "+str(created_selling_order))
                            persistenceHandler.storeTrade(oe[0],str(created_selling_order),allowed_budget)
                            break;
                    if(list_trader[index][3]==oe[0] and ((list_trader[index][4]==SELLING) or ((list_trader[index][4]==BUYING) and (status==CANCELED)))):
                        logger.info("2/ "+str(list_trader[index][4])+" order "+str(oe[0])+" was originally created by trader "+str(index)+".")
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
                        logger.info("Trader "+str(list_trader[index][0])+" is now in mode"+str(WAITING))
                        
                        # Special notification if to give you benefits
                        if(flag_benefit):
                            try:
                                benefits=businessLogic.estimate_benefits(list_trader[index][2],volume,list_trader[index][2]+step_between_unit_sell_and_unit_price)
                                todays_benefits=businessLogic.calculate_today_benefits(persistenceHandler.get_todays_benefits())
                                logger.info("Todays Benefits are "+str(todays_benefits))
                                notifier.notify(";) Congrats","If configuration did t change, Benefits are little bit under "+str(benefits)+"€\nTotal for today :"+str(todays_benefits[1])+"€ (in "+str(todays_benefits[0])+" trades)")
                                logger.info("CONGRATULATIONS !!! Benefits are little bit under "+str(benefits)+"€")
                                logger.info("---------------------Total for today-> "+str(todays_benefits[1])+"€ ("+str(todays_benefits[0])+" trades)")
                            except Exception as e:
                                logger.info("fail to send Special notification for benefit. error was "+str(e))
                        break;

    # Finally setup open order to freshest list
    list_open_orders_with_ids=fresh_open_orders_ids_list
    time.sleep(15)
    
    
    if(DO_STEP2==True):
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
            df2=persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,2)
            df5=persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,5)
            df10=persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,10)
            # I take 16 mins to be sure having at least 14.5 mins
            df15=persistenceHandler.get_Trends_time_series(kraken_time,TRADING_CURRENCY,16)
            
            trends2_is_growing=businessLogic.it_market_increasing(df2)
            trends5_is_growing=businessLogic.it_market_increasing(df5)
            trends10_is_growing=businessLogic.it_market_increasing(df10)
            trends15_is_growing=businessLogic.it_market_increasing(df15)
            
            delay_covered=(max(df15.index) - min(df15.index)).seconds
            logger.info('Covered delay = '+str(delay_covered/60) +" mins")
            logger.info('Trend data:  (Trend2:'+str(len(df2))+' elems),(Trend5:'+str(len(df5))+' elems),(Trend10:'+str(len(df10))+' elems),(Trend15='+str(len(df15))+' elems)')
            
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
            list_trader=budgetCalculation(list_trader)
            
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
                        # Checking if we are under budget

                        # Checking it trader is available:
                        if(list_trader[SELECTED_TRADER_ID_FOR_BUYING][4]==WAITING):
                            # Calculate volume to buy
                            volume_to_buy=businessLogic.get_maximum_volume_to_buy_with_budget(list_trader[SELECTED_TRADER_ID_FOR_BUYING][5],list_trader[SELECTED_TRADER_ID_FOR_BUYING][2])
                            logger.info("Trader "+str(SELECTED_TRADER_ID_FOR_BUYING)+' was selected to buy at '+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][2])+" because market price is "+str(currency_actual_ask_price))
                            logger.info("          budget is going to be "+str(list_trader[SELECTED_TRADER_ID_FOR_BUYING][5])+"€")
                            logger.info("          buying volume :"+str(volume_to_buy))
                            logger.info("          For further analysis, unix time is "+str(kraken_time))
                        
                            # create buying order
                            created_buying_order=kraken.secure_buy(volume_to_buy,list_trader[SELECTED_TRADER_ID_FOR_BUYING][2])
                            logger.info("Buying order "+str(created_buying_order)+" was created")
                            list_open_orders_with_ids.append([created_buying_order,BUYING])
                            # /!\set up right status and cut budget setup selling order 
                            list_trader[SELECTED_TRADER_ID_FOR_BUYING][3]=created_buying_order
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
                        # TODO Technical security : get open order details  and check them
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

