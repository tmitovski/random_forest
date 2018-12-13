# =================================
# =================================
import pandas as pd
import numpy as np
from tech_indicator import *
from sklearn.metrics import *
import os

from requests.exceptions import ReadTimeout  
from requests.exceptions import Timeout  # this handles ReadTimeout or ConnectTimeout
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import random
# =================================
# =================================
# Get online data
api_key=""
api_secret=""
# import data from binance

count_buy = 0
count_sell = 0

pairs=[12]

for trade in range(0,10000):
    time.sleep(random.uniform(55,65))
    print('Loop:', trade)
    client = Client(api_key, api_secret, requests_params={'timeout': 10000})
    try:
        status = client.get_system_status()
        status0 = status.get('status')
        if (status0 != 1):
        # 0: normal，1：system maintenance
            info = client.get_account(recvWindow=600000)
            balance_ETH = client.get_asset_balance(asset='ETH', recvWindow=600000)
            balance_USDT= client.get_asset_balance(asset='USDT',recvWindow=600000)
            numb_ETH = float(balance_ETH.get('free'))
            numb_USDT= float(balance_USDT.get('free'))
            prices = client.get_all_tickers()
            pric0 = prices[pairs[0]].get('price')
            pric0 = float(pric0)   
            name0 = prices[pairs[0]].get('symbol')
            if (trade == 0):
                start_balance =  (numb_ETH) + (numb_USDT)/pric0
                # Adjust prices to current
                save_sell1 = pric0
                save_buy1  = pric0
            print('Price:', pric0)    
            print('ETH amount:', numb_ETH, '; USDT amount:', numb_USDT)    
            print('Income:', ((((numb_ETH) + (numb_USDT)/pric0)/(start_balance))*100.)-100., '%')

            # 1=buy ETH , 2=sell ETH
            if ((numb_ETH) > (numb_USDT)/pric0):
                trigger = 2
          
            if ((numb_ETH) < (numb_USDT)/pric0):
                trigger = 1
            print('Trigger:', trigger)    
            TIME_IN_FORCE_GTC = 'GTC'


            klines2 = client.get_historical_klines(name0, Client.KLINE_INTERVAL_5MINUTE, "3 hours ago UTC")
            save_klines2=np.array(klines2).astype(np.float)
            go_on = 0

            for loop_1 in range(0,10):
                if (len(save_klines2[:,3]) == 36) and (go_on == 0): 
                    go_on=1
                if (len(save_klines2[:,3]) < 36) and (go_on == 0):
                    print('ntim2 < 36', loop_1)  
                    time.sleep(random.uniform(8,12))
                    klines2 = client.get_historical_klines(name0, Client.KLINE_INTERVAL_5MINUTE, "3 hours ago UTC")
                    save_klines2=np.array(klines2).astype(np.float)
            ntim2 = 35 # exclude last data point. This is not 5 minute tick, but current price
            data_i2= np.empty((ntim2,5))

            data_i2[:,0] = save_klines2[0:ntim2,1]
            data_i2[:,1] = save_klines2[0:ntim2,2]
            data_i2[:,2] = save_klines2[0:ntim2,3]
            data_i2[:,3] = save_klines2[0:ntim2,4]
            data_i2[:,4] = save_klines2[0:ntim2,5]

            df = pd.DataFrame(data_i2[:,:], columns=list(['Open', 'High', 'Low', 'Close', 'Volume']))
            end0=ntim2

# =================================
# =================================

# constants

            n1=6
            n2=27
# =================================
# =================================
# compute technical indicators

            MA1    = moving_average(df,n1) 
            MA2    = moving_average(df,n2)

            MVA1 = MA1.iloc[:end0,5] 
            MVA2 = MA2.iloc[:end0,5] 

# =================================
# =================================
# BUY ETH

            if (MVA1[34] > MVA2[34]) and (trigger == 1) and ((numb_USDT)>20.):
                offer = 0.  
                if (data_i2[-1,3] <= pric0):
                    offer =  data_i2[-1,3]
                if (data_i2[-1,3] > pric0):
                    offer =  pric0
                if (200. < offer < 5000.) and (save_sell1 < 5000.):  
                    amount = offer*1.0002
                    precision1 = 2
                    precision2 = 3
                    buying = numb_USDT/pric0*0.9995
        
                    amt_str = "{:0.0{}f}".format(amount, precision1)    # price
                    numb_str =  "{:0.0{}f}".format(buying, precision2)  # quantity
        
                    save_buy1 = amount
                    count_buy = count_buy + 1
                    print('buy 1:', save_buy1)
                    print('amount:', amt_str)
                    print('number:', numb_str)

                    #place a market buy order
                    order = client.create_order(
                        symbol='ETHUSDT',
                        side=Client.SIDE_BUY,
                        type=Client.ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=numb_str,
                        price=amt_str, recvWindow=600000)
                    time.sleep(random.uniform(20,25))
                    trigger = 2
                    os.system('say "Toni you bought Etherium"')   


#=================================================
# sell ETH
      
            if (MVA1[34]<MVA2[34]) and (trigger == 2) and ((numb_ETH)>0.05):
                offer = 10000.  
                if (data_i2[-1,3] >= pric0):
                    offer =  data_i2[-1,3]
                if (data_i2[-1,3] < pric0):
                    offer =  pric0
                if (200. < offer < 5000.) and (save_buy1 < 5000.):
                    amount = offer*0.9998
                    precision1 = 2
                    precision2 = 3                
                    selling = numb_ETH*0.9995
        
                    amt_str = "{:0.0{}f}".format(amount, precision1)      # price
                    numb_sell =  "{:0.0{}f}".format(selling, precision2)  # quantity

                    save_sell1 = amount
                    count_sell = count_sell + 1
                    print('sell 1:', save_sell1)
                    print('amount:', amt_str)
                    print('number:', numb_sell)

                    order = client.create_order(
                        symbol='ETHUSDT',
                        side=Client.SIDE_SELL,
                        type=Client.ORDER_TYPE_LIMIT, 
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=numb_sell,
                        price=amt_str, recvWindow=600000)
                    time.sleep(random.uniform(20,25))  
                    trigger = 1
                    os.system('say "Toni you sold Etherium"') 

        if (status0 == 1):
            print('status=1') #system maintanance
  
    except ReadTimeout:
        print("ReadTimeOut happened. Will try again....")
        pass
    except Timeout:
        print("TimeOut happened. Will try again....")
        pass
    except BinanceAPIException:
        print("TimeOut happened. Will try again....")
        pass
