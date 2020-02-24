#!/usr/bin/python3

from fileHandlers import *
import random
import time
import signal
import os
import math
import RPi.GPIO as GPIO # using RPi.GPIO for non-PWM

import argparse

parser = argparse.ArgumentParser(description='Set brightness of headlights')
parser.add_argument('-b', type=int, default=0, help='behavior')

args = parser.parse_args()
b=args.b


#------------------------------------------------------------------------

CHANNELS=32
FPS = 30; # refresh rate of LEDs

#------------------------------------------------------------------------

# grid synch related
start_time=time.time()

#------------------------------------------------------------------------
# GPIO related
STR = 17
DATA = 27
CLK = 22

#------------------------------------------------------------------------
# RPi.GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(STR, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
GPIO.setup(DATA, GPIO.OUT, initial=GPIO.LOW) # make pin into an output
GPIO.setup(CLK, GPIO.OUT, initial=GPIO.LOW) # make pin into an output

def regClear():
	GPIO.output(DATA, 0)
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)

def regOutput(channels):
	for i in range(CHANNELS):
		GPIO.output(CLK, 0)
		GPIO.output(DATA, channels[CHANNELS - i - 1])
		GPIO.output(CLK, 1)
	GPIO.output(CLK, 0)
	GPIO.output(STR, 1)
	GPIO.output(STR, 0)
	GPIO.output(DATA, 0)

#------------------------------------------------------------------------
# Behavior related

channelStates=[]
eventTimes=[]
eventIndexes=[]
lastCycleTime = -1


def setLightOn(channel):
	global channelStates
	channelStates[channel] = 1

def setLightOff(channel):
	global channelStates
	channelStates[channel] = 0

def timing():

	global eventTimes
	global eventIndexes

	for c in range(CHANNELS):
		if eventTimes[c]:
			if (time.time() > eventTimes[c][0]):
				if (eventIndexes[c][0] == 1):
					setLightOn(c)
				elif (eventIndexes[c][0] == 0):
					setLightOff(c)
				# remove the event from queue
				eventIndexes[c]=eventIndexes[c][1:]
				eventTimes[c]=eventTimes[c][1:]
				if (len(eventTimes[c])==0):
					setLightOff(c)

def generateTimings(behavior):
	times=[]
	indexes=[]
	startTime=time.time()
	offset = random.uniform(-behavior[2],behavior[2])
	for t in range(len(behavior[0])):
		eventTime = startTime + offset + behavior[0][t] + random.uniform(-behavior[1][t],behavior[1][t])
		times.append(eventTime)
		if (t%2==0):
			indexes.append(1)
		else:
			indexes.append(0)

	return [times, indexes]

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	regClear()
	GPIO.cleanup()
	os._exit(0)

def main():

	global eventTimes
	global eventIndexes
	global channelStates
	global lastCycleTime

	for i in range(CHANNELS):
		eventTimes.append([])
		eventIndexes.append([])
		channelStates.append(0)

	regClear()
	updateScore()
	behaviors = loadScore()

	while True:
		global b
		cycleTime = int(time.time()-start_time) % 90
		# print("   {:02d}".format(cycleTime), end='\r')
		if( cycleTime == 0 and cycleTime != lastCycleTime):
			print(behaviors[b])
			allTimings=[]
			for c in range(CHANNELS):
				timings=generateTimings(behaviors[b])
				eventTimes[c]+=timings[0]
				eventIndexes[c]+=timings[1]
				allTimings.append(timings)
			print(allTimings)
		timing()
		regOutput(channelStates)
		lastCycleTime=cycleTime
		time.sleep(1/FPS)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)
signal.signal(signal.SIGHUP, interruptHandler)

main()