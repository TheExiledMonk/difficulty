from hashRate import *
from blockChain import *
from Constants import *

import math
import random


class simulation:
    """ Continuous-time simulation that creates a discrete-time blockchain. """

    ## Class attributes ##
    ## The class itself will return these values if called, i.e. hashRate.time returns [0.0] etc.
    ## These also cause the default values of specific instances of this class.

    clock = 0.0 # Clocks always start at 0.0; force into an int before actually using the clock.
    logFileName = "logs/simulationLog.log"
    arrivalRate = 1.0
    maxTime = MAX_RUN_TIME
    lambdaTarget = LAMBDA_TARGET
    diffForm = DIFFICULTY_FORMULA
    nextDifficulty = STARTING_DIFFICULTY
    difficultyAdjustmentPeriod = DIFF_ADJ_PERIOD
    diffSampleSize = DIFF_SAMPLE_SIZE
    timeSampleSize = TIME_SAMPLE_SIZE

    bChain = blockChain()
    hRate = hashRate()

    ###########################################################

    def __init__(self,  params = None):
        if(params==None or not params):
            self.printToLog("Error in (simulation __init__): No parameters passed in, using defaults.")
        else:
            #print("A simulation object has been initialized. params = " + str(params))
            self.maxTime = params[0]
            self.lambdaTarget = params[1]
            self.diffForm = params[2]
            self.nextDifficulty = params[3]
            self.difficultyAdjustmentPeriod = params[4]
            self.diffSampleSize = params[5]
            self.timeSampleSize = params[6]
            self.hRate = params[7]


        self.bChain = blockChain([[],[],self.lambdaTarget, self.diffForm, self.nextDifficulty])
        self.setBlockArrivalRate();

        self.logFileName = "logs/simulation" + self.diffForm + str(self.maxTime) + "Log.log"
        temp = open(self.logFileName,"w") # Clear the log file 
        temp.close() # Clear the log file

    ###########################################################

    def printToLog(self, text):
        """ Prints to error log file."""
        self.logFile = open(self.logFileName, "a")
        if(not self.logFile):
            print("Error in (blockChain __printToLog__): Log file is an empty object!")
        else:
            self.logFile.write(text + "\n")
        self.logFile.close()
    
    ###########################################################

    def setBlockArrivalRate(self):
        hr = self.hRate.getFunctionValue(self.clock)
        if(isinstance(hr,bool)):
            if(not hr):
                self.printToLog("Error in (simulation - setBlockArrivalRate): No index found, hash rate must be 1.0, although that should have been returned.")
            else:
                self.printToLog("Error in (simulation - setBlockArrivalRate): Boolean index returned, this should be impossible.")
        else:
            self.arrivalRate = self.hRate.getFunctionValue(self.clock)/float(self.bChain.nextDifficulty)
        #print("Block arrival rate is " + str(self.arrivalRate))

    ###########################################################

    def takeNextStep(self):
        """ Computes block-arrival-times, checks them against hashrate updating times,
        and rolls forward time until the next block is discovered."""

        noMoreHashes = False

        while(self.clock >= 0.0 and self.clock < self.maxTime):
            # Accept/reject method of generating randomized timesteps.
            # Generate exponentially-distributed inter-arrival time to determine a candidate
            # block arrival time. If that block arrives after the next hashrate change, then 
            # we move time forward to the next hash change and we try again. If that block
            # Arrives before the next hashrate change, we move time forward to the block arrival,
            # we append the block to the blockchain, and in so doing we compute the next diff.

            self.setBlockArrivalRate() # Update block arrival rate
            u = random.SystemRandom().expovariate(self.arrivalRate) # Random interarrival time, float
            tempClock = self.clock + u # This is a candidate block arrival time.
            nextEventTime = min(tempClock, self.maxTime) 

            # Compute the next hash event time.
            nextHashTime = self.hRate.getNextChangePoint(self.clock)
            noMoreHashes = isinstance(nextHashTime, bool)
            # When we are out of hash events, nextHashTime becomes False, so noMoreHashes becomes true.
            # Once this is the case, we can expect nextEventTime == nextHashTime to regularly return false.
            
            if(not noMoreHashes):
                nextEventTime = min(nextHashTime, nextEventTime) 

            if(nextEventTime == nextHashTime):
                self.clock = nextHashTime
                # If the next event is a hash event, roll time forward to that point.
                
            elif(nextEventTime == tempClock):
                # If the next event is a block addition, roll time forward to that point, add block.
                self.clock = tempClock
                self.bChain.addBlock(self.distortTime())
            else:
                # The only other possibility is the simulation comes to an end.
                self.clock = self.maxTime


    ###########################################################

    def runSim(self):
        """ Run the actual simulation, finishing by writing data to file. """
        bh = len(self.bChain.timeChain)
        oldClock = self.clock
        thisDay = 1
        #print("Beginning simulation.")
        while(abs(self.clock) < self.maxTime):
            # Just in case time accidentally runs backwards...

            self.takeNextStep()
            newClock = self.clock
            #print("Time has adjusted from " + str(oldClock) + " to " + str(newClock))
            # Throw an exception and abort the simulation if time isn't moving forward.
            if(newClock < oldClock):
                self.printToLog("Critical error in (simulation runSim): time running backwards! Holy shit! Aborting simulation by setting time to the maxTime")
                self.clock = self.maxTime
            elif(newClock == oldClock):
                self.printToLog("Critical error in (simulation runSim): time holding still! Holy shit! Aborting simulation by setting time to the maxTime")
                self.clock = self.maxTime
            else: # If time is moving forward correctly, announce when block height has changed or when a day has passed.
                thisBH = len(self.bChain.timeChain)
                if(bh != thisBH):
                    self.printToLog("Blockchain growth: We are at block height " + str(thisBH) + " at time " + str(self.clock) + " and with difficulty " + str(self.bChain.nextDifficulty) + ". We have appended the timestamp " + str(self.bChain.timeChain[-1]) + ".")
                    bh = thisBH
                thisSecond = int(math.ceil(self.clock))
                while(thisSecond > thisDay*86400):
                    print("Day " + str(thisDay) + " has passed...")
                    thisDay = thisDay + 1
        self.printToLog("MaxTime obtained, writing data to file...")
        print("MaxTime obtained, writing data to file...")
        self.writeDataToFile("data/output.csv")

###########################################################

    def distortTime(self):
        #TODO: Implement time distortion policies

        return int(math.ceil(self.clock))

###########################################################

    def writeDataToFile(self, fileName):
        return self.bChain.writeDataToFile(fileName, self.hRate)

#####################EOF###################################

