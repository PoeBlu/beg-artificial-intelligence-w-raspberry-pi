import RPi.GPIO as GPIO
import time
from random import randint
# next two libraries must be installed IAW appendix instructions
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

global pwmL, pwmR, fitA, fitB, fitC, pwrThreshold, mcp

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# initial fitness values for each of the 3 activities
fitA = 20
fitB = 20
fitC = 20

#initial pwrThreshold
pwrThreshold = 500 # units of milliwatts

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
TRIG = 23 # an output
ECHO = 24 # an input

# set the output pin
GPIO.setup(TRIG, GPIO.OUT)

# set the input pin
GPIO.setup(ECHO, GPIO.IN)

# initialize sensor
GPIO.output(TRIG, GPIO.LOW)
time.sleep(1)

# modified robotAction module
def robotAction(select):
    global pwmL, pwmR, pwrThreshold, fitA, fitB, fitC
    if select == 0:
        # stop immediately
        exit()
    elif select == 1:
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
        fitA = fitA - 0.5 if calcPower() > pwrThreshold else fitA + 0.5
    elif select == 2:
        pwmL.ChangeDutyCycle(2.2)
        pwmR.ChangeDutyCycle(2.8)
        fitB = fitB - 0.5 if calcPower() > pwrThreshold else fitB + 0.5
    elif select == 3:
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(2.2)
        fitC = fitC - 0.5 if calcPower() > pwrThreshold else fitC + 0.5
     
# backup module
def backup(select):
    global fitA, fitB, fitC, pwmL, pwmR
    if select == 1:
        fitA = fitA - 1
        fitA = max(fitA, 0)
    elif select == 2:
        fitB = fitB - 1
        fitB = max(fitB, 0)
    else:
        fitC = fitC -1
        fitC = max(fitC, 0)
    # now, drive the robot in reverse for 2 secs.
    pwmL.ChangeDutyCycle(2.2)
    pwmR.ChangeDutyCycle(3.6)
    time.sleep(2) # unconditional time interval
   
# power calculation module
def calcPower:
    global mcp
    count0 = mcp.read_adc(0)
    count1 = mcp.read_adc(1)
    diff = count0 - count1
    power = (diff*diff)/5
    return power

clockFlag = False

# forever loop
while True:
    if clockFlag == False:
        start = time.time()

        randomInt = randint(0, 255)
        draw = (randomInt*(fitA + fitB + fitC))/255

        if fitA + fitB + fitC == 0:
            select = 0
            robotAction(select)
        elif draw >= 0 and draw <= fitA:
            select = 1
            robotAction(select)
        elif draw > fitA and draw <= (fitA + fitB):
            select = 2
            robotAction(select)
        elif draw > (fitA + fitB):
            select = 3
            robotAction(select)

        clockFlag = True

    current = time.time()

    # check to see if 2 seconds (2000ms) have elapsed
    if current - start > 2:
        # this triggers a new draw at loop start
        clockFlag = False 

    # generate a 10 µsec trigger pulse
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(TRIG, GPIO.LOW)

    # following code detects the time duration for the echo pulse
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    # distance calculation
    distance = pulse_duration * 17150

    # round distance to two decimal points
    distance = round(distance, 2)

    # check for 25.4 cm distance or less
    if distance < 25.40:
        backup()
