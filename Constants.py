"""
These are just some default values all held in one place so we don't get magic numbers.

These are global default constants, and shouldn't be changed; instance and class attributes
may be set to these values, however.
"""

import sys
import math

# simulation params:
# maxTime = params[0]
# lambdaTarget = params[1]
# diffForm = params[2]
# nextDifficulty = params[3]
# difficultyAdjustmentPeriod = params[4]
# diffSampleSize = params[5]
# timeSampleSize = params[6]
# hRate = hashRate(params[7], params[8], params[9], maxTime)
#       ~ time = params[7]
#       ~ values = params[8]
#       ~ desc = params[9] i.e. "StepwiseHashRate"

MAX_RUN_TIME = 4000000.0
LAMBDA_TARGET = 1.0/60.0
#DIFFICULTY_FORMULA = "bitmonero"
DIFFICULTY_FORMULA = "bitcoin"
#STARTING_DIFFICULTY = 1
STARTING_DIFFICULTY = int(math.ceil(1.0/LAMBDA_TARGET))
DIFF_ADJ_PERIOD = 1
DIFF_ADJ_PERIOD_BITCOIN = 2016
DIFF_SAMPLE_SIZE = 720
TIME_SAMPLE_SIZE = 60
DIFF_SAMPLE_SIZE_BITCOIN = 2016
TIME_SAMPLE_SIZE_BITCOIN = 11

TIME_EXAMPLE   = [0.0,  11.0,   100.0, 250.0, 375.1, 478.0]
VALUES_EXAMPLE = [18.7, 364.2, 841.2, 241.8, 906.8]
DESC_EXAMPLE = "StepwiseHashrate"

HASHRATE_LOGFILE = "logs/hashRateLog.log"
BLOCKCHAIN_LOGFILE = "logs/blockChainLog.log"
SIMULATION_LOGFILE = "logs/simulationLog.log"
