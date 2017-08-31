#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 09:15:29 2017

@author: dboudeau
"""

import persistenceHandler
import businessLogic
import pandas
import exchange_krakken as kraken
from sqlalchemy import create_engine
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pylab as pl
import numpy
from matplotlib import pyplot as plt


currency='XXRPZEUR'
kraken.init()
#init_time=kraken.get_server_unixtime()


# Init parameters
#engine = create_engine('postgresql://azalead:azalead@localhost:5432/speculator')    
#conn = engine.connect()

#epoch=0
#for now in range(init_time-244800,init_time,60):
#    print("Epoch "+str(epoch))
#    market_price=persistenceHandler.get_ask_price_at_momentum(now,currency)
#    ts2=persistenceHandler.get_Trends_time_series(now,currency,2)
#    ts5=persistenceHandler.get_Trends_time_series(now,currency,5)
#    ts10=persistenceHandler.get_Trends_time_series(now,currency,10)
#    ts15=persistenceHandler.get_Trends_time_series(now,currency,15)
#    ts20=persistenceHandler.get_Trends_time_series(now,currency,20)
#    ts40=persistenceHandler.get_Trends_time_series(now,currency,40)
#    ts60=persistenceHandler.get_Trends_time_series(now,currency,60)
#    
#    
#    trend2 =businessLogic.it_market_increasing(ts2) 
#    trend5 =businessLogic.it_market_increasing(ts5)
#    trend10=businessLogic.it_market_increasing(ts10)
#    trend15=businessLogic.it_market_increasing(ts15)
#    trend20=businessLogic.it_market_increasing(ts20)
#    trend40=businessLogic.it_market_increasing(ts40)
#    trend60=businessLogic.it_market_increasing(ts60)
#    
#    t2='red'
#    t5='red'
#    t10='red'
#    t15='red'
#    t20='red'
#    t40='red'
#    t60='red'
#    if(trend2):
#        t2='green'
#    if(trend5):
#        t5='green'
#    if(trend10):
#        t10='green'
#    if(trend15):
#        t15='green'
#    if(trend20):
#        t20='green'
#    if(trend40):
#        t40='green'        
#    if(trend60):
#        t60='green'        
#        
#        
#    print("Is market Growing on 2  :"+str(trend2))
#    print("Is market Growing on 5  :"+str(trend5))
#    print("Is market Growing on 10 :"+str(trend10))
#    print("Is market Growing on 15 :"+str(trend15))
#    print("Is market Growing on 20 :"+str(trend20))
#    print("Is market Growing on 40 :"+str(trend40))
#    print("Is market Growing on 60 :"+str(trend60))
#    sql="insert into analysis(momentum,price,buy2,buy5,buy10,buy15,buy20,buy40,buy60) values ( to_timestamp("+str(now)+"),"+str(market_price)+",'"+t2+"','"+t5+"','"+t10+"','"+t15+"','"+t20+"','"+t40+"','"+t60+"')"
#    print(sql)
#    conn.execute(sql)
#    epoch=epoch+1


#
## Get crawled values from 10 last mins
#sql="""select * from analysis order by momentum asc;"""
#df_last_minutes=pandas.read_sql(sql,conn)
#df_last_minutes.momentum=pandas.to_datetime(df_last_minutes.momentum)
#df_last_minutes.price=df_last_minutes.price.astype(float)
#df_last_minutes.buy5=df_last_minutes.buy5.astype(str)
#
#
#
#
#color_d = {'green': 'g', 'red': 'r'}
#
#df_last_minutes_g = df_last_minutes[df_last_minutes['buy5'] == 'green']
#df_last_minutes_r = df_last_minutes[df_last_minutes['buy5'] == 'red']
#df_last_minutes.buy5.map(color_d)
#plt.figure(1)
#plt.plot(df_last_minutes.momentum.values, df_last_minutes.price.values, 'b')
#plt.plot(df_last_minutes_g.momentum.values, df_last_minutes_g.price.values,'x', c='g')
#plt.plot(df_last_minutes_r.momentum.values, df_last_minutes_r.price.values,'x', c='r')
#
#df_last_minutes_g = df_last_minutes[df_last_minutes['buy10'] == 'green']
#df_last_minutes_r = df_last_minutes[df_last_minutes['buy10'] == 'red']
#df_last_minutes.buy10.map(color_d)
#plt.figure(2)
#plt.plot(df_last_minutes.momentum.values, df_last_minutes.price.values, 'b')
#plt.plot(df_last_minutes_g.momentum.values, df_last_minutes_g.price.values,'x', c='g')
#plt.plot(df_last_minutes_r.momentum.values, df_last_minutes_r.price.values,'x', c='r')
#
#df_last_minutes_g = df_last_minutes[df_last_minutes['buy15'] == 'green']
#df_last_minutes_r = df_last_minutes[df_last_minutes['buy15'] == 'red']
#df_last_minutes.buy15.map(color_d)
#plt.figure(3)
#plt.plot(df_last_minutes.momentum.values, df_last_minutes.price.values, 'b')
#plt.plot(df_last_minutes_g.momentum.values, df_last_minutes_g.price.values,'x', c='g')
#plt.plot(df_last_minutes_r.momentum.values, df_last_minutes_r.price.values,'x', c='r')
#
#
#df_last_minutes_g = df_last_minutes[df_last_minutes['buy20'] == 'green']
#df_last_minutes_r = df_last_minutes[df_last_minutes['buy20'] == 'red']
#df_last_minutes.buy20.map(color_d)
#plt.figure(4)
#plt.plot(df_last_minutes.momentum.values, df_last_minutes.price.values, 'b')
#plt.plot(df_last_minutes_g.momentum.values, df_last_minutes_g.price.values,'x', c='g')
#plt.plot(df_last_minutes_r.momentum.values, df_last_minutes_r.price.values,'x', c='r')
#
#
#def transform(row):
#    if(row['buy2']==row['buy5'] and row['buy5']==row['buy10'] and row['buy10']==row['buy15'] and row['buy5']=='green'):
#        return 'green'
#    else:
#        return 'red'
#
#df_last_minutes['test']=df_last_minutes.apply( lambda row:transform(row),axis=1)
#
#
#
#df_last_minutes_g = df_last_minutes[df_last_minutes['test'] == 'green']
#df_last_minutes_r = df_last_minutes[df_last_minutes['test'] == 'red']
#df_last_minutes.test.map(color_d)
#plt.figure(5)
#plt.plot(df_last_minutes.momentum.values, df_last_minutes.price.values, 'b')
#plt.plot(df_last_minutes_g.momentum.values, df_last_minutes_g.price.values,'x', c='g')
#plt.plot(df_last_minutes_r.momentum.values, df_last_minutes_r.price.values,'x', c='r')
#
#
#plt.show()
##c=ts_b5
##ax.scatter(df_last_minutes.momentum.values, df_last_minutes.price.values)
#
#
##df_last_minutes.plot(kind='scatter', x='momentum', y='price')
#
##plt.scatter(df_last_minutes.momentum,df_last_minutes.price)
#
#
## CA CA MARCHE df_last_minutes.plot(x='momentum', y='price', style=".",c='r')




## Rattrapage des ordres qui n'avaient pas été enregistrés
#rattrapage=[]
#
#closed_orders=kraken.get_closed_orders()
#for coeid in rattrapage:
#    coe=closed_orders.get(coeid)
#    price=float(coe.get('price'))
#    volume=float(coe.get('vol'))
#    status=str(coe.get('status'))
#    descr=str(coe.get('descr'))
#    opening_date=str(coe.get('opentm'))
#    closing_date=str(coe.get('closetm'))
#    ttype=str(coe.get('descr').get('type'))
#    persistenceHandler.storeClosedOrder(coeid,opening_date,closing_date,price,volume,ttype,status)

