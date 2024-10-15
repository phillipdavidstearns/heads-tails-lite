#!/usr/bin/python3

#------------------------------------------------------------------------
# heads-tails-lite.py
#
# Refactoring of heads-tails.py

from fileHandlers import loadScore
import IO
import signal
import os
import random
import time
from datetime import datetime
import argparse

import logging

#------------------------------------------------------------------------
# verbose or debug mode

def debug(message):
  if verbose: print(message)

#------------------------------------------------------------------------
# HEADLIGHTS
# Some global variables related to headlights
headlightTimes = [ 25200, 68400 ] # default sunrise/sunset times of 7am 7pm
headlightState = 0 # 0 for dim 1 for bright
DIM = 0.25
BRIGHT = 1.0

# check what time it is and dijust headlight brightnesss accordingly
def updateHeadlights():
  debug("[+] Setting headlight brightness")
  currentTime = adjustedTime() % 86400
  if ( currentTime >= headlightTimes[0] and currentTime < headlightTimes[1] ):
    IO.setPWM(DIM) # dim
  else:
    IO.setPWM(BRIGHT) # dim

#------------------------------------------------------------------------
# TIMING

# Provides a reading of time that should be synched to the grid
def adjustedTime():
  return int(datetime.now().timestamp())

#------------------------------------------------------------------------

def updateEvents():
  debug("[+] Updating behavior events")
  global eventTimes
  global eventStates
  eventList = makeEventList()
  for c in range(channels):
    times, states = generateTimings(behaviors[eventList[c]])
    eventTimes[c] += times
    eventStates[c] += states
  debug([eventTimes, eventStates])

#------------------------------------------------------------------------

def updateChannels():
  debug("[+] Updating channels")
  global eventTimes
  global eventStates
  global channelStates
  for c in range(channels):
    if eventTimes[c]:
      if (adjustedTime() >= eventTimes[c][0]):
        channelStates[c] = eventStates[c][0]
        eventStates[c] = eventStates[c][1:] # remove from queue
        eventTimes[c] = eventTimes[c][1:] # remove from queue
        if (len(eventTimes[c]) == 0):
          channelStates[c] = 0
  debug(channelStates)
  return channelStates

#------------------------------------------------------------------------

def generateTimings(behavior):
  debug("[+] Generate timings")
  times = []
  states = []
  offset = random.uniform(-behavior[2], behavior[2])
  startTime = adjustedTime()

  for t in range(len(behavior[0])):
    eventTime = startTime + offset + behavior[0][t] + random.uniform(-behavior[1][t], behavior[1][t])
    times.append(eventTime)
    if (t % 2 == 0):
      states.append(1)
    else:
      states.append(0)

  debug(times, states)

  return (times, states)

#------------------------------------------------------------------------

def makeEventList():
  debug("[+] Making behavior event list")
  eventList = []
  itemCount = [0] * len(behaviors)

  while (len(eventList) < channels):
    candidate = random.randint(0, len(behaviors) - 1)
    if (itemCount[candidate] < max_repeat):
      eventList.append(random.randint(0, len(behaviors) - 1))
      itemCount[candidate] += 1

  debug(eventList)

  return eventList

#----------------------------------------------------------------

def interruptHandler(signal, frame):
  shutdownIO()
  os._exit(0)

#----------------------------------------------------------------

def startupIO():

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
  outputs = [ strobe, data, clock, enable ]
  inputs = []
  pwm_args = [ pwm_pin, pwm_freq, pwm_brightness ]

  pins = [ outputs , inputs, pwm_args ]

  IO.init(pins, channels)
  IO.clear()
  IO.enable()

#----------------------------------------------------------------

def shutdownIO():
  IO.disable()
  IO.clear()
  IO.cleanup()

#----------------------------------------------------------------

def main():

  updateFlag = True

  while True:
    
    updateHeadlights()

    cycleTime = adjustedTime() % 90
    if(cycleTime == 0 and updateFlag):
      updateEvents()
      updateFlag = False
    elif(cycleTime != 0 and not updateFlag):
      updateFlag = True

    IO.update(updateChannels())
    time.sleep(1 / fps)

#----------------------------------------------------------------

if __name__ == "__main__":
  signal.signal(signal.SIGINT, interruptHandler)
  signal.signal(signal.SIGTERM, interruptHandler)

  parser = argparse.ArgumentParser(description='heads-tails-lite')

  # create arguments
  parser.add_argument(
    '-v',
    dest='verbose',
    action='store_true',
    default=False,
    help='Verbose mode. Display debug messages'
  )

  # parse the args
  args = parser.parse_args()

  # store the argument values
  verbose = args.verbose
  debug("Verbose mode. Displaying debug messages")

  max_repeat = 3
  fps = 30.0
  channels = 32 # number of output channels

  startupIO()

  eventTimes = [[]] * channels
  eventStates = [[]] * channels
  channelStates = [0] * channels

  behaviors = loadScore()

  updateEvents()

  main()
