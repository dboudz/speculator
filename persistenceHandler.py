#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 21:20:20 2017

@author: dboudeau
"""
from sqlalchemy import create_engine
import pandas
import os
import logging

# Logging Management
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# Init parameters
engine = create_engine(os.environ["DATABASE_URL"])    
conn = engine.connect()

def getCrawling(currency=""):
    if(len(currency)>0):
        currency=" and currency in ('"+currency+"') "
    df=pandas.read_sql('select * from crawling where 1=1 '+currency+' order by currency_date ',conn)
    return df 
    

def initDB():
    # Create table for currency crawling
    logger.debug("create if not exist table crawling")
    sql_create_crawling_table="""
    create table if not exists
    crawling(
        currency_date timestamp without time zone,
        currency character varying,
        ask_price float,
        ask_whole_lot_volume float,
        ask_lot_volume float,
        bid_price float,
        bid_whole_lot_volume float,
        bid_lot_volume float,
        last_trade_closed_price float,
        last_trade_closed_volume float,
        volume_today float,
        volume_last24h float,
        volume_weight_today float,
        volume_weight_24h float,
        number_of_trades_today float,
        number_of_trades_24h float,
        low_today float,
        low_24h float,
        high_today float,
        high_24h float,
        opening_price float
    );
    """
    conn.execute(sql_create_crawling_table)

        
    # Create table for currency crawling
    logger.debug("create if not exist table buying signals")
    sql_create_crawling_table="""
    create table if not exists
    buying_signal(
        buying_signal_date timestamp without time zone,
        currency character varying,
        ask_price float
    );
    """
    conn.execute(sql_create_crawling_table)

    
    #df = pd.read_sql_query("select * from lol2 limit 5;", conn)
    
#    a = ask array(<price>, <whole lot volume>, <lot volume>),
#    b = bid array(<price>, <whole lot volume>, <lot volume>),
#    c = last trade closed array(<price>, <lot volume>),
#    v = volume array(<today>, <last 24 hours>),
#    p = volume weighted average price array(<today>, <last 24 hours>),
#    t = number of trades array(<today>, <last 24 hours>),
#    l = low array(<today>, <last 24 hours>),
#    h = high array(<today>, <last 24 hours>),
#    o = today's opening price



def storeBuyingSignal(timestamp,currency,ask_price):
    
    sql_check="""SELECT COUNT(*) as counter from buying_signal 
    where 
    buying_signal_date='"""+str(timestamp)+"""'
    and currency='"""+str(currency)+"""'
    and ask_price="""+str(ask_price)+"""
    """
    
    df=pandas.read_sql(sql_check,conn)
    if(int(df.iloc[0]['counter'])>0):
        logger.debug("Record already exists")
        return 0
    else:
        sql_insert=""" INSERT INTO buying_signal(buying_signal_date,currency,ask_price) VALUES
        ('"""+str(timestamp)+"""','"""+str(currency)+"""',"""+str(ask_price)+""")"""
        conn.execute(sql_insert)
        return(1)
    

def storeCurrency(currency,ask_array,bid_array,last_trade_closed_array,volume_array,volume_weighted_average_price_array,number_of_trades_array,low_array,high_array,today_opening_price):
    
    sql_insert=""" INSERT INTO crawling(
    currency_date,
    currency,
    ask_price,
    ask_whole_lot_volume,
    ask_lot_volume,
    bid_price,
    bid_whole_lot_volume,
    bid_lot_volume,
    last_trade_closed_price,
    last_trade_closed_volume,
    volume_today,
    volume_last24h,
    volume_weight_today,
    volume_weight_24h,
    number_of_trades_today,
    number_of_trades_24h,
    low_today,
    low_24h,
    high_today,
    high_24h,
    opening_price
    )
    values
    (
    now(),
    '"""+currency+"""',
    """+str(ask_array[0])+""",
    """+str(ask_array[1])+""",
    """+str(ask_array[2])+""",
    """+str(bid_array[0])+""",
    """+str(bid_array[1])+""",
    """+str(bid_array[2])+""",
    """+str(last_trade_closed_array[0])+""",
    """+str(last_trade_closed_array[1])+""",
    """+str(volume_array[0])+""",
    """+str(volume_array[1])+""",
    """+str(volume_weighted_average_price_array[0])+""",
    """+str(volume_weighted_average_price_array[1])+""",
    """+str(number_of_trades_array[0])+""",
    """+str(number_of_trades_array[1])+""",
    """+str(low_array[0])+""",
    """+str(low_array[1])+""",
    """+str(high_array[0])+""",
    """+str(high_array[1])+""",
    """+str(today_opening_price)+"""
    )
    """
    conn.execute(sql_insert)
initDB()