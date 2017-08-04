#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 23:30:10 2017

@author: dboudeau
"""
import logging
import math


# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Business Variables
MINIMUM_XRP_VOLUME=30
SELL_STEP=0.0001
FEE_PERCENTAGE=0.16


def check_traders_configuration(list_trader,step_between_unit_sell_and_unit_price,expected_gain_by_band,allowed_budget):
    is_config_viable=True
    #Checking theoric viability of each traders
    test_budget=0.0
    for trader in list_trader:
        isViable=can_I_setup_like_this_to_respect_objective_and_step( trader[2],step_between_unit_sell_and_unit_price,trader[1],expected_gain_by_band)
        if(isViable==False):
            is_config_viable=False
            logger.error("Configuration of trader "+str(trader[0])+"  is not valid.")
        test_budget=test_budget+trader[1]
        
    #Checking theoric viability of global Budget
    if(test_budget!=allowed_budget):
        is_config_viable=False
        logger.error("Sum of trader budget ("+str(test_budget)+") is different of globa budget("+str(allowed_budget)+")")
    return is_config_viable

def calculate_fee(budget):
    return(budget/100)*FEE_PERCENTAGE

def get_maximum_volume_to_buy_with_budget(budget,unit_price):
    budget_minus_fee=budget - calculate_fee(budget)
    max_buy_volume=math.floor(budget_minus_fee/unit_price)
    logger.info('Maximum buy volume is '+str(max_buy_volume))
    return max_buy_volume

def can_I_setup_like_this_to_respect_objective_and_step(initial_unit_price,step_sell,budget_all_inclusive,expected_gain):
    maximum_volume_with_budget=get_maximum_volume_to_buy_with_budget(budget_all_inclusive,initial_unit_price)
    minimum_unit_sell_price=calculate_minimum_sell_price_to(maximum_volume_with_budget,initial_unit_price,expected_gain)
    
    if(minimum_unit_sell_price>(initial_unit_price+step_sell)):
        logger.info('Not possible, missing '+str(minimum_unit_sell_price-(initial_unit_price+step_sell)))
        return False
    else:
        logger.info('Sell is possible for minimum unit price '+str(minimum_unit_sell_price))
        return True
    
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
    logger.info('Minimum unit sell price to fit the objective is '+str(unit_sell_price))
    return unit_sell_price
   