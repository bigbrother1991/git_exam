import pandas as pd
import numpy as np
import pyupbit
import time
import datetime
import json
from tqdm import tqdm 


access='9nQLNICO2fkCLPA51gUCb05QxdpHtY9mlzkbnt6h'
secret='LTNcZ5vPTVBfL4hKUyjQ0o31llqZGNnLpSYjAgCP'
tickers = pyupbit.get_tickers(fiat="KRW")

def 중간값(코인):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(코인, interval="minute1", count=200)
    df['중간값'] = (df['open']+df['high'])/2
    중간 = df['중간값'].rolling(20).mean().iloc[-1]
    return 중간

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute" )
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=200)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def BEST_K(코인):
    bestk=[]
    df = pyupbit.get_ohlcv(코인, interval='minute1' )
    for k in np.arange(0.3, 1.0, 0.05):

        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        ror = df['ror'].cumprod()[-1]    
#         print("%.1f %f" % (k, ror))
        bestk.append((ror,k))
    return max(bestk)[1]
    
def 코인선정K():

    코인2=[]
    누적수익율2=[]
    mdd2=[]
    ratio2=[]

    for ticker in tickers:
        # 변동폭 * k 계산, (고가 - 저가) * k값
        df = pyupbit.get_ohlcv(ticker, interval='minute60' )
        time.sleep(0.2)
        df['range'] = (df['high'] - df['low']) * BEST_K('KRW-BTC')

        # target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
        df['target'] = df['open'] + df['range'].shift(1)

        # ror(수익률), np.where(조건문, 참일때 값, 거짓일때 값)
        df['ror'] = np.where(df['high'] > df['target'],
                             df['close'] / df['target'],
                             1)

        # 누적 곱 계산(cumprod) => 누적 수익률
        df['hpr'] = df['ror'].cumprod()

        # Draw Down 계산 (누적 최대 값과 현재 hpr 차이 / 누적 최대값 * 100)
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

        #MDD 계산
        ratio=df['hpr'][-1]*100/df['dd'].max()

        표준편차=df['hpr'][-1].std( )

        ratio2.append(ratio)
        mdd2.append(df['dd'].max())
        누적수익율2.append(df['hpr'][-1])
        코인2.append(ticker)
    #     print(f" 누적수익률 : {df['hpr'][-1]}   /  MDD(%): ", df['dd'].max())
    코인선정={"코인명":코인2, "누적수익율":누적수익율2,"MDD":mdd2,"Ratio":ratio2}

    코인선정2=pd.DataFrame(코인선정)
    코인선정3=코인선정2.sort_values('Ratio',ascending=False)
    코인선정4=코인선정3[코인선정3['Ratio'] >10]
    코인선정4=코인선정4[코인선정4['MDD'] <15]
    코인선정5=코인선정4.sort_values('누적수익율',ascending=False)
    
    return 코인선정5['코인명'].tolist()[0]

def 지정가매수(ticker,h):
    orderbook = pyupbit.get_orderbook(ticker)
    sell_price = orderbook[0]['orderbook_units'][h]['bid_price']
    unit = krw/sell_price
    upbit.buy_limit_order(ticker, sell_price, unit)
def 지정가매도(ticker,h):
    orderbook = pyupbit.get_orderbook(ticker)
    잔고 = upbit.get_balance(ticker)
    sell_price = orderbook[0]['orderbook_units'][h]['ask_price']
    upbit.sell_limit_order(ticker, sell_price, 잔고)
tickers = pyupbit.get_tickers(fiat="KRW")
def short_trading_for_1percent(ticker):
    dfs = [ ]
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    time.sleep(0.15)
    # 1) 매수 일자 판별
    cond = df['high'] >= df['open'] * 1.01

    acc_ror = 1
    sell_date = None

    # 2) 매도 조건 탐색 및 수익률 계산
    for buy_date in df.index[cond]:
        if sell_date != None and buy_date <= sell_date:
            continue

        target = df.loc[ buy_date :  ]

        cond = target['high'] >= target['open'] * 1.02
        sell_candidate = target.index[cond]

        if len(sell_candidate) == 0:
            buy_price = df.loc[buy_date, 'open'] * 1.01
            sell_price = df.iloc[-1, 3]
            acc_ror *= (sell_price / buy_price)
            break
        else:
            sell_date = sell_candidate[0]
            acc_ror *= 1.005
            # 수수료 0.001 + 슬리피지 0.004

    return acc_ror


##############################################  실제 매매로직     ##############################################

import telegram
from telegram.ext import Updater, MessageHandler, Filters
telgm_token = '1108135935:AAEzD9fUZxII258ELQm3ah_gej1E3LqLlmU'
chat_id=1069639277
bot = telegram.Bot(token = telgm_token)

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("자동매매 시작")
cnt=0
# 자동매매 시작
data={}
while True:
    try:
        if 1<cnt <1800:
            코인 = 코인선정K()
            cnt=0
        else:
            pass
        
        now = datetime.datetime.now()
        start_time = get_start_time('KRW-BTC')
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            목표가 = 중간값(코인) *(1-0.02*BEST_K(코인)) # 각 코인별로 다른 값 적용되도록
            판매가 = 중간값(코인) *(1+0.02*BEST_K(코인))
            ma15 = get_ma15('KRW-BTC')
            현재가 = get_current_price(코인)
            time.sleep(0.1)
            if 목표가 > 현재가 and ma15 < pyupbit.get_current_price('KRW-BTC'):
                krw = get_balance("KRW")
                if krw > 5000:
                    매수=지정가매수(코인,1)
                    bot.send_message(chat_id=chat_id, text=f'지정가 매수 : {코인} / {매수}')
            elif ma15 > pyupbit.get_current_price('KRW-BTC'):
                MT=지정가매도(코인,1) # 현재 가격으로 매도함
                
        #매수됐으면        
        잔고목록=[]
        cnt+=0.5
        for 잔고 in range(0,len(upbit.get_balances())):
            잔고목록.append(upbit.get_balances()[잔고]['currency'])   
        if  len(잔고목록) >1:
            for 매도할것 in 잔고목록[1:]:
                현재가 = get_current_price(코인)
                time.sleep(0.2)
                if 판매가 < 현재가 :
                    매도=지정가매도(f'KRW-{매도할것}',1)  # 1퍼센트 붙여서 매도함 
                    try:
                        get_balance(코인)
                    except:

                        bot.send_message(chat_id=chat_id, text=f'목표가  매도 : {코인} / {매도}')
                        pass
            time.sleep(0.2)
    except Exception as ex:
        bot.send_message(chat_id=chat_id, text=f'[에러발생] {ex}')
        time.sleep(0.1)