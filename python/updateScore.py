#!/usr/bin/python3/

# csv tab of the score is publicly available at:
# https://docs.google.com/spreadsheets/d/1IF0b8Fv-7jCC3OciHavgOJIZhVEpCWoEPLl8GdaNXFA/edit#gid=1797776547
# after publishing the command to download is:
# curl -L "https://docs.google.com/spreadsheets/d/e/2PACX-1vTGp8GI85wmWP7yZaUa0EV_reKdn2yDFgRBotHnqVOfPKjek4_6JIy4lCnnp9xT9BZavKjeOy-ZYsn_/pub?gid=1797776547&single=true&output=csv"
# (credit - https://stackoverflow.com/questions/24255472/download-export-public-google-spreadsheet-as-tsv-from-command-line)

from fileHandlers import *
import signal
import os

def interruptHandler(signal, frame):
	print()
	print("Interrupt (ID: {}) has been caught. Cleaning up...".format(signal))
	os._exit(0)

def main():

	os._exit(fetchScore())

signal.signal(signal.SIGINT, interruptHandler)
signal.signal(signal.SIGTERM, interruptHandler)

main()