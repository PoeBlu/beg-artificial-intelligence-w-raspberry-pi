import RPi.GPIO as GPIO
import time
from random import randint
import numpy as np
# next two libraries must be installed IAW appendix instructions
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

global pwmL, pwmR, mcp
lightOld = 0
hysteresis = 2

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

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

# The following matrix elements are all that are needed 
# (and a bit more) to implement the motor control function.  
# Read the brain mapping section to see why this is true.
m25 = 2
m26 = -2
m27 = 4
m28 = -8
m29 = 10
m30 = -4
m31 = 0
m32 = 0
m33 = -10
m34 = 2
m35 = -4
m36 = 10

# robotAction module
def robotAction(select):
    global pwmL, pwmR
    if select == 0: # drive straight
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
    elif select == 1: # turn left
        pwmL.ChangeDutyCycle(2.4)
        pwmR.ChangeDutyCycle(2.8)
    elif select == 2: # turn right
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(3.4)
    elif select == 3: # stop
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(2.8)

# forever loop 
while True:
    # light sensor readings

    # acquire new reading
    lightNew = mcp.read_adc(0)
    v7 = 0
    # debug
    print 'lightNew = ',lightNew, ' lightOld = ',lightOld

    # determine if moving toward or away from light source
    if lightNew  > (lightOld+hysteresis):
        # moving toward the light source
        v1 = 1
        v2 = -1
    elif lightNew < (lightOld-hysteresis):
        # moving away from light source
        v1 = -1
        v2 = 1
    else:
        # must be stationary
        v1 = 1
        v2 = 1
        v7 = 1
    # save sensor reading
    lightOld = lightNew
    # sensor 1 reading
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

    # check for distance and set v3 as appropriate
    if distance1 < threshold:
        # set v3 to -1 to signal obstacle detected
        v3 = -1
    else:
        v3 = 1 # no obstacle detected
    time.sleep(0.1) # ensure that sensor 1 is quiet

    # sensor 2 reading
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

    # check for distance and set v4 as appropriate
    if distance2 < threshold:
        # set v4 to -1 to signal obstacle detected
        v4 = -1
    else:
        v4 = 1 # no obstacle detected
    time.sleep(0.1) # ensure that sensor 2 is quiet

    # calculate v5 and v6
    v5 = m25*v1 + m26*v2 + m27*v3 + m28*v4 # not using m29 and m30
    v6 = m31*v1 + m32*v2 + m33*v3 + m34*v4 # not using m35 and m36

    # normalize v5 and v6
    if v5 >= 0:
        v5 = 1
    else:
        v5 = -1
    if v6 >  0:
        v6 = 1
    else:
        v6 = -1

    # motor control actions based on the new computed vector elements
    if v7 == 1:
        # stop, light is unchanged
        select = 3
        robotAction(select)
        # debug
        print 'stopped'
        exit()
    elif v5 == 1 and v6 == -1:
        # drive straight ahead
        select = 0
        robotAction(select)
        # debug
        print 'driving straight ahead'
    elif v5 == -1 and v6 == -1:
        # randomly select turning left or right
        turnRnd = randint(0,1)
        if turnRnd == 0:
            # turn left 
            select = 1
            robotAction(select)
            # debug
            print 'turning left'
        else:
            # turn right
            select = 2
            robotAction(select)
            # debug
            print 'turning right'

    # pause for a 2 seconds
    time.sleep(2)