# Random Forest for ETHBTC (use sample code 1)
# a) Use Sep1 2017 to Sep1 2018 to train and test
# b) Use Sep1 2017 to Jun1 2018 to train and Jun1 2018 to sep1 2018 to test
# test whether a) and b) give similar results
###########################################################################

import numpy
import numpy as np
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import sys
from netCDF4 import Dataset

###########################################################################

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)


# fix random seed for reproducibility
numpy.random.seed(7)

# load the dataset'
data1 = Dataset('/home/toni/Desktop/Git/random_forest/THBTC_1hour_Sep1_2017_Sep1_2018.nc')
data2 = data1.variables['klines']
# sorted in the order: columns=list(['Open', 'High', 'Low', 'Close', 'Volume']))
nlen = len(data2[:,3])
dataset = np.empty((nlen,1))
dataset[:,0] = data2[:,3]*1000.
dataset = dataset.astype('float32')

# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset)

# split into train and test sets
train_size = int(len(dataset) * 0.8)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]

# reshape into X=t and Y=t+1
look_back = 1
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
print(np.shape(trainX))

# reshape input to be [samples, time steps, features]
trainX = numpy.reshape(trainX, (trainX.shape[0], trainX.shape[1]))
testX = numpy.reshape(testX, (testX.shape[0], testX.shape[1]))
print(np.shape(trainX))
# create and fit the RF model
# n_estimators (The number of trees in the forest)
reg = RandomForestRegressor(n_estimators=10, bootstrap=False, oob_score=False, random_state=0) 
reg.fit(trainX, trainY)

# make predictions

trainPredict = numpy.empty_like(trainX)
testPredict = numpy.empty_like(testX)

trainPredict[:,0] = reg.predict(trainX.reshape(-1,1))
testPredict[:,0] = reg.predict(testX.reshape(-1,1))

# invert predictions
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])

# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

# shift train predictions for plotting
trainPredictPlot = numpy.empty_like(dataset)
trainPredictPlot[:, :] = numpy.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict

# shift test predictions for plotting
testPredictPlot = numpy.empty_like(dataset)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict

# plot baseline and predictions
plt.plot(scaler.inverse_transform(dataset))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()

nlen0 = len(testPredict[:,0])
# Another test to estimate earnings
start_am = 0
n_buy = 0
n_sell = 0
trigger = 1
save_buy = 0.
save_sell = 0.
buy=0.
sell=0.

for count in range(1,nlen0-1):
              if (testPredict[count,0] > 1.02*testY[0,count-1]) and (trigger == 1):
 
                  if (start_am == 1):# and (data1orig[tr0+count+start]*1.01 < save_sell):
                          buy = (sell/testY[0,count-1])*0.99925
                          save_buy = testY[0,count-1]
                          n_buy = n_buy + 1
                          trigger = 2
                          sell = 0.
                  if (start_am == 0):
                          buy = (1./testY[0,count-1])*0.99925
                          save_buy = testY[0,count-1]
                          buy_start = buy
                          start_am = 1
                          trigger = 2
                          sell=0.

              if (testPredict[count,0] < 0.98*testY[0,count-1]) and (trigger == 2):# and (data1orig[tr0+count]*0.99 > save_buy):
                      sell = buy*testY[0,count-1]*0.99925
                      save_sell = testY[0,count-1]
                      trigger = 1
                      n_sell = n_sell + 1
                      buy = 0.

gain1 = 0.
gain1 = (((buy*testY[0,count-1]) + sell)/(testY[0,count-1]/testY[0,1]))
print('Relative to no trade (need >1):', gain1)
print('Earnings (%) :', 100.*(((buy*testY[0,count-1]) + sell)-1.))
print('number of trades:', n_sell+n_buy)
print('===========================')
gain1 = 0.
gain1 = (buy + (sell/testY[0,count-1]))/(buy_start)
print('Relative to no trade (need >1):', gain1)
print('===========================') 

