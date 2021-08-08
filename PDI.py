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
    orderbook = pyupbit.get_orderbook(ticker)
    sell_price = orderbook[0]['orderbook_units'][0]['ask_price']
    unit = krw/len(이격도df3)*3
    upbit.buy_market_order(ticker, unit)
def 시장가매도(ticker):
    unit = upbit.get_balance(ticker)
    upbit.sell_market_order(ticker, unit)


def 매수조건식(df4,period=7):
    # 즉, + DI와 ADX 값이 상승 중이면서 파라볼릭이 상승추세 일때 매수 포지션을 취하고, 
    #반대로 -DI와 ADX값이 상승 중이면서 파라볼릭 지표가 하락추세 일때는 매도 포지션을 취해야 합니다.
    df4['SAR']=real = talib.SAR(df4['high'], df4['low'], acceleration=0.02, maximum=0.2)
    df4['MINUS_DI']=talib.MINUS_DI(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['ADX'] = talib.ADX(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['PLUS_DI']=talib.PLUS_DI(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['RSI'] =talib.RSI(df4['close'], timeperiod=period)
    df4['수익률'] = df4['close'].pct_change()
    df4['CCI']=talib.CCI( df4['high'], df4['low'], df4['close'], timeperiod=14)
    #9.WPR : william percent range (Williams' %R)
    df4['WPR'] = talib.WILLR(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['EMA']=talib.EMA(df4['close'], timeperiod=30)
    fastk, fastd = talib.STOCHRSI( df4['close'], timeperiod=period, fastk_period=5, fastd_period=3, fastd_matype=0)
    df4['OBV']=talib.OBV( df4['close'],  df4['volume'])
    df4['OBV_EMA5']=talib.EMA(df4['OBV'], timeperiod=5)
    df4['OBV_EMA20']=talib.EMA(df4['OBV'], timeperiod=20) 
    ############################################################################
    df4['ma3+'] = df4['PLUS_DI'].rolling(1).mean().shift(1)
    df4['ma10+'] = df4['PLUS_DI'].rolling(2).mean().shift(1)
    df4['ma3-'] = df4['MINUS_DI'].rolling(1).mean().shift(1)
    df4['ma10-'] = df4['MINUS_DI'].rolling(2).mean().shift(1)
    
    df4['ma3_ADX'] = df4['ADX'].rolling(1).mean().shift(1)
    df4['ma10_ADX'] = df4['ADX'].rolling(2).mean().shift(1)
    df4['ma3_SAR'] = df4['SAR'].rolling(1).mean().shift(1)
    df4['ma10_SAR'] = df4['SAR'].rolling(2).mean().shift(1)    
    
    
    df4['OBV_EMA5']=talib.EMA(df4['OBV'], timeperiod=2)
    df4['OBV_EMA20']=talib.EMA(df4['OBV'], timeperiod=5)    
    
    df4=df4.dropna()
    
    매수조건1= df4['ma3+']>df4['ma10+'] 
    매수조건2= df4['ma3_ADX']>df4['ma10_ADX']
    매수조건3= df4['ma3_SAR']>df4['ma10_SAR']
    매수조건4= df4['OBV_EMA5']>df4['OBV_EMA20']

    매수조건=매수조건1 & 매수조건2 & 매수조건3 &매수조건4
    return 매수조건[-1]


def 매도조건식(df4,period=7):
    df4['SAR']=real = talib.SAR(df4['high'], df4['low'], acceleration=0.02, maximum=0.2)
    df4['MINUS_DI']=talib.MINUS_DI(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['ADX'] = talib.ADX(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['PLUS_DI']=talib.PLUS_DI(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['RSI'] =talib.RSI(df4['close'], timeperiod=period)
    df4['수익률'] = df4['close'].pct_change()
    df4['CCI']=talib.CCI( df4['high'], df4['low'], df4['close'], timeperiod=14)
    #9.WPR : william percent range (Williams' %R)
    df4['WPR'] = talib.WILLR(df4['high'], df4['low'], df4['close'], timeperiod=period)
    df4['EMA']=talib.EMA(df4['close'], timeperiod=30)
    fastk, fastd = talib.STOCHRSI( df4['close'], timeperiod=period, fastk_period=5, fastd_period=3, fastd_matype=0)
    df4['OBV']=talib.OBV( df4['close'],  df4['volume'])
    df4['OBV_EMA5']=talib.EMA(df4['OBV'], timeperiod=5)
    df4['OBV_EMA20']=talib.EMA(df4['OBV'], timeperiod=20) 
    ############################################################################
    df4['ma3+'] = df4['PLUS_DI'].rolling(1).mean().shift(1)
    df4['ma10+'] = df4['PLUS_DI'].rolling(2).mean().shift(1)
    df4['ma3-'] = df4['MINUS_DI'].rolling(1).mean().shift(1)
    df4['ma10-'] = df4['MINUS_DI'].rolling(2).mean().shift(1)
    
    df4['ma3_ADX'] = df4['ADX'].rolling(1).mean().shift(1)
    df4['ma10_ADX'] = df4['ADX'].rolling(2).mean().shift(1)
    df4['ma3_SAR'] = df4['SAR'].rolling(1).mean().shift(1)
    df4['ma10_SAR'] = df4['SAR'].rolling(2).mean().shift(1)    
    
    
    df4['OBV_EMA5']=talib.EMA(df4['OBV'], timeperiod=2)
    df4['OBV_EMA20']=talib.EMA(df4['OBV'], timeperiod=5)    
    
    df4=df4.dropna()
    매도조건1= df4['ma3-']>df4['ma10-']
    매도조건2= df4['ma3_ADX']>df4['ma10_ADX']
    매도조건3= df4['ma3_SAR'] <df4['ma10_SAR'] 

    매도조건=(매도조건1 & 매도조건2 & 매도조건3 )
    return 매도조건[-1]


while True:
    df = pyupbit.get_ohlcv('KRW-BTC', interval="day")
    잔고 = upbit.get_balance("KRW")
    time.sleep(1)
    if 매수조건식(df):
        시장가매수('KRW-BTC')
    if 매도조건식(df):
        시장가매도('KRW-BTC')
        