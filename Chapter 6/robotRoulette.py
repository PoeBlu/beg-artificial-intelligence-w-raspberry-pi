import RPi.GPIO as GPIO
import time
from random import randint

global select, pwmL, pwmR, fitA, fitB, fitC

fitA = 20
fitB = 20
fitC = 20

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

pwmL = GPIO.PWM(18,20) # pin 18 is left wheel pwm
pwmR = GPIO.PWM(19,20) # pin 19 is right wheel pwm

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

# robotAction module
def robotAction(select):
    global pwmL, pwmR
    if select == 0:
        # stop immediately
        exit()
    elif select == 1:
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
    elif select == 2:
        pwmL.ChangeDutyCycle(2.2)
        pwmR.ChangeDutyCycle(2.8)
    elif select == 3:
        pwmL.ChangeDutyCycle(2.8)
        pwmR.ChangeDutyCycle(2.2)
     

# backup module
def backup():
    global select, fitA, fitB, fitC, pwmL, pwmR
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
    pwmL.start(2.2)
    pwmR.start(3.6)
    time.sleep(2) # unconditional time interval
   

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

    if current - start > 2:
        clockFlag = False



    # generate a 10 usec trigger pulse
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
       
