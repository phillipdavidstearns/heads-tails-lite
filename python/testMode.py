#!/usr/bin/python3

#------------------------------------------------------------------------

from fileHandlers import *
import IO
import signal
import os
from random import randint
import time
from math import sin, pow, pi

#------------------------------------------------------------------------

verbose = False

fps=1.0
frameCount=0
rate=0.01
angle=0
channels = 32 # number of output channels

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
def updateHeadlights(angle):
	debug("[+] Setting headlight brightness")
	IO.setPWM(pow(sin(2*pi*angle), 2)) # dim

def updateChannels(channel):
	debug("[+] Updating channels")
	channelStates=[]
	for c in range(channels):
		if c == channel: 
			channelStates.append(1)
		else:
			channelStates.append(0)
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
	global angle

	while True:
		IO.update(updateChannels( framecount % channels ))
		frameCount += 1
		updateHeadlights(angle)
		angle += rate;
		angle = ( angle % 1 ) + 1
		time.sleep( 1 / fps )

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)
signal.signal(signal.SIGHUP, interruptHandler)

setup()
main()