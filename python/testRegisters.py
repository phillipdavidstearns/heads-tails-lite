#!/usr/bin/python3

# strobe = pins[0]
# data = pins[1]
# clock = pins[2]
# enable = pins[3]

import Registers as REG
import time

# def init():
# 	GPIO.setmode(GPIO.BCM)

# def output(pins):
# 	for pin in pins: 
# 	GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW) # make pin into an output

# def enable(pins):
# 	GPIO.output(pins[3], 1)

# def disable(pins):
# 	GPIO.output(pins[3], 0)

# def clear(pins, channels):
# 	strobe = pins[0]
# 	data = pins[1]
# 	clock = pins[2]
# 	GPIO.output(data, 0)
# 	for c in range(channels):
# 		GPIO.output(clock, 0)
# 		GPIO.output(clock, 1)
# 	GPIO.output(clock, 0)
# 	GPIO.output(strobe, 1)
# 	GPIO.output(strobe, 0)

# def update(value, pins, channels):
# 	strobe = pins[0]
# 	data = pins[1]
# 	clock = pins[2]

# 	for c in range(channels):
# 		GPIO.output(clock, 0)
# 		GPIO.output(data, value >> (channels - c - 1) & 1)
# 		GPIO.output(clock, 1)
# 	GPIO.output(clock, 0)
# 	GPIO.output(data, 0)
# 	GPIO.output(strobe, 1)
# 	GPIO.output(strobe, 0)

# Pin assignments
strobe = 17 # latch strobe GPIO pin
data = 27 # data GPIO pin
clock = 22 # clock GPIO pin
enable = 23 # register enable GPIO pin
interrupt = 24 # interrupt GPIO pin

outputs = [ strobe, data, clock, enable]
inputs = [ interrupt ]
pins = [ outputs , inputs ]

channels = 24 # number of output channels

def sayHello():
	print("hello!")

def main():
	REG.init(pins)
	REG.attachInterrupt(interrupt,"CHANGE", sayHello)
	REG.clear()
	REG.enable()
	REG.update(412)
	REG.clear()

main()