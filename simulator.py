
import random
import operator as op
import functools
import time
import os
import csv
import numpy

import sys
import math
from blockChain import *
from simulation import *
from hashRate import *

def letsGetThisPartyStarted(params=[]):
    s = simulation([])
    s.runSim()

params = []
# Bitcoin network:
# daPeriod = 2016
# daSample = 2016
# tsSample = 11
# lambdaTar= 1.0/600.0
# mTime    = 190000000

# Monero network
daPeriod = 1
daSample = 720
tsSample = 60
lambdaTar = 1.0/60.0
mTime    = 47000000

# Attack policy and hashrate description - both independent of the network we are on.
aPolicy  = [0.0,1]
hashDesc = "Simple stepwise hashRate."
time   = [0.0, 0.2*float(mTime), 0.4*float(mTime), 0.6*float(mTime), 0.8*float(mTime)]
values = [1000, 10000, 1000, 100000, 1000]

####################

params.append(daPeriod)       # difficulty adjustment period 2 weeks in blocks
params.append(daSample)       # difficulty adjustment sample size, 2 weeks in blocks with target arrival rate
params.append(tsSample)         # timeSampleSize for bitcoin is 11 blocks.
params.append(lambdaTar)  # lambdaTarget
params.append(mTime)  # 6 years of bitcoin life. maxTime
params.append(aPolicy)    # Attack policy; for simplicity, set to [0.0,x], which is no attack at all.
params.append(hashDesc) # Hash rate description
params.append(time)
params.append(values)

letsGetThisPartyStarted(params) 
