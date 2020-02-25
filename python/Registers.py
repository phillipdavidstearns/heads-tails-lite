#!/usr/bin/python3

# strobe = pins[0]
# data = pins[1]
# clock = pins[2]
# enable = pins[3]

import RPi.GPIO as GPIO

def init(pins):
	GPIO.setmode(GPIO.BCM)
	setMode(pins)


def setMode(pins):
	for pin in pins[0]: 
		GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
	for pin in pins[1]: 
		GPIO.setup(pin, GPIO.IN)


def attachInterrupt(pin, mode, callback): 
	if (mode == "falling" or mode == "FALLING"):
		event = GPIO.FALLING
	else if (mode == "rising" or mode == "RISING"):
		event = GPIO.RISING
	else if (mode == "both" or mode == "BOTH" or mode == "change" or mode == "CHANGE"):
		event = GPIO.BOTH
	else:
		return
	print("Attaching callback \""+str(callback)+"\" to interrupt pin: "+str(pin)+" for "+str(mode))
	GPIO.add_event_detect(pin, event)
	GPIO.add_event_callback(pin, callback)


def enable(pins):
	GPIO.output(pins[3], 1)

def disable(pins):
	GPIO.output(pins[3], 0)

def clear(pins, channels):
	strobe = pins[0]
	data = pins[1]
	clock = pins[2]
	GPIO.output(data, 0)
	for c in range(channels):
		GPIO.output(clock, 0)
		GPIO.output(clock, 1)
	GPIO.output(clock, 0)
	GPIO.output(strobe, 1)
	GPIO.output(strobe, 0)

def update(value, pins, channels):
	strobe = pins[0]
	data = pins[1]
	clock = pins[2]
	for c in range(channels):
		GPIO.output(clock, 0)
		GPIO.output(data, value >> (channels - c - 1) & 1)
		GPIO.output(clock, 1)
	GPIO.output(clock, 0)
	GPIO.output(data, 0)
	GPIO.output(strobe, 1)
	GPIO.output(strobe, 0)