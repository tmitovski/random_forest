#saves 1-hour klines for a pair

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 06:50:04 2018

@author: mitovski
"""
#import datetime

from requests.exceptions import ReadTimeout  
from requests.exceptions import Timeout  # this handles ReadTimeout or ConnectTimeout
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import random
from requests.exceptions import ConnectionError

import numpy as np
import numpy
import sys
#import pyopencl
#from pyopencl.tools import get_test_platforms_and_devices
#print(get_test_platforms_and_devices())
#===========
pairs = [0] #specify 1 pair, 0 = ETHBTC
#===========

#toni_mito (generated Sept 22, 2018)
api_key="aDvDaxmLjqJZ9ryNehFWAEO3iLnGjfV4rM9bf5pKQQ0rIiEUvgt5xV4ii1Dn19Mx"
api_secret="BDJCtrHI0RHQeKRANHdSPX8fAE5ZmqU6IiCONfGLsnGDVFpTTccAOCeG2RILJogD"
# import data from binance


client = Client(api_key, api_secret, requests_params={'timeout': 1000})
  
  #client = Client(api_key, api_secret, {"verify": False, "timeout": 20})
  #print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
try:
    
  status = client.get_system_status()
  status0 = status.get('status')
  if (status0 != 1):
     # 0: normal，1：system maintenance
    #=================================================
      info = client.get_account(recvWindow=600000)
      #info = client.get_symbol_info('XLMETH')
      
      # prices show PAIR exchange (NOTE: it is last (ask) price)
      prices = client.get_all_tickers()
      name0 = prices[pairs[0]].get('symbol')
      print('Name:', name0)
      
      #klines1 = client.get_historical_klines(name0, Client.KLINE_INTERVAL_5MINUTE, "10 MONTHS ago UTC")
      #klines1 = client.get_historical_klines(name0, Client.KLINE_INTERVAL_1HOUR, "1 Sep, 2017", "1 Jun, 2018")
      klines1 = client.get_historical_klines(name0, Client.KLINE_INTERVAL_1HOUR, "1 Sep, 2017", "1 Sep, 2018")
      save_klines0=np.array(klines1).astype(np.float)
      #ntim = (np.shape(save_klines0[:,0]))
      ntim = len(save_klines0[:,0])
      plot_klines= np.empty(((ntim,5)))
      print(np.shape(plot_klines))
 
      plot_klines[:,0] = save_klines0[:,1]
      plot_klines[:,1] = save_klines0[:,2]
      plot_klines[:,2] = save_klines0[:,3]
      plot_klines[:,3] = save_klines0[:,4]
      plot_klines[:,4] = save_klines0[:,5]
      #print(plot_klines[loop,:,3])
      #print('loop:', loop)
      # klines are:
      #"1499040000000",    // Open time
      #"0.01634790",       // Open
      #"0.80000000",       // High
      #"0.01575800",       // Low
      #"0.01577100",       // Close
      #"148976.11427815",  // Volume
      #1499644799999,      // Close time
      #"2434.19055334",    // Quote asset volume
      #308,                // Number of trades
      #"1756.87402397",    // Taker buy base asset volume
      #"28.46694368",      // Taker buy quote asset volume
      #"17928899.62484339" // Ignore

      from netCDF4 import Dataset
      rootgrp = Dataset('ETHBTC_1hour_Sep1_2017_Sep1_2018.nc', 'w', format='NETCDF4')
      print(rootgrp.file_format)
      rootgrp.close()
      rootgrp = Dataset('ETHBTC_1hour_Sep1_2017_Sep1_2018.nc', 'a')
      fcstgrp = rootgrp.createGroup('forecasts')
      #analgrp = rootgrp.createGroup('analyses')

      #pair = rootgrp.createDimension('pair', len(pairs))
      time = rootgrp.createDimension('time', ntim)
      data = rootgrp.createDimension('data', 5)

      klines = rootgrp.createVariable('klines','f8',('time','data',))
      klines[:,:] = plot_klines[:,:]

      rootgrp.close()
    #================================================= 
  if (status0 == 1):
    print('status=1') #system maintanance
  
except ReadTimeout:
        print("ReadTimeOut happened. Will try again....1")
        time.sleep(60)
        pass
except Timeout:
        print("TimeOut happened. Will try again....2")
        time.sleep(60)
        pass
except BinanceAPIException:
        print("TimeOut happened. Will try again....3")
        time.sleep(60)
        pass
except ConnectionError:
        print("Connection Error happened. Will try again in 3 minutes")
        time.sleep(180)
        pass
except MaxRetryError:
        print("Max Retry Error happened. Will try again in 4 minutes")
        time.sleep(240)
        pass

