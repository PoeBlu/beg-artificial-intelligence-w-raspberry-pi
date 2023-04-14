import RPi.GPIO as GPIO
import time
import threading
import numpy as np

# next two libraries must be installed IAW appendix instructions
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

class Behavior():
    global pwmL, pwmR, distance1, distance2

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



class Controller():

    def __init__(self):
        self.behaviors = []
        self.wait_object = threading.Event()
        self.active_behavior_index = None

        self.running = True
        #self.return_when_no_action = return_when_no_action

        #self.callback = lambda x: 0

    def add(self, behavior):
        self.behaviors.append(behavior)

    def remove(self, index):
        old_behavior = self.behaviors[index]
        del self.behaviors[index]
        if self.active_behavior_index == index:  # stop the old one if the new one overrides it
            old_behavior.suppress()
            self.active_behavior_index = None

    def update(self, behavior, index):
        old_behavior = self.behaviors[index]
        self.behaviors[index] = behavior
        if self.active_behavior_index == index:  # stop the old one if the new one overrides it
            old_behavior.suppress()

    def step(self):
        behavior = self.find_next_active_behavior()
        if behavior is not None:
            self.behaviors[behavior].action()
            return True
        return False

    def find_next_active_behavior(self):
        for priority, behavior in enumerate(self.behaviors):
            active = behavior.takeControl()
            if active == True:
                activeIndex = priority
        print 'index = ', activeIndex
        time.sleep(2)
        return activeIndex    

    def find_and_set_new_active_behavior(self):
        new_behavior_priority = self.find_next_active_behavior()
        if self.active_behavior_index is None or self.active_behavior_index > new_behavior_priority:
            if self.active_behavior_index is not None:
                self.behaviors[self.active_behavior_index].suppress()
            self.active_behavior_index = new_behavior_priority
            print 'priority = ', self.active_behavior_index
            # Callback to tell something it changed the active behavior if anything is interested
#            self.callback(self.active_behavior_index)

    def start(self):  # run the action methods
        self.running = True
        self.find_and_set_new_active_behavior()  # force do it ourselves once to find the right one
        thread = threading.Thread(name="Continuous behavior checker",
                                  target=self.continuously_find_new_active_behavior, args=())
        thread.daemon = True
        thread.start()
        

        while self.running:
            if self.active_behavior_index is not None:
                running_behavior = self.active_behavior_index
                self.behaviors[running_behavior].action()
                
                if running_behavior == self.active_behavior_index:  
                    self.active_behavior_index = None
                    self.find_and_set_new_active_behavior()
#
#            elif self.return_when_no_action:
#                break

            #Nothing more to do, so we are shutting down
            self.running = False

#    def start(self, run_in_thread=False):
#        if run_in_thread:
#            thread = threading.Thread(name="Subsumption Thread",
#                                      target=self._start, args=())
#            thread.daemon = True
#            thread.start()
#        else:
#            self.start()

    def stop(self):
        self._running = False
        self.behaviors[self.active_behavior_index].suppress()

    def continuously_find_new_active_behavior(self):
        while self.running:
            self.find_and_set_new_active_behavior()

    def __str__(self):
        return str(self.behaviors)

class NormalBehavior(Behavior):
    def takeControl(self):
        return True
    def action(self):
        # drive forward
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
    def suppress(self):
        # all stop
        pwmL.ChangeDutyCycle(2.6)
        pwmR.ChangeDutyCycle(2.6)

class AvoidObstacle(Behavior):
       
    def takeControl(self):
        #self.distance1 = distance1
        #self.distance2 = distance2
        return self.distance1 <= 25.4 or self.distance2 <= 25.4
    
    def action(self):
        # drive backward
        pwmL.ChangeDutyCycle(2.2)
        pwmR.ChangeDutyCycle(3.6)
        time.sleep(1.5)
        # turn right
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.6)
        time.sleep(0.3)
        # stop
        pwmL.ChangeDutyCycle(2.6)
        pwmR.ChangeDutyCycle(2.6)

    def suppress(self):
        # all stop
        pwmL.ChangeDutyCycle(2.6)
        pwmR.ChangeDutyCycle(2.6)

    def setDistances(self, dest1, dest2):
        self.distance1 = dest1
        self.distance2 = dest2

class StopRobot(Behavior):
    global voltage
    critical_voltage = 6

    def takeControl(self):
        return voltage < critical_voltage
    def action(self):
        # drive forward
        pwmL.ChangeDutyCycle(3.6)
        pwmR.ChangeDutyCycle(2.2)
    def suppress(self):
        # all stop
        pwmL.ChangeDutyCycle(2.6)
        pwmR.ChangeDutyCycle(2.6)


class testBBR():
       
    def __init__(self):
        
        # instantiate objects
        self.nb = NormalBehavior()
        self.oa = AvoidObstacle()
        self.control = Controller()

        # setup the behaviors array by priority; last-in = highest
        self.control.add(self.nb)
        self.control.add(self.oa)

        # initialize distances
        distance1 = 50
        distance2 = 50
        self.oa.setDistances(distance1, distance2)

        # activate the behaviors
        self.control.start()

        threshold = 25.4 #10 inches

        # use the BCM pin numbers
        GPIO.setmode(GPIO.BCM)

        # ultrasonic sensor pins
        self.TRIG1 = 23 # an output
        self.ECHO1 = 24 # an input
        self.TRIG2 = 25 # an output
        self.ECHO2 = 27 # an input

        # set the output pins
        GPIO.setup(self.TRIG1, GPIO.OUT)
        GPIO.setup(self.TRIG2, GPIO.OUT)

        # set the input pins
        GPIO.setup(self.ECHO1, GPIO.IN)
        GPIO.setup(self.ECHO2, GPIO.IN)

        # initialize sensors
        GPIO.output(self.TRIG1, GPIO.LOW)
        GPIO.output(self.TRIG2, GPIO.LOW)
        time.sleep(1)

        # Hardware SPI configuration:
        SPI_PORT   =  0
        SPI_DEVICE = 0
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


    def run(self):        
        # forever loop 
        while True:
            # sensor 1 reading
            GPIO.output(self.TRIG1, GPIO.HIGH)
            time.sleep(0.000010)
            GPIO.output(self.TRIG1, GPIO.LOW)

            # following code detects the time duration for the echo pulse
            while GPIO.input(self.ECHO1) == 0:
                pulse_start = time.time()
        
            while GPIO.input(self.ECHO1) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            # distance calculation
            distance1 = pulse_duration * 17150

            # round distance to two decimal points
            distance1 = round(distance1, 2)

            time.sleep(0.1) # ensure that sensor 1 is quiet
    
            # sensor 2 reading
            GPIO.output(self.TRIG2, GPIO.HIGH)
            time.sleep(0.000010)
            GPIO.output(self.TRIG2, GPIO.LOW)

            # following code detects the time duration for the echo pulse
            while GPIO.input(self.ECHO2) == 0:
                pulse_start = time.time()
        
            while GPIO.input(self.ECHO2) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            # distance calculation
            distance2 = pulse_duration * 17150

            # round distance to two decimal points
            distance2 = round(distance2, 2)
   
            time.sleep(0.1) # ensure that sensor 2 is quiet

            self.oa.setDistances(distance1, distance2)
            
            count0 = self.mcp.read_adc(0)
            # approximation given 1023 = 7.5V
            voltage = count0 / 100
             
            self.control.find_and_set_new_active_behavior()

            print 'distance1 = ', distance1
            print
            print 'distance2 = ', distance2
            print 
            print 'voltage = ', voltage
            print
            time.sleep(5)

# instantiate an instance of testBBR
bbr = testBBR()

# run it
bbr.run()
