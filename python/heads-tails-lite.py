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

tzOffset = -5 * 3600 # timezone offset
dotOffset = 0 # based on the start of Phase B @ 51 seconds in the cycle starting + 28 past midnight
deviation = 0
power_line_time = time.time()
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

# Some global variables related to headlights
headlightTimes=[ 26400, 60300 ] # default sunrise/sunset times
headlightState=0 # 0 for dim 1 for bright
lastHeadlightState=0 # 0 for dim 1 for bright
DIM = 0.15
BRIGHT = 1.0

# fetch the current date and set headlight timings accordingly
def updateHeadlightTimes():
	debug("[+] Updating headlight timings")
	date=str(time.localtime()[1])+'/'+str(time.localtime()[2])
	debug(date)
	try: # if the date is accounted for, we good
		global headlightTimes
		dim = headlights[date][0].split(':')
		bright = headlights[date][1].split(':')
		headlightTimes[0]=int(dim[0])*3600+int(dim[1])*60
		headlightTimes[1]=int(bright[0])*3600+int(bright[1])*60
		debug("[+] headlight times: " + headlightTimes)
	except: # otherwise we go with the defaults or last used
		pass

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
	debug("[+] Setting headlight brightness")
	currentTime=int(adjustedTime())%86400
	if ( currentTime >= headlightTimes[0] and currentTime < headlightTimes[1] ):
		IO.setPWM(DIM) # dim
	else:
		IO.setPWM(BRIGHT) # dim

#------------------------------------------------------------------------
#	DEVIATION
#	>> NOT USED FOR FREE RUNNING MODE<<
# 	* fetchDeviation()
# 	* deviationChanged()
# 	* loadDeviation()

def resynch():
	debug("[+] Updating deviation amount")
	global power_line_time
	global deviation
	if fetchDeviation():
		if deviationChanged():
			deviation = loadDeviation()
			power_line_time=time.time()

#------------------------------------------------------------------------
# TIMING

# Provides a reading of time that should be synched to the grid
def adjustedTime():
	# return power_line_time + tzOffset + dotOffset + deviation
	return time.time() + tzOffset + dotOffset + deviation

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
	# fetchScore() # check that the current score is present in ./data/
	behaviors = loadScore()
	# resynch()
	updateHeadlightTimes()
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

	global eventTimes
	global eventStates
	global channelStates
	global lastCycleTime
	global power_line_time

	global updateFlag
	global resynchFlag
	global refreshScoreFlag
	global headlightFlag

	global behaviors

	while True:

		currentTime = int(adjustedTime())
#		if(currentTime % 2 == 0): debug(currentTime)

		refreshHeadlightTime = (currentTime - 3600) % 86400 # 86400 should trigger at ~1AM
		if(refreshHeadlightTime == 0 and headlightFlag):
			updateHeadlightTimes()
			headlightFlag = False
		elif(refreshHeadlightTime != 0 and not headlightFlag):
			headlightFlag = True

		# resynchTime = currentTime % 3600 # triggers every hour
		# if(resynchTime == 0 and resynchFlag):
		# 	resynch()
		# 	resynchFlag = False
		# elif(resynchTime != 0 and not resynchFlag):
		# 	resynchFlag = True

		# refreshScoreTime = currentTime  % 1800 # triggers every 1/2 hour
		# if(refreshScoreTime == 0 and refreshScoreFlag):
		# 	verbose("Fetching score")
		# 	if fetchScore():
		# 		behaviors = loadScore()
		# 		verbose(behaviors)
		# 	refreshScoreFlag = False
		# elif(refreshScoreTime != 0 and not refreshScoreFlag):
		# 	refreshScoreFlag = True

		cycleTime = currentTime % 90
		if(cycleTime == 0 and updateFlag):
			updateEvents(behaviors)
			updateFlag = False
		elif(cycleTime != 0 and not updateFlag):
			updateFlag = True

		IO.update(updateChannels())
		updateHeadlights()
		time.sleep(1/fps)

setup()
main()
