import RPi.GPIO as GPIO
import time
from random import randint
import numpy as np

global pwmL, pwmR

threshold = 25.4

# use the BCM pin numbers
GPIO.setmode(GPIO.BCM)

# setup the motor control pins
GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

pwmL = GPIO.PWM(18,20) # pin 18 is left wheel pwm
pwmR = GPIO.PWM(19,20) # pin 19 is right wheel pwm

# must 'start' the motors with 0 rotation speeds
pwmL.start(2.8)
pwmR.start(2.8)
 
# ultrasonic sensor pins
TRIG1 = 23 # an output
ECHO1 = 24 # an input
TRIG2 = 25 # an output
ECHO2 = 27 # an input

# set the output pins
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(TRIG2, GPIO.OUT)

# set the input pins
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(ECHO2, GPIO.IN)

# initialize sensors
GPIO.output(TRIG1, GPIO.LOW)
GPIO.output(TRIG2, GPIO.LOW)
time.sleep(1)

# Create an initial weighting matrix named wtg
# based on all 1's in the input data vector
vInput = np.array([1,1,1,1,1])[:,None] # actually a [1,0] matrix
wtg = vInput.T*vInput # matrix multiplication yields a 5 x 5 matrix
                      # vInput.T is the transpose form (i.e. column)
                      # The square of new and successful input data 
                      # vectors will be added to wtg matrix.



# robotAction module
def robotAction(select):
    global pwmL, pwmR
    if select == 0: # drive straight
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
    elif select == 1: # turn left
        pwmL.ChangeDutyCycle(2.2)
        pwmR.ChangeDutyCycle(2.8)
    elif select == 2: # turn right
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(3.6)
    elif select == 3: # stop
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(2.8)
# flag used to trigger a new draw     
clockFlag = False

# forever loop 
while True:
   
    if clockFlag == False:
        start = time.time()
        draw = randint(0,3) # generate a random draw
        if draw == 0:   # drive forward
            select = 0
            robotAction(select)
        elif draw == 1: # turn left
            select = 1
            robotAction(select)
        elif draw == 2: # turn right
            select = 2
            robotAction(select)
        elif draw == 3: # stop
            select = 3
            robotAction(select)
        clockFlag = True 
        numHits = 0
            

    GPIO.output(TRIG1, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(TRIG1, GPIO.LOW)

    # following code detects the time duration for the echo pulse
    while GPIO.input(ECHO1) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO1) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    # distance calculation
    distance1 = pulse_duration * 17150

    # round distance to two decimal points
    distance1 = round(distance1, 2)

    # check for distance and set v1 as appropriate
    if distance1 < threshold:
        # set v1 to -1 to signal obstacle detected
        v1 = -1
        numHits = numHits + 1
    else:
        v1 = 1 # no obstacle detected
    time.sleep(0.1) # ensure that sensor 1 is quiet
    

    GPIO.output(TRIG2, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(TRIG2, GPIO.LOW)

    # following code detects the time duration for the echo pulse
    while GPIO.input(ECHO2) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO2) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    # distance calculation
    distance2 = pulse_duration * 17150

    # round distance to two decimal points
    distance2 = round(distance2, 2)
   
    # check for distance and set v2 as appropriate
    if distance2 < threshold:
        # set v2 to -1 to signal obstacle detected
        v2 = -1
        numHits = numHits + 1
    else:
        v2 = 1 # no obstacle detected
   
    time.sleep(0.1) # ensure that sensor 2 is quiet

    # check if both sensors detected an obstacle
    if  v1 == -1 and v2 == -1:
        v3 = -1 # set v3 to a -1
        numHits = numHits + 1
    else:
        v3 = 1  # set v3 to a 1 indicating that both sensors 
                # have not detected an obstacle

    # Create a new input data vector reflecting the new situation    
    vInput = np.array([v1, v2, v3, 0, 0])[:,None]
  

    # Dot product between the vector transpose and the wtg matrix
    testVector = np.dot(vInput.T,wtg)
    testVector = np.array(testVector).tolist()
   
    # normalize testVector
    tv = np.array([0,0,0,0,0])[:,None]
    for i in range(0,4):
        if testVector[0][i] >= 0:
            tv[i][0] = 1
        else:
            tv[i][0] = -1
 
    # check for a solution
    if(tv[0][0] != v1 or tv[1][0] != v2 or tv[2][0] != v3):
        print 'No solution found'
        
        # generate a random solution
        if randint(0,64) > 31:
            v4 = 1
        else:
            v4 = -1
        if randint(0,64) > 31:
            v5 = 1
        else:
            v5 = -1
    
        # select an action based on the random draws for v3 and v4
        if v4 ==1 and v5 == 1:
            select = 0
            robotAction(select)
        elif v4 == 1 and v5 == -1:
            select = 1
            robotAction(select)
        elif v4 == -1 and v5 == 1:
            select = 2
            robotAction(select)
        elif v4 == -1 and v5 == -1:
            select =3
            robotAction(select)


        earlyNumHits =  numHits
        numHits = 0 # reset to check if new solution is better    
    
        # check if the new solution, if any, is better
        if  numHits < earlyNumHits or numHits == 0:
            # create the solution vector
            vInput = np.array([v1, v2, v3, v4, v5])[:,None]
            # multiply by itself
            VInputSq = vInput.T*vInput
            # Add it to the wtg matrix
            wtg = wtg + VInputSq
            # The wtg matrix now has the new solution stored in it
    
    current = time.time()
     
    if (current - start)*1000 > 2000:
        #this triggers a new draw at loop start
        clockFlag = False
