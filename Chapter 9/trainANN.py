import numpy as np
import matplotlib.pyplot as plt
from ANN import ANN

# setup the network configuration
inode = 784
hnode = 100
onode = 10

# set the learning rate
lr = 0.2

# instantiate an ANN object named ann
ann = ANN(inode, hnode, onode, lr)

with open('mnist_train_100.csv') as dataFile:
    dataList = dataFile.readlines()
# train the ANN using all the records in the list
for record in dataList:
    recordx = record.split(',')
    inputT = (np.asfarray(recordx[1:])/255.0 * 0.99) + 0.01
    train = np.zeros(onode) + 0.01
    train[int(recordx[0])] = 0.99
    # training begins here
    ann.trainNet(inputT, train)
