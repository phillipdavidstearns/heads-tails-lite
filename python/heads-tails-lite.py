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

#------------------------------------------------------------------------

import argparse

parser = argparse.ArgumentParser(description='heads-tails-lite')

# create arguments
parser.add_argument('-v', dest='verbose', action='store_true',
					default=False,
                    help='Verbose mode. Display debug messages')

# parse the args
args = parser.parse_args()

# store the argument values
verbose=args.verbose

if verbose:
	print("Verbose mode. Displaying debug messeges")

behaviors = []
channelStates = []
eventTimes = []
eventStates = []
headlights = []
updateFlag = True
resynchFlag = True
refreshScoreFlag = True
headlightFlag = True
maxRepeat = 3

fps=30.0
channels = 32 # number of output channels

# Pin assignments

# outputs
strobe = 17 # latch strobe GPIO pin
data = 27 # data GPIO pin
clock = 22 # clock GPIO pin
enable = 23 # IOister enable GPIO pin

# pwm
pwm_pin = 12 # pwm pin
pwm_freq = 10000
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

# Some global variables related to headlights
headlightTimes=[ 25200, 68400 ] # default sunrise/sunset times of 7am 7pm
headlightState=0 # 0 for dim 1 for bright
lastHeadlightState=0 # 0 for dim 1 for bright
DIM = 0.975
BRIGHT = 1.0

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
	debug("[+] Setting headlight brightness")
	currentTime=int(adjustedTime())%86400
	if ( currentTime >= headlightTimes[0] and currentTime < headlightTimes[1] ):
		IO.setPWM(DIM) # dim
	else:
		IO.setPWM(BRIGHT) # dim

#------------------------------------------------------------------------
# TIMING

# Provides a reading of time that should be synched to the grid
def adjustedTime():
	return time.time() + time.localtime().tm_gmtoff

#------------------------------------------------------------------------

def updateEvents(behaviors):
	debug("[+] Updating behavior events")
	global eventTimes
	global eventStates
	eventList=makeEventList(behaviors)
	for c in range(channels):
		timings = generateTimings(behaviors[eventList[c]])
		eventTimes[c]+=timings[0]
		eventStates[c]+=timings[1]
	debug([eventTimes,eventStates])

def updateChannels():
	debug("[+] Updating channels")
	global eventTimes
	global eventStates
	global channelStates
	for c in range(channels):
		if eventTimes[c]:
			if (adjustedTime() > eventTimes[c][0]):
				channelStates[c]=eventStates[c][0]
				eventStates[c]=eventStates[c][1:] # remove from queue
				eventTimes[c]=eventTimes[c][1:] # remove from queue
				if (len(eventTimes[c])==0):
					channelStates[c]=0
	debug(channelStates)
	return channelStates

def generateTimings(behavior):
	debug("[+] Generate timings")
	times=[]
	states=[]
	offset = random.uniform(-behavior[2],behavior[2])
	startTime=adjustedTime()
	for t in range(len(behavior[0])):
		eventTime = startTime + offset + behavior[0][t] + random.uniform(-behavior[1][t],behavior[1][t])
		times.append(eventTime)
		if (t%2==0):
			states.append(1)
		else:
			states.append(0)
	debug([times, states])
	return [times, states]

def makeEventList(behaviors):
	debug("[+] Making behavior event list")
	eventList=[]
	itemCount=[0]*len(behaviors)
	while (len(eventList) < channels):
		candidate=random.randint(0,len(behaviors)-1)
		if (itemCount[candidate] < maxRepeat):
			eventList.append(random.randint(0,len(behaviors)-1))
			itemCount[candidate] += 1
	debug(eventList)
	return eventList

#------------------------------------------------------------------------

def interruptHandler(signal, frame):
	shutdownIO()
	os._exit(0)

def setup():
	global eventTimes
	global eventStates
	global channelStates
	global behaviors
	global headlights

	# clear channel state and event queues
	for i in range(channels):
		eventTimes.append([])
		eventStates.append([])
		channelStates.append(0)

	startupIO()

	behaviors = loadScore()
	headlights = loadHeadlights()

def startupIO():
	IO.init(pins, channels)
	IO.clear()
	IO.enable()

def shutdownIO():
	IO.disable()
	IO.clear()
	IO.cleanup()

def main():

	global behaviors
	global eventTimes
	global eventStates
	global channelStates
	global lastCycleTime
	global updateFlag

	while True:
		
		currentTime = int(adjustedTime())

		updateHeadlights()

		cycleTime = currentTime % 90
		if(cycleTime == 0 and updateFlag):
			updateEvents(behaviors)
			updateFlag = False
		elif(cycleTime != 0 and not updateFlag):
			updateFlag = True

		IO.update(updateChannels())
		time.sleep(1/fps)

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

setup()
main()
