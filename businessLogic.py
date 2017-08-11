#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 23:30:10 2017

@author: dboudeau
"""
import logging
import math
import numpy as np


# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Business Variables
MINIMUM_XRP_VOLUME=30
SELL_STEP=0.0001
FEE_PERCENTAGE=0.16
DONE=0
NOT_DONE=1

def check_traders_configuration(budget_available_on_exchange,number_of_traders,list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget):
    is_config_viable=True
    # Checking number of traders
    if(len(list_trader)!=number_of_traders):
        is_config_viable=False
        logger.error("Number of declared traders is wrong according to trader list size.")

    # Checking theoric viability of each traders
    test_budget=0.0
    for trader in list_trader:
        isViable=can_I_setup_like_this_to_respect_objective_and_step( trader[2],step_between_unit_sell_and_unit_price,trader[1],expected_gain_by_band)
        if(isViable==False):
            is_config_viable=False
            logger.error("Configuration of trader "+str(trader[0])+"  is not valid.")
        test_budget=test_budget+trader[1]
        
    # Checking theoric viability of global Budget
    if(test_budget!=allowed_budget):
        is_config_viable=False
        logger.error("Sum of trader budget ("+str(test_budget)+") is different of globa budget("+str(allowed_budget)+")")
    
    return is_config_viable

def calculate_fee(budget):
    return (budget/100)*FEE_PERCENTAGE

def estimate_benefits(unit_buy_price,volume,unit_sell_price):
    invest_amount=(unit_buy_price*volume)+calculate_fee(unit_buy_price*volume)
    sell_amount=(unit_sell_price*volume)-calculate_fee(unit_sell_price*volume)
    gain=round(sell_amount-invest_amount,5)
    return gain

def get_maximum_volume_to_buy_with_budget(budget,unit_price):
    budget_minus_fee=budget - calculate_fee(budget)
    max_buy_volume=math.floor(budget_minus_fee/unit_price)
    logger.info('Maximum buy volume is '+str(max_buy_volume))
    return max_buy_volume

#project(42,0.001,0.08,0.163,1000)
def project(nb_traders	,step_between_traders,minimal_trade_benefit,max_unit_buy_price,budget):
    # Check viability : check minimal budget for highest trader
    budget_to_test=budget
    max_unit_buy_price_to_test=max_unit_buy_price
    viability_at_level=True
    budget_viability=True
    minimal_budget=[]
    
    for trader in range(0+1,nb_traders+1):
        if(viability_at_level==False):
            break
        viability_at_level=False
        logger.info(" Testing trader "+str(trader)+" with budget "+str(budget_to_test))
        if(budget_to_test==0):
            logger.error("Budget is 0")
        for current_budget in range(1,budget_to_test+1):
            viability_at_level=can_I_setup_like_this_to_respect_objective_and_step(max_unit_buy_price_to_test,step_between_traders,current_budget,minimal_trade_benefit)
            if(viability_at_level==True):
                logger.info(" trader can respect this setup with a minimal budget of "+str(current_budget))
                budget_to_test=budget_to_test-current_budget
                minimal_budget.append(current_budget)
                break
        if(viability_at_level==False):
            logger.error("Setup is not possible for trader "+str(trader))
            budget_viability=False
        max_unit_buy_price_to_test=max_unit_buy_price_to_test-step_between_traders
    logger.info("Budget viability :"+str(budget_viability)+" - Available money "+str(budget_to_test))
    # If budget is viable, project scenarios
    if(budget_viability==True):
    #Trader	budget	budget cumulé	unit buy price	unit sell price	objectif	gain min 	gain max
        cumulated_budget=0
        unit_bp=max_unit_buy_price
        print("Trader,budget,budget_cumulé,unit_buy_price,unit_sell_price,minimal_benefit,maximal_benefit")
        for trader in range(0+1,nb_traders+1):
            budget=minimal_budget[trader-1]
            cumulated_budget=cumulated_budget+budget
            unit_bp=unit_bp-step_between_traders
            unit_sp=unit_bp+step_between_traders
            minimal_volume=get_maximum_volume_to_buy_with_budget(budget,unit_bp)
            minimal_benefit=estimate_benefits(unit_bp,minimal_volume,unit_sp)
            maximal_volume=get_maximum_volume_to_buy_with_budget(cumulated_budget,unit_bp)
            maximal_benefit=estimate_benefits(unit_bp,maximal_volume,unit_sp)
            print("Trader"+str(trader)+" budget "+str(budget)+" cumulated "+str(cumulated_budget)+" Unit buy price:"+str(unit_bp)+" Unit sell price:"+str(unit_sp)+" Minimal benefit:"+str(minimal_benefit)+" Maximal benefit:"+str(maximal_benefit))

            
    

def can_I_setup_like_this_to_respect_objective_and_step(initial_unit_price,step_sell,budget_all_inclusive,expected_gain):
    maximum_volume_with_budget=get_maximum_volume_to_buy_with_budget(budget_all_inclusive,initial_unit_price)
    minimum_unit_sell_price=calculate_minimum_sell_price_to(maximum_volume_with_budget,initial_unit_price,expected_gain)
    
    if(minimum_unit_sell_price>(initial_unit_price+step_sell)):
        #logger.info('Not possible, missing '+str(minimum_unit_sell_price-(initial_unit_price+step_sell)))
        return False
    else:
        #logger.info('Sell is possible for minimum unit price '+str(minimum_unit_sell_price))
        return True

# return (ask_price:float,slope:float)
def it_market_increasing(ts_last_minutes_ask_price):
    
    # Thanks to ttp://www.emilkhatib.com/analyzing-trends-in-data-with-pandas/
    try:
        coefficients, residuals, _, _, _ = np.polyfit(range(len(ts_last_minutes_ask_price.index)),ts_last_minutes_ask_price.values,1,full=True)
    except Exception as e:
        logger.error('it_market_increasing exception '+str(e))
        logger.error('Protective behavior: sending False for is_trend_positive ')
        return False
    #mse = residuals[0]/(len(ts_last_minutes_ask_price.index))
    #nrmse = np.sqrt(mse)/(ts_last_minutes_ask_price.max() - ts_last_minutes_ask_price.min())
    #logger.debug('Slope ' + str(coefficients[0]))
    #logger.debug('NRMSE: ' + str(nrmse))
    
    #TO IMPROVE tester plus tard la régression linéaire
    #model = pd.ols(y=ts,x=ts.index,intercept=True)
    is_trend_positive=True
    if(coefficients[0]<0):
        is_trend_positive=False
    
    return is_trend_positive

def calculate_minimum_sell_price_to(volume,unit_price,objective=1.0):
    volume=float(volume)
    buy_unit_price=float(unit_price)
    buy_price=round(volume*buy_unit_price,5)
    buy_fee=round((buy_price/100)*FEE_PERCENTAGE,5)

    potential_gain=0
    sell_price=buy_price+(buy_fee*2)
    
    while(potential_gain<objective):
        sell_price=sell_price+SELL_STEP
        sell_fee=(sell_price/100)*FEE_PERCENTAGE
        potential_gain=sell_price-buy_price-buy_fee-sell_fee
        
    unit_sell_price=round( (sell_price/volume) ,5)
    logger.debug('Minimum unit sell price to fit the objective is '+str(unit_sell_price))
    return unit_sell_price

