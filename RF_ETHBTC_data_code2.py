# Using 1 feature ('Close') all 400 values predicted (testPredict) were identical (ex. 49.0403) 
# For that reason, use at least two features
# Random Forest for ETHBTC (use sample code 2)
# a) Use Sep1 2017 to Sep1 2018 to train and test
# b) Use Sep1 2017 to Jun1 2018 to train and Jun1 2018 to sep1 2018 to test
# test whether a) and b) give similar results
###########################################################################

import numpy
import numpy as np
# import matplotlib.pyplot as plt
from pandas import read_csv
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
#from sklearn.model_selection import train_test_split
from sklearn.cross_validation import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import sys
from netCDF4 import Dataset
from sklearn.metrics import *

###########################################################################

# fix random seed for reproducibility
numpy.random.seed(7)

# load the dataset'
data1 = Dataset('ETHBTC_1hour_Jun01_2018_Sep1_2018.nc')

data2 = data1.variables['klines']
# sorted in the order: columns=list(['Open', 'High', 'Low', 'Close', 'Volume']))
nlen = len(data2[:,3])

# nf=number of features
nf = 4 
dataset = np.empty((nlen,nf))

# dataset[:,0] needs to be the feature you predict (ex. Price)
# if feature 1 is too small multiply by 1000, to get larger (x1000) RMSE values
# do not need to multiply other features (even they are too small)

dataset[:,0] = data2[:,3]*1000.
dataset[:,1] = data2[:,4]
dataset[:,2] = data2[:,1]
dataset[:,3] = data2[:,2]

dataset = dataset.astype('float32')

###########################################################################

# reshape into X=t and Y=t+1
ts = 1 # time steps

dataset_y = np.empty(nlen)
dataset_y = dataset_y.astype('float32')

for loop in range(0,nlen-ts):
    dataset_y[loop] = dataset[loop+ts,0]

# split into train and test sets
train_size = int(nlen * 0.8)
test_size = nlen - train_size - ts
trainX, testX = dataset  [0:train_size,:], dataset  [train_size:(nlen-ts),:]
trainY, testY = dataset_y[0:train_size],   dataset_y[train_size:(nlen-ts)]

###########################################################################

# create and fit the RF model
# n_estimators (The number of trees in the forest)
reg = RandomForestRegressor(n_estimators=10, random_state=0)
reg.fit(trainX, trainY)

trainPredict = numpy.empty(train_size)
testPredict  = numpy.empty(test_size)

trainPredict = reg.predict(trainX)
testPredict  = reg.predict(testX)

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY, trainPredict))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY, testPredict))
print('Test Score: %.2f RMSE' % (testScore))

