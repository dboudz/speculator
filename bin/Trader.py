#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 21:42:09 2017

@author: dbo
"""

class Trader:
    # Initialize traders
    WAITING='wait'
    SELLING='sell'
    BUYING='buy'
    def __init__(self,id,budget,buying_price):
                
        self.id = id
        self.budget =0.0
        self.buying_price=buying_price
        self.order_id=None
        self.status = self.WAITING
        self.available_budget = 0.0
        self.engaged_budget
        
