""" Runs and executes the simulation; take an instance of the hashRate class and produce a
randomly generated instance of the blockChain class.

__Primary Data:
bc                         ~ blockChain class; will contain timestamps and difficulties.
hr                         ~ hashRate class; will contain hash rate over time.

__Methods:


__Variables:
bc                         ~ blockChain class; will contain timestamps and difficulties.
hr                         ~ hashRate class; will contain hash rate over time.
clock                      ~ clock
difficultyAdjustmentPeriod ~ re-compute difficulty every `this many' blocks.
sampleSize                 ~ Compute difficulty using the top sampleSize blocks.
timeStampSampleSize        ~ Blocks rejected if their timestamps occur before the median of the
                             timestamps of the top timeStampSampleSize blocks.
lambdaTarget               ~ target block arrival rate (arrivals per unit time)
maxTime                    ~ simulation maximum running time
"""
import math
import random
from hashRate import *
from blockChain import *


class simulation:

###########################################################

    def __init__(self,  params):
        """ Typical __init__ function. The input `params` should include 8 pieces as 
        described.  If params is an array with length less than 8, you are doing it
         wrong, so we will just use defaults.

        Variables:
        difficultyAdjustmentPeriod ~ params[0] ~ re-compute difficulty every `this many' blocks 
        sampleSize                 ~ params[1] ~ When computing difficulty use this many blocks
        timeStampSampleSize        ~ params[2] ~ When rejecting blocks, use this many blocks
        lambdaTarget               ~ params[3] ~ Target arrivals per second, max likelihood
                                                 estimate for this is sampleSize/deltaT
        maxTime                    ~ params[4] ~ Maximum simulation running time.
        attackPolicy               ~ params[5] ~ TODO: for now this is a probability of pushing
                                                 a timestamp ahead by 7200 seconds (2 hours)
        hashRateDescription        ~ params[6] ~ String describing hash rate function
        hr                         ~ params[7] ~ Input hash rate, constructed a priori
        """
        # Our simulations are continuous-time, but recording of events occurs at discrete integer-time-valued points.
        self.clock = 0.0 # Clocks always start at 0.0; force into an int before actually using the clock.
        self.logFileName = "logs/simulationLog.log"
        temp = open(self.logFileName,"w")
        temp.close()
        self.printToLog("Beginning new simulation construction log.")


        if( not params or len(params)!= 8): # Empty arrays are false, so we start our object with default values... or if our parameter vector is the wrong length, we will just use defaults.
            if( not params): 
                self.printToLog("Warning in (simulation __init__): No parameters used to instantiate simulation. Using defaults.")
            else: 
                self.printToLog("Error in (simulation __init__): Parameter array used to instantiate simulation is wrong dimension. Using defaults.")
            x = True;
            self.difficultyAdjustmentPeriod = 1
            self.sampleSize = 720
            self.timeStampSampleSize = 60
            self.lambdaTarget = 1.0/60.0
            self.maxTime = 1000000.0
            self.nextHashTime = float(self.maxTime)
            self.attackPolicy = [0.0,72] # With probability p_i, apply shift shift_i. self.attackPolicy = [[p_0, shift_0], [p_1, shift_1], ...] 
            self.hashRateDescription = "Simple stepwise hash rate."

            quarters = self.maxTime/4.0
            tomato=[0.0,quarters,2.0*quarters,3.0*quarters] # t is for time, t is for tomato
            horseradish=[1,10,1,100] # h is for horseradish, h is for hash value

            #tomato = [0.0] # t is for time, t is for tomato
            #horseradish = [1] # h is for horseradish, h is for hash value
            self.hr = hashRate(tomato,horseradish,self.hashRateDescription, self.maxTime)

            # Construct the blockchain object and get first difficulty, which should be 1, and first block arrival rate
            self.bc = blockChain([self.sampleSize, self.difficultyAdjustmentPeriod, self.lambdaTarget, self.timeStampSampleSize])
            self.currentDifficulty = self.bc.getNextDifficulty()
            self.currentBlockArrivalRate = float(self.hr.getCurrentHashRate(0.0))/float(self.currentDifficulty)

        else:
            test = []
            test = [isinstance(params[0], int), isinstance(params[1],int), isinstance(params[2],int), isinstance(params[3],float), isinstance(params[4], int), isinstance(params[6], string)]
            x = True;
            for thing in test:
                x = x and thing
            if(not x):
                self.printToLog("Error in (simulation __init__): parameter array correct length but at least one element of wrong type.")
                y = test.index(False);
                self.printToLog("...... in particular, params[" + y + "] is first element in the array that is not the correct type.")
            else:
                self.difficultyAdjustmentPeriod = params[0]
                self.sampleSize = params[1]
                self.timeStampSampleSize = params[2]
                self.lambdaTarget = params[3]
                self.maxTime = params[4] # Should be a float already
                self.nextHashTime = float(self.maxTime)
                self.attackPolicy = params[5]
                self.hashRateDescription = params[6]
                self.hr = hashRate(params[7],params[8],self.hashRateDescription)

                # Construct the blockchain object and get first difficulty, which should be 1, and first block arrival rate
                self.bc = blockChain([self.sampleSize, self.difficultyAdjustmentPeriod,self.lambdaTarget,self.timeStampSampleSize])
                self.currentDifficulty = self.bc.getNextDifficulty()
                self.currentBlockArrivalRate = float(self.hr.getCurrentHashRate(0.0))/float(self.currentDifficulty)

        if(not isinstance(self.currentDifficulty,int)):
            self.printToLog("Warning in (simulation __init__): Initial difficulty incorrectly set as non-integer.")
            if(self.currentDifficulty != 1.0):
                self.printToLog("...... initial difficulty not one, either.")
        elif(self.currentDifficulty != 1):
            self.printToLog("Warning in (simulation __init__): Initial difficulty set to integer other than 1")
        self.printToLog("Tried to construct simulation and got " + str(x));

###########################################################

    def printToLog(self, text):
        self.logFile = open(self.logFileName, "a")
        if(not self.logFile):
            print("Error in (blockChain __printToLog__): Log file is an empty object!")
        else:
            self.logFile.write(text + "\n")
        self.logFile.close()
        
###########################################################

    def runSim(self):
        """ Run the actual simulation, finishing by writing data to file. """
        bh = self.bc.getBlockHeight()
        oldClock = self.clock
        thisDay = 1
        while(abs(self.clock) < self.maxTime):
            self.takeNextStep()
            newClock = self.clock
            # Throw an exception and abort the simulation if time isn't moving forward.
            if(newClock < oldClock):
                self.printToLog("Critical error in (simulation runSim): time running backwards! Holy shit! Aborting simulation by setting time to the maxTime")
                self.clock = self.maxTime
            elif(newClock == oldClock):
                self.printToLog("Critical error in (simulation runSim): time holding still! Holy shit! Aborting simulation by setting time to the maxTime")
                self.clock = self.maxTime
            else: # If time is moving forward correctly, announce when block height has changed or when a day has passed.
                thisBH = self.bc.getBlockHeight()
                if(bh != thisBH):
                    self.printToLog("%%%%% Blockchain growth %%%%% We are at block height " + str(thisBH) + " at time " + str(self.clock) + " and with difficulty " + str(self.bc.getNextDifficulty()) + ". We have appended the timestamp " + str(self.bc.getTopTimeStamp()) + ".")
                    bh = thisBH
                thisSecond = int(math.ceil(self.clock))
                while(thisSecond > thisDay*86400):
                    print("Day " + str(thisDay) + " has passed...")
                    thisDay = thisDay + 1
        self.printToLog("MaxTime obtained, writing data to file...")
        print("MaxTime obtained, writing data to file...")
        self.writeDataToFile("data/output.csv")

###########################################################

    def takeNextStep(self):
        """ Computes block-arrival-times, checks them against hashrate updating times,
        and rolls forward time until the next block is discovered."""

        if(self.clock >= 0.0 and self.clock < self.maxTime):
            # Set current difficulty and verify it is a nonzero integer. 
            self.currentDifficulty = self.bc.getNextDifficulty() # Current difficulty.
            if(not self.currentDifficulty): # zero objects are false
                self.printToLog("Critical Error in (simulation takeNextStep): Difficulty has been computed to be zero object. Other warnings or errors should have been thrown. To ensure smooth workflow, setting difficulty to 1 for this block, but this error must be addressed and we can't proceed with the sim.")

            elif(not isinstance(self.currentDifficulty, int)):
                self.printToLog("Error in (simulation takeNextStep): Current difficulty has been computed as a non-integer, in particular, self.currentDifficulty = " + str(self.currentDifficulty) + ". Simulations cannot proceed.")
            else:
                """ If current difficulty is a nonzero integer and current clock is within
                the support of the simulation, [0, maxTime], compute block arrival rate and 
                generate random arrival time. Roll time forward to either this arrival time or 
                the next hashrate changepoint. If we roll time forward to this arrival time, 
                then we add a block; if we roll time forward to the hashrate changepoint, we 
                update hash rate and then generate a new random arrival time... lather, rinse...
                and we don't stop until we have found a block."""

                self.currentBlockArrivalRate = float(self.hr.getCurrentHashRate(self.clock))/float(self.currentDifficulty)
                u = random.SystemRandom().expovariate(self.currentBlockArrivalRate) # Random interarrival time, float
                self.nextHashTime = self.hr.getNextHashEventTime(self.clock) # Next hashrate changepoint, float
                temp = self.clock + u

                while(temp > min(self.nextHashTime,self.maxTime) and self.clock < self.maxTime):
                    #print("This is the song that never ends...")
                    # We enter this while loop whenever self.clock < min(self.nextHashTime, self.maxtime) < temp, which is true whenever the next event is NOT a block arrival.
                    # Exiting this while loop, we should have the next block arrival time stored in `temp' and no hash events between self.clock and temp.
                    if(self.nextHashTime < self.maxTime):
                        # In this case, self.clock < self.nextHashTime < temp < self.maxTime so we roll time forward to the next hash event and re-roll.
                        self.clock = self.nextHashTime  # Roll time forward
                        self.nextHashTime = self.hr.getNextHashEventTime(self.clock) # Find next hash arrival time.
                        self.currentBlockArrivalRate = float(self.hr.getCurrentHashRate(self.clock))/float(self.currentDifficulty) # Recompute block arrival rate given new hash rate
                        u = random.SystemRandom().expovariate(self.currentBlockArrivalRate) 
                        temp = self.clock + u # Roll a new block arrival time.
                    else:
                        # In this case, self.clock < self.maxTime < temp < self.nextHashTime so we just roll time forward to the end of the sim.
                        temp = self.maxTime
                
                if(temp < self.maxTime):
                    self.clock = temp # Roll time forward to next block arrival.
                    currentClockInt = int(math.ceil(self.clock))
                    self.bc.addBlock(self.distortTime())
                else:
                    self.printToLog("Warning in (simulation takeNextStep): Next event to occur will happen outside of support [0, maxTime]. Setting clock to maxTime, so we should exit the sim now.")
                    self.clock = self.maxTime

        else:
            self.printToLog("Warning in (simulation takeNextStep): Clock has exceeded support of simulation, [0, maxTime], but takeNextStep was called anyway!.")




###########################################################

    def distortTime(self):
        """ Given a particular time distortion policy, adjust timestamp. """

        # Probability an attacker controls this block is self.attackPolicy[0]
        u = random.SystemRandom().uniform(0.0,1.0);
        result = int(math.ceil(self.clock))
        if(u <= self.attackPolicy[0]):
            result = result + self.attackPolicy[1];

        result = int(math.ceil(result))
        return result;

###########################################################

    def writeDataToFile(self, fileName):
        return self.bc.writeDataToFile(fileName, self.hr)

#####################EOF###################################
