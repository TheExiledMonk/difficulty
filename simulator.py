from Constants import *
from hashRate import *
from blockChain import *
from simulation import *

import random
import operator as op
import functools
import time
import os
import csv
import numpy

import sys
import math

def letsGetThisPartyStarted(params=None):
    if params==None:
        #print("No parameters passed when party getting started. Using defaults.")
        s = simulation([])
    else:
        #print("Parameters passed in to get a party started! Indeed, params = " + str(params))
        s = simulation(params)
    s.runSim()


fifths = MAX_RUN_TIME*0.2
thisTime = [0.0, 1.0*fifths, 2.0*fifths, 3.0*fifths, 4.0*fifths, 5.0*fifths]
theseValues = [10.0, 20.0, 40.0, 80.0, 100.0]
thisHashRate = hashRate([thisTime,theseValues,DESC_EXAMPLE,MAX_RUN_TIME])

params = [MAX_RUN_TIME, LAMBDA_TARGET, DIFFICULTY_FORMULA, STARTING_DIFFICULTY, DIFF_ADJ_PERIOD, DIFF_SAMPLE_SIZE, TIME_SAMPLE_SIZE, thisHashRate]
letsGetThisPartyStarted(params) 
