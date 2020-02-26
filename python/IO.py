#!/usr/bin/python3

import RPi.GPIO as GPIO
import pigpio

STROBE=-1
DATA=-1
CLOCK=-1
ENABLE=-1
CHANNELS=-1

PWM_PIN = -1
PWM_FREQ = -1
PWM_VAL = 0

PWM = object()


# pins is a list of lists
# pins[0] are basic output pins
# pins[1] are basic input pins
# pins[2] are hardware PWM values: [ pin, freq, brightness ]

def init(pins, channels):

	GPIO.cleanup() # clear any pit assignments left over from unclean terminations
	GPIO.setmode(GPIO.BCM) # use GPIO pin numbers

	# Setup hardware PWM

	global PWM
	global PWM_PIN
	global PWM_FREQ
	global PWM_VAL

	PWM = pigpio.pi()
	if not PWM.connected:
		exit()

	PWM_PIN=pins[2][0]
	PWM_FREQ=pins[2][1]
	PWM_VAL=pins[2][2]

	setPWM(PWM_VAL)

	# Setup Rregister outputs

	global STROBE
	global DATA
	global CLOCK
	global ENABLE
	global CHANNELS

	STROBE=pins[0][0]
	DATA=pins[0][1]
	CLOCK=pins[0][2]
	ENABLE=pins[0][3]
	CHANNELS=channels

	if STROBE == -1 or DATA == -1 or CLOCK == -1 or ENABLE == -1:
		print("Registers require 4 GPIO pins: strobe, data, clock, and enable")
		return

	if CHANNELS == -1:
		print("Number of channels must be greater than 0")
		return

	for pin in pins[0]: 
		GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
	for pin in pins[1]: 
		GPIO.setup(pin, GPIO.IN)

def setPWM(brightness):
	PWM.hardware_PWM(PWM_PIN, PWM_FREQ, brightness*1000000.0)

def attachInterrupt(pin, mode, callback): 
	if (mode == "falling" or mode == "FALLING"):
		event = GPIO.FALLING
	elif (mode == "rising" or mode == "RISING"):
		event = GPIO.RISING
	elif (mode == "both" or mode == "BOTH" or mode == "change" or mode == "CHANGE"):
		event = GPIO.BOTH
	else:
		print("mode not recognized: "+str(mode))
		return
	GPIO.add_event_detect(pin, event)
	GPIO.add_event_callback(pin, callback)

def cleanup():
	GPIO.cleanup()
	setPWM(0)
	PWM.stop()

def enable():
	GPIO.output(ENABLE, 1)

def disable():
	GPIO.output(ENABLE, 0)

def clear():
	GPIO.output(DATA, 0)
	for c in range(CHANNELS):
		GPIO.output(CLOCK, 0)
		GPIO.output(CLOCK, 1)
	GPIO.output(CLOCK, 0)
	GPIO.output(STROBE, 1)
	GPIO.output(STROBE, 0)

def update(value):
	for c in range(CHANNELS):
		GPIO.output(CLOCK, 0)
		GPIO.output(DATA, value >> (CHANNELS - c - 1) & 1)
		GPIO.output(CLOCK, 1)
	GPIO.output(CLOCK, 0)
	GPIO.output(STROBE, 1)
	GPIO.output(STROBE, 0)
	GPIO.output(DATA, 0)