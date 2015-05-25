""" Represents the main chain of a blockchain.

### Class Attributes ###
chain = []
lambdaTarget = 1.0/60.0
d_Next = 1
diffForm = "bitmonero"

The list, chain = [[t[0], d[0]], [t[1], d[1]], ... [t[n-1],d[n-1]], consists of a sequence of
ordered pairs. The i^th pair represents the data associated with the i^th block of the
blockchain.  The first coordinate of any pair is a timestamp and the second coordinate is a
difficulty score. 

The int, d_Next, represents current difficulty of the blockchain, which is also the difficulty 
of the (n+1)^th block, d[n].  The difficulty, d_Next, is computed directly from array of ordered
pairs. The formula used to compute d_Next depends on a parameter provided by the user upon initialization of an instance of the blockChain class.

The float, lambdaTarget, represents target block arrival time (arrivals per second).

The string, diffForm, tells us which formula to use to compute difficulty.
    ~ if diffForm == "bitmonero" then use the CryptoNote reference code difficulty formula.
    ~ if diffForm == "bitcoin" then use the bitcoin reference code difficulty formula.
    ~ otherwise, specialize a difficulty formuala by hand.

### Methods ###
addBlock ~ Not to be confused with adblock. Takes an integer timestamp as input, and inserts
           a new block in the blockChain with that timestamp. Note: timestamps may not repeat,
           and so if an integer timestamp has already been used in the blockchain, it shall be
           iteratively pushed forward until the least integer timestamp is found  that satisfies
           both (i) greater than or equal to the original timestamp and (ii) unused so far on
            the blockchain.

"""
from Constants import *

import math
import numpy
import os
import errno

class blockChain:

    ## Class attributes ##
    ## The class itself will return these values if called, i.e. blockChain.chain returns [] etc.
    ## These also cause the default values of specific instances of this class.

    timeChain = []
    difficultyChain = []
    lambdaTarget = LAMBDA_TARGET
    diffForm = DIFFICULTY_FORMULA
    nextDifficulty = STARTING_DIFFICULTY
    difficultyAdjustmentPeriod = DIFF_ADJ_PERIOD
    # nextDifficulty = int(math.ceil(1.0/lambdaTarget))
    diffSampleSize = DIFF_SAMPLE_SIZE
    timeSampleSize = TIME_SAMPLE_SIZE
    logFileName = "logs/blockChainLog.log"

    # Historically, difficulty default is 1. But I usually like to start my differential equations
    # and difference equations simulations at equilibrium to prevent transient behavior from
    # confounding results. If initial hash rate is always assumed to be 1 H per second, this
    # equilibrium solution is between d_Next = int(math.ceil(1.0/lambdaTarget) and 
    # d_Next = int(math.floor(1.0/lambdaTarget)). Since difficulty is an integer and we we
    # want to avoid zero, we use the ceiling function.

    # d_Next = int(math.ceil(1.0/lambdaTarget))

    ###########################################################

    def __init__(self, params=None):
        paramsAreEmptyObject = not params # True if params is empty
        paramsAreNone = (params==None)    # True if params==None, when params ahven't been passed in at all.
        paramsPassedIn = not(paramsAreEmptyObject or paramsAreNone) # True if something nonempty was passed

        if(paramsPassedIn):
            ## User-defined instance attributes ##
            # bc = blockChain([],[],1.0/60.0,"bitmonero",1)
            self.timeChain = params[0]
            self.difficultyChain = params[1]
            self.lambdaTarget = params[2]
            self.diffForm = params[3]
            self.nextDifficulty = params[4] 

            # self.nextDifficulty = int(math.ceil(self.d_Next)) # It is good form dynamically to use this

            if(self.diffForm == "bitmonero"):
                self.diffSampleSize = DIFF_SAMPLE_SIZE
                self.timeSampleSize = TIME_SAMPLE_SIZE
            elif(self.diffForm == "bitcoin"):
                self.diffSampleSize = DIFF_SAMPLE_SIZE_BITCOIN
                self.timeSampleSize = TIME_SAMPLE_SIZE_BITCOIN
                self.difficultyAdjustmentPeriod = DIFF_ADJ_PERIOD_BITCOIN
            else:
                self.diffSampleSize = params[5]
                self.timeSampleSize = params[6]
                self.difficultyAdjustmentPeriod = params[7]

        self.make_sure_path_exists("logs")
        self.logFileName = "logs/blockChain" + self.diffForm + ".log"
        temp = open(self.logFileName,"w") # Clear the log file 
        temp.close() # Clear the log file

    ###########################################################

    def printToLog(self, text):
        self.logFile = open(self.logFileName, "a")
        if(not self.logFile):
            print("Error in (blockChain __printToLog__): Log file is an empty object!")
        else:
            self.logFile.write(text + "\n")
        self.logFile.close()

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    
    ###########################################################

    def setNextDifficulty(self):
        """ Compute difficulty of next block """
        blockHeight = len(self.timeChain)

        if(blockHeight > self.diffSampleSize):
            # We only bother computing difficulty if we have at least sampleSize blocks in our blockchain. And we only consider the top sampleSize blocks.
            sampleTimeChain = self.timeChain[-self.diffSampleSize:]
            sampleDifficultyChain = self.difficultyChain[-self.diffSampleSize:]
            cumDiff = 0
            deltaT = 0
            DAPeriod = self.difficultyAdjustmentPeriod

            if(self.diffForm == "bitmonero"):
                # First order the timestamps, but not difficulty
                # Then slice out the outlying 1/12 blocks from the top and bottom, leaving 5/6
                # Then compute sample rate as usual from this particularly sampled data.
                toSlice = int(math.floor(1.0/12.0*float(self.diffSampleSize)))

                sampleTimeChain = sorted(sampleTimeChain)
                sampleTimeChain = sampleTimeChain[toSlice:-toSlice]
                deltaT = sampleTimeChain[-1] - sampleTimeChain[0]

                if(deltaT > 0):
                    # Since block height is greater than sampleSize,
                    # and since block times must be at least one second
                    # apart, we have at least deltaT > sampleSize - 1,
                    # So we should never fail this test.
                    sampleDifficultyChain = sampleDifficultyChain[toSlice:-toSlice]
                    cumDiff = sum(sampleDifficultyChain)
                    self.nextDifficulty = float(cumDiff)/(self.lambdaTarget*float(deltaT))

                else:
                    self.printToLog("Error in (blockChain setNextDifficulty): deltaT computed to be zero or negative.")
                    
                
            elif(self.diffForm == "bitcoin"):
                # Simply compute the sample rate from the top sampleSize blocks.
                if(blockHeight % DAPeriod == 0):

                    cumDiff = sum(sampleDifficultyChain)
                    deltaT = max(sampleTimeChain) - min(sampleTimeChain)
              
                    if(deltaT > 0):
                        # Since block height is greater than sampleSize,
                        # and since block times must be at least one second
                        # apart, we have at least deltaT > sampleSize - 1,
                        # So we should never fail this test.
                        self.nextDifficulty = float(cumDiff)/(self.lambdaTarget*float(deltaT))

                    else:
                        self.printToLog("Error in (blockChain setNextDifficulty): deltaT computed to be zero or negative.")


    ###########################################################

    def addBlock(self, params=None):
        """
        Takes an integer timestamp as input, and inserts a new block in the blockChain with 
        that timestamp. Note: timestamps may not repeat, and so if an integer timestamp has
        already been used in the blockchain, this function is recursively called with +1 until 
        the least integer timestamp is found that satisfies both (i) greater than or equal to 
        the original timestamp and (ii) unused so far on the blockchain.

        """
        paramsAreEmptyObject = not params # True if params is empty
        paramsAreNone = (params==None)    # True if params==None
        paramsPassedIn = not(paramsAreEmptyObject or paramsAreNone) # True if something was passed

        if(not paramsPassedIn or paramsAreNone):
            self.printToLog("Error in (blockChain addBlock): Did not pass in time to add to blockchain!")
        else:
            timeToAdd = params
            timeIsInt = isinstance(timeToAdd, int)
            timeIsFloat = isinstance(timeToAdd,float)

            if(not timeIsInt or not timeIsFloat):
                self.printToLog("Error in (blockChain addBlock): Timestamp of new block not a number.")
            elif(not timeIsInt and timeIsFloat):
                self.printToLog("Error in (blockChain addBlock): Timestamp of new block not an integer, rounding up.")
                timeToAdd = int(math.ceil(timeToAdd))

            if(isinstance(timeToAdd,int)):
                self.timeChain.append(timeToAdd)
                self.difficultyChain.append(self.nextDifficulty)
                # Recompute difficulty now that we have new blocks
                self.setNextDifficulty()

    ###########################################################

    def writeDataToFile(self, fileName, hr):
        """ Again, simple: write the entire blockchain and user-provided hash rate 
        to a tab-separated file. """

        self.make_sure_path_exists("data")
        w = open(fileName, "w")
        w.write("Timestamp \t True Hash Rate \t Difficulty \t (LambdaTarg - LambdaHat)/LambdaTarg \t OldDiff \t (LambdaTarg - LambdaHatOld)/LambdaTarg \n");

        index = 0
        while(index < len(self.timeChain)):
            timeStamp = float(self.timeChain[index])
            #print("Floated timestamp = " + str(timeStamp))
            diffish = float(self.difficultyChain[index])
            horseradish = float(hr.getFunctionValue(timeStamp))
            isHorseRadishBool = isinstance(horseradish,bool)
            #print("horseradish = " + str(horseradish))

            """ Error catch: we shouldn't have any zero difficulty values (daikon) or boolean
            hashrates (horseradish). If we have any such values, we have made an error 
            somewhere else. """
            if(diffish == 0.0 or isHorseRadishBool):
                if(diffish == 0.0):
                    self.printToLog("Critical error in (blockChain writeDataToFile): A zero (new) difficulty snuck into the final result somehow, despite all our failsafes.")
                if(isHorseRadishBool):
                    self.printToLog("Critical error in (blockChain writeDataToFile): Tried to compute hash rate at time t = " + str(timeStamp) + " and got " + str(horseradish))
                #print("Critical error! A zero (new) difficulty snuck into the final result somehow, despite all our failsafes.\n")
                error = -1.0
            else: 
                error = abs(self.lambdaTarget - horseradish/diffish)/self.lambdaTarget
            
            # Print this block to file.
            sentence = str(timeStamp) + " \t " + str(horseradish) + " \t " + str(diffish) + " \t " + str(error) + "\n"
            w.write(sentence)
            index = index + 1

        return w.close()
