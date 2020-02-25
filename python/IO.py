#!/usr/bin/python3

import RPi.GPIO as GPIO

STROBE=-1
DATA=-1
CLOCK=-1
ENABLE=-1
CHANNELS=-1


def init(pins, channels):

	GPIO.setmode(GPIO.BCM)

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

	print("Strobe Pin set to: "+str(STROBE))
	print("Data Pin set to: "+str(DATA))
	print("Clock Pin set to: "+str(CLOCK))
	print("Enable Pin set to: "+str(ENABLE))
	print("Number of register channels: "+str(CHANNELS))

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