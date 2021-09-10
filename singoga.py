import numpy as np
import pandas as pd
import math
import time
from datetime import timedelta, datetime
import copy
import datetime
import talib 
import numpy as np
import pyupbit
access_key='9nQLNICO2fkCLPA51gUCb05QxdpHtY9mlzkbnt6h'
secret_key='LTNcZ5vPTVBfL4hKUyjQ0o31llqZGNnLpSYjAgCP'
upbit = pyupbit.Upbit(access_key, secret_key)

def 시장가매수(ticker):
    잔고 = upbit.get_balance("KRW")*0.995
    orderbook = pyupbit.get_orderbook(ticker)
    sell_price = orderbook[0]['orderbook_units'][0]['ask_price']
    unit = 잔고
    upbit.buy_market_order(ticker, unit)
def 시장가매도(ticker):
    unit = upbit.get_balance(ticker)
    upbit.sell_market_order(ticker, unit)

def 매수조건식():
    매수조건0=df0['close_y'] >df0['btc180']
    매수조건6= df0['close_x'] > df0['최고가']
    매수조건7 = df0['close_x'].shift(periods=1) < df0['최고가'].shift(periods=1)
    매수조건= 매수조건6 & 매수조건7 & 매수조건0
    return 매수조건[-1]

def 매도조건식():
    
    매도조건6= df0['close_x']/ df0['ewm20'] > 1.03
   
    매도조건0=df0['close_y'] < df0['btc180']
    매도조건=(매도조건6 )

    return 매도조건[-1]

while True:
    btc=pyupbit.get_ohlcv('KRW-BTC', interval="minute1")
    df0 = pyupbit.get_ohlcv('KRW-BCHA', interval="minute1")
    time.sleep(0.1)
    잔고 = upbit.get_balance("KRW")
    time.sleep(0.5)
    btc['종가']=btc['close']
    최고가=[]
    for i in range(0,len(df0['close'])):
        temp=df0['close'][i-20:i].max()
        최고가.append(temp)
        
    df0['최고가']=최고가
    btc['btc180']=btc['종가'].ewm(span=180).mean()  
  
    df0=pd.merge(df0, btc,left_index=True, right_index=True,how='left')
#     df0['EMA20']=talib.EMA(df0['close_x'], timeperiod=20)
#     df0['MA20']=df0['close_x'].rolling(window=20).mean()
    df0['ewm20']=df0['close_x'].ewm(span=20).mean()    
    df0=df0.dropna()
    if 매수조건식():
        시장가매수('KRW-BCHA')
    if 매도조건식():
        시장가매도('KRW-BCHA')
        
    