import os
import csv
import logging

script_dir = os.path.split(os.path.realpath(__file__))[0]

def loadScore():
  with open( script_dir + "/data/score.csv",'rt') as f:
    reader = csv.reader(f)
    behaviors=[]
    for row in reader:
      index = 0
      times = []
      variations = []
      offset_variation = 0
      for item in row:
        temp = -1.0

        if item: # execute if string isn't empty
          try: # convert appropriate strings to float
            temp = float(item)
          except:
            pass

          if temp != -1: # test if a conversion happened
            if (index == 0):
              offset_variation = temp
            elif (index % 2 == 1):
              times.append(temp)
            else:
              variations.append(temp)
            index += 1
      behaviors.append([times, variations, offset_variation])
  return behaviors
