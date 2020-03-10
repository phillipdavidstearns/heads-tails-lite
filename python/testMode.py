#!/usr/bin/python3

#------------------------------------------------------------------------
# heads-tails-lite.py
#
# Refactoring of heads-tails.py

from fileHandlers import *
import IO
import signal
import os
import random
import time
from math import sin, pow, pi

#------------------------------------------------------------------------

verbose = False

fps=30.0
frameCount=0
channels = 48 # number of output channels

# Pin assignments

# outputs
strobe = 17 # latch strobe GPIO pin
data = 27 # data GPIO pin
clock = 22 # clock GPIO pin
enable = 23 # IOister enable GPIO pin

# pwm
pwm_pin = 12 # pwm pin
pwm_freq = 14000
pwm_brightness = 0

# make composite lists to pass along to IO
outputs = [ strobe, data, clock, enable]
inputs = [ ]
pwm_args = [ pwm_pin, pwm_freq, pwm_brightness ]

pins = [ outputs , inputs, pwm_args ]

#------------------------------------------------------------------------
#	verbose or debug mode

def debug(message):
	if verbose:
		print(message)

#------------------------------------------------------------------------
#	HEADLIGHTS
#	updating of the actual headlight timetables is done using functions in fileHandlers.py
#		* fetchHeadlights()
#		* loadHeadlights()


# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
	debug("[+] Setting headlight brightness")
	IO.setPWM(pow(sin(2*pi*frameCount/1000), 2)) # dim

def updateChannels():
	debug("[+] Updating channels")
	channelStates=[]
	for c in range(channels):
		channelStates.append(frameCount >> c & 1)
	debug(channelStates)
	return channelStates

#------------------------------------------------------------------------

def interruptHandler(signal, frame):
	shutdownIO()
	os._exit(0)

def setup():
	startupIO()

def startupIO():
	IO.init(pins, channels)
	IO.clear()
	IO.enable()

def shutdownIO():
	IO.disable()
	IO.clear()
	IO.cleanup()

def main():

	global frameCount

	while True:
		IO.update(updateChannels())
		updateHeadlights()
		frameCount += 1
		time.sleep(0.125)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)
signal.signal(signal.SIGHUP, interruptHandler)

setup()
main()
