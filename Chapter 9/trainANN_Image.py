import numpy as np
import matplotlib.pyplot as plt
from ANN import ANN
import PIL
from PIL import Image


# setup the network configuration
inode = 784
hnode = 100
onode = 10



# set the learning rate
lr = 0.9

# instantiate an ANN object named ann
ann = ANN(inode, hnode, onode, lr)

# create the training list data
dataFile = open('mnist_train.csv')
dataList = dataFile.readlines()
dataFile.close()

# train the ANN using all the records in the list
for record in dataList:
    recordx = record.split(',')
    inputT = (np.asfarray(recordx[1:])/255.0 * 0.99) + 0.01
    train = np.zeros(onode) + 0.01
    train[int(recordx[0])] = 0.99
    # training begins here
    ann.trainNet(inputT, train)

# create the test list data from an image
img = Image.open('ninebw.jpg')
img = img.resize((28, 28), PIL.Image.ANTIALIAS)

# read pixels into list
pixels = list(img.getdata())

# convert into single values from tuples
pixels = [i[0] for i in pixels]

a = np.array(pixels)
a.tofile('test.csv', sep=',')

testDataFile = open('test.csv')
testDataList =  testDataFile.readlines()
testDataFile.close()

for record in testDataList:
    recordx = record.split(',')
    input = (np.asfarray(recordx[0:])/255.0 * 0.99) + 0.01
    output = ann.testNet(input)

# display output
print output
 
