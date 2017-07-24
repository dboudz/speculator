#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 21:20:20 2017

@author: dboudeau
"""
import sqlite3
from configobj import ConfigObj
import pandas
# Init parameters
config = config = ConfigObj('./config')
db_filename=config['db_filename']
conn = sqlite3.connect(db_filename,timeout=30000)



def getCrawling(currency=""):
    if(len(currency)>0):
        currency=" and currency in ('"+currency+"') "
    df=pandas.read_sql('select * from crawling where 1=1 '+currency+' order by currency_date ',conn)
    return df 
    

def initDB():
    # Create table for currency crawling
    print("create if not exist table crawling")
    sql_create_crawling_table="""
    create table 
    crawling(
        currency_date timestamp,
        currency text,
        ask_price real,
        ask_whole_lot_volume real,
        ask_lot_volume real,
        bid_price real,
        bid_whole_lot_volume real,
        bid_lot_volume real,
        last_trade_closed_price real,
        last_trade_closed_volume real,
        volume_today real,
        volume_last24h real,
        volume_weight_today real,
        volume_weight_24h real,
        number_of_trades_today real,
        number_of_trades_24h real,
        low_today real,
        low_24h real,
        high_today real,
        high_24h real,
        opening_price real
    );
    """
    try:
        conn.execute(sql_create_crawling_table)
        print("Table created")
    except sqlite3.OperationalError:
        print("Table already created")
        
        
    # Create table for currency crawling
    print("create if not exist table buying signals")
    sql_create_crawling_table="""
    create table 
    buying_signal(
        buying_signal_date timestamp,
        currency text,
        ask_price real
    );
    """
    try:
        conn.execute(sql_create_crawling_table)
        print("Table created")
    except sqlite3.OperationalError:
        print("Table already created")
    
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


lol=None

def storeBuyingSignal(timestamp,currency,ask_price):
    
    sql_check="""SELECT COUNT(*) as counter from buying_signal 
    where 
    buying_signal_date='"""+str(timestamp)+"""'
    and currency='"""+str(currency)+"""'
    and ask_price="""+str(ask_price)+"""
    """
    
    df=pandas.read_sql(sql_check,conn)
    if(int(df.iloc[0]['counter'])>0):
        print("Record already exists")
        return 0
    else:
        sql_insert=""" INSERT INTO buying_signal(buying_signal_date,currency,ask_price) VALUES
        ('"""+str(timestamp)+"""','"""+str(currency)+"""',"""+str(ask_price)+""")"""
        conn.execute(sql_insert)
        conn.commit()
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
    datetime('now'),
    """+'"'+currency+'"'+""",
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
    conn.commit()
initDB()