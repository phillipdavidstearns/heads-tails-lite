#!/usr/bin/python3/

# grabs headlight dim/bright timings from a pubilshed google drive spreadsheet and saves as 'headlights.csv'

from fileHandlers import *
import signal
import os

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	os._exit(0)

def main():
	os._exit(fetchHeadlights())

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()