import random
import time
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO

# Start Raspberry Pi configuration
# Raspberry Pi pin designations
lcd_rs        = 27  
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight =  4

# Define LCD column and row size for a 16x4 LCD.
lcd_columns = 16
lcd_rows    =  4

# Instantiate an LCD object
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

# Print a two line welcoming message
lcd.message('Lets play nim\ncomputer vs human')

# Wait 5 seconds
time.sleep(5.0)

# Clear the screen
lcd.clear()

# Setup GPIO pins
# Set the BCM mode
GPIO.setmode(GPIO.BCM)

# Inputs
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

global player
player = ""
global humanTurn
humanTurn = False
global stickNumber
stickNumber = 21
global humanPick
humanPick = 0
global gameover
gameover = False

# Setup the callback functions
def pickOne(channel):
    global humanTurn
    global humanPick
    humanPick = 1
    humanTurn = True
    
def pickTwo(channel):
    global humanTurn
    global humanPick
    humanPick = 2
    humanTurn = True

def pickThree(channel):
    global humanTurn
    global humanPick
    humanPick = 3
    humanTurn = True
    
def quit(channel):
    lcd.clear()
    exit()      # pin 20, immediate exit from the game

# Add event detection and callback assignments
GPIO.add_event_detect(12, GPIO.RISING, callback=pickOne)
GPIO.add_event_detect(13, GPIO.RISING, callback=pickTwo)
GPIO.add_event_detect(19, GPIO.RISING, callback=pickThree)
GPIO.add_event_detect(20, GPIO.RISING, callback=quit)

# random selection for the players
playerSelect = random.randint(0,1)
if playerSelect:
    humanTurn = True
    lcd.message('Human goes first')
else:
    humanTurn = False
    lcd.message('Computer goes first')

time.sleep(2)
lcd.clear()



def computerMove():
    global stickNumber
    global humanTurn

    if (stickNumber-1) % 4 == 1:
        computerPick = 1
    elif (stickNumber-2) % 4 == 1:
        computerPick = 2
    elif (stickNumber-3) % 4 == 1:
        computerPick = 3
    else:
        computerPick = random.randint(1,3)

    if stickNumber >= 4:
        stickNumber -= computerPick
    elif stickNumber in [4, 3, 2]:
        stickNumber = 1
    humanTurn = True

def humanMove():
    global humanPick
    global humanTurn
    global stickNumber
    while not humanPick:
        pass
    while (humanPick >= stickNumber):
        lcd.message('Number selected\n')
        lcd.message('is >= remaining\n')
        lcd.message('sticks')
    stickNumber -= humanPick
    humanTurn = False
    humanPick = 0
    lcd.clear()

def checkWinner():
    global gameover
    global player
    global stickNumber
    if stickNumber == 1:
        msg = f'{player} wins!'
        lcd.message(msg)
        time.sleep(5)
        gameover = True

def resetGameover():
    global gameover
    global stickNumber
    gameover = False
    stickNumber = 21
    return gameover

def game():
    global player
    global humanTurn
    global gameover
    global stickNumber
    while gameover == False:
        if humanTurn == True:
            lcd.message('human turn\n')
            msg = f'sticks left: {str(stickNumber)}' + '\n'
            lcd.message(msg)
            humanMove()
        else:
            lcd.message('computer turn\n')
            computerMove()
        msg = f'sticks left: {str(stickNumber)}'
        lcd.message(msg)
        time.sleep(2)
        checkWinner()
        lcd.clear()
    if gameover == True:
            lcd.clear()
            playAgain()

def playAgain():
    global humanPick
    lcd.message('Play again?\n')
    lcd.message('1 = y, 2 = n')
   
    while humanPick == 0:
        pass
    if humanPick == 1:
        lcd.clear()
        resetGameover()
        game()
    elif humanPick == 2:
        lcd.clear()
        lcd.message('Thanks for \n')
        lcd.message('playing the game')
        time.sleep(5)
        lcd.clear()
        exit()   

game()
