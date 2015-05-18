""" Represents the blockchain.

Primary data consist of a sequence of timestamps and associated difficulties. Ancillary data, which all may be computed freely from primary data, consist of the next difficulty that will be included with the next timestamp

__Methods:
getNextDifficulty()       ~ return the difficulty of the next block. If block height is zero, 
                            return 1. If block height is n < sampleSize, return a special case
                            difficulty computed with smaller-than-usual sample size.
                            If block height is n > sampleSize, return usual difficulty score.
getOldDifficulty()        ~ return the difficulty of the next block *using the old diff algo.* 
addBlock(time)            ~ add block with timestamp `time' to block chain. 
writeDataToFile(filename) ~ publish blockChain object to file `filename' with tab-separated values.
getBlockHeight()          ~ return height of top block (genesis block has height 1)


__Variables:
sampleSize                ~ When computing difficulty, we only consider the top sampleSize blocks
timeStampSampleSize       ~ Only allow blocks with timestamps ``close'' to the top `this many' 
                            blocks. In particular, if M = median(last timeStampSampleSize stamps)
                            and T = max(last timeStampSampleSize timestamps) then only allow
                            timestamps in the interval [M, T+2 hours].
difficultyAdjustmentPeriod~ compute new difficulty every `this many' blocks
lambdaTarget              ~ target block arrival rate (arrivals per unit time)
blocks = []               ~ blocks will take the form [[t_0, d_0, e_0], [t_1, d_1, e_1], ...]
                            where each t_i, d_i, e_i is a float. The t_i represents timestamp,
                            the d_i represents new difficulty algo, the e_i represents old algo.
nextDifficulty            ~ Float object describing difficulty of next block to be added. 
                            If len(blocks[]) == 0, then set nextDiff = 1.
                            If len(blocks[]) < sampleSize, then compute nextDiff using a smaller
                            sample size.
oldDifficulty             ~ Float object describing difficulty of next block to be added (as
                            computed by the old algorithm!)
"""

import math
import numpy

class blockChain:

###########################################################

    def __init__(self, params):
        """ Typical __init__ function. The input `params` should include 4 pieces,
        namely sample size, difficulty adjustment period, target block arrival rate, and
        timeStampSampleSize. If params is an array with length less than 4, you are 
        doing it wrong, so we will just use defaults.

        Variables:
        blocks = []                ~ blocks will take the form [[t_0, d_0, e_0], [t_1, d_1, e_1], ...]
                                     where each t_i, d_i, e_i is a float. The t_i represents timestamp,
                                     the d_i represents new difficulty algo, the e_i represents old algo.
        nextDifficulty             ~ Float object describing difficulty of next block to be added. 
                                     If len(blocks[]) == 0, then set nextDiff = 1.
                                     If len(blocks[]) < sampleSize, then compute nextDiff using a smaller
                                     sample size.
        oldDifficulty              ~ float object, describing difficulty of next block to be added (as
                                     computed by the old algorithm!)
        sampleSize                 ~ int object, describing number of blocks used to compute difficulty.
        difficultyAdjustmentPeriod ~ int object, recompute difficulty every this many blocks.
        lambdaTarget               ~ float object, target block arrival rate (arrivals per second)
        timeStampSampleSize        ~ int object, reject blocks based on a statistic of this many blocks.

        """
        
        self.blocks = []
        self.nextDifficulty = 1
        self.oldDifficulty = 1

        self.logFileName = "logs/blockChainLog.log"
        temp = open(self.logFileName,"w")
        temp.close()
        self.printToLog("Beginning new blockChain construction log.")

        if(not params or len(params)!=4): # Empty arrays are false
            if(not params):
                self.printToLog("Warning in (blockChain __init__): No parameters used to instantiate blockchain. Using defaults.")
                #print("Warning in (blockChain __init__): No parameters used to instantiate blockchain. Using defaults.")
            else: 
                self.printToLog("Error in (blockChain __init__): parameter array used to instantiate blockchain is wrong dimension. Using defaults.")
                
                #print("Error in (blockChain __init__): parameter array used to instantiate blockchain is wrong dimension. Using defaults.")
            self.sampleSize = 720
            self.difficultyAdjustmentPeriod = 1
            self.lambdaTarget = 1.0/60.0
            self.timeStampSampleSize = 60
            self.nextDifficulty = int(math.ceil(1.0/self.lambdaTarget))
            self.oldDifficulty = self.nextDifficulty

        else:
            test = []
            test = [isinstance(params[0],int), isinstance(params[1],int), isinstance(params[2],float), isinstance(params[3], int)]
            x = True;
            for thing in test:
                x = x and thing
            if(not x):
                self.printToLog("Error in (blockChain __init__): parameter array correct length but at least one element of wrong type.")
                #print("Error in (blockChain __init__): parameter array correct length but at least one element of wrong type.")
                y = test.index(False);
                self.printToLog("...... in particular, params[" + y + "] is first element in the array that is not the correct type.")
                #print("...... in particular, params[" + y + "] is first element in the array that is not the correct type.")

            else:
                self.sampleSize = params[0]
                self.difficultyAdjustmentPeriod = params[1]
                self.lambdaTarget = params[2]
                self.timeStampSampleSize = params[3]
                self.nextDifficulty = int(math.ceil(1.0/self.lambdaTarget))
                self.oldDifficulty = self.nextDifficulty



###########################################################

    def printToLog(self, text):
        self.logFile = open(self.logFileName, "a")
        if(not self.logFile):
            print("Error in (blockChain __printToLog__): Log file is an empty object!")
        else:
            self.logFile.write(text + "\n")
        self.logFile.close()
    
###########################################################

    def getBlockHeight(self):
        """ Simple enough: return block height"""
        return len(self.blocks)
    
###########################################################

    def getTopTimeStamp(self):
        """ Simple enough: return time stamp of top block, if one exists"""
        result = -1
        if(not self.blocks):
            self.printToLog("Warning in (blockChain getTopTimeStamp): Attempted to find timestamp of top block on an empty blockchain! Returning -1.")
        else:
            topBlock = self.blocks[-1]
            topTimeStamp = topBlock[0]
            result = topTimeStamp
        return result

###########################################################

    def writeDataToFile(self, fileName, hr):
        """ Again, simple: write the entire blockchain and user-provided hash rate 
        to a tab-separated file. """

        w = open(fileName, "w")
        w.write("Timestamp \t True Hash Rate \t New Diff \t (LambdaTarg - LambdaHat)/LambdaTarg \t OldDiff \t (LambdaTarg - LambdaHatOld)/LambdaTarg \n");
        for block in self.blocks:
            """ Starting with the genesis block, write each block's values to file."""
            tomato = float(block[0]) # t is for tomato, t is for timestamp
            horseradish = float(hr.getCurrentHashRate(block[0])) # h is for horseradish, h is for hash rate
            daikon = float(block[1]) # d is for daikon, d is for (new) difficulty
            okra = float(block[2]) # o is for okra, o is for old difficulty.

            """ Error catch: we shouldn't have any zero difficulty values (daikon or okra). If 
            we have any such values, we have made an error somewhere in the construction of the
            blockChain object. """
            if(daikon == 0.0):
                self.printToLog("Critical error in (blockChain writeDataToFile): A zero (new) difficulty snuck into the final result somehow, despite all our failsafes.")
                #print("Critical error! A zero (new) difficulty snuck into the final result somehow, despite all our failsafes.\n")
                error = -1.0
            else: 
                errorNew = abs(self.lambdaTarget - horseradish/daikon)/self.lambdaTarget

            if(okra == 0.0):
                self.printToLog("Critical error! A zero (old) difficulty snuck into the final result somehow, despite all our failsafes.")
                #print("Critical error! A zero (old) difficulty snuck into the final result somehow, despite all our failsafes.\n")
                error = -1.0
            else: errorOld = abs(self.lambdaTarget - horseradish/okra)/self.lambdaTarget

            
            # Print this block to file.
            sentence = str(tomato) + " \t " + str(horseradish) + " \t " + str(daikon) + " \t " + str(errorNew) + "\t" + str(okra) + "\t" + str(errorOld) + "\n"
            w.write(sentence)

        return w.close()


###########################################################  

    def addBlock(self, timeStamp):
        """ Not to be confused with AdBlock. Append an ordered triple of the form 
        [timestamp, newDifficulty, oldDifficulty] to the block chain object, where 
        timestamp is provided by the user and the difficulty values are determin-
        istically computed from the rest of the blockChain."""

        isTimeStampFloat = isinstance(timeStamp, int); # Return true if proposed timeStamp is an integer.
        if(not isTimeStampFloat):
            self.printToLog("Error in (blockChain addBlock): proposed timestamp is not an integer. Rounding up to nearest integer (ceiling function).")
            timeStamp = int(math.ceil(timeStamp))
            #print("Error in (blockChain addBlock): proposed timestamp is not an integer. Rounding up to nearest integer (ceiling function).")


        # Run quick check for zero diff. If zero, still append block, but throw an error.
        validDifficulties = True;
        daikon = self.nextDifficulty; # d is for daikon, d is for (new) difficulty
        okra = self.oldDifficulty; # o is for okra, o is for old difficulty
        if(daikon==0.0):
            validDifficulties = False;
            self.printToLog("Error in (blockChain addBlock): tried to add block with a new difficulty of zero.")
            #print("Error in (blockChain addBlock): tried to add block with a new difficulty of zero")
        else:
            if(okra==0.0):
                validDifficulties = False;
                self.printToLog("Error in (blockChain addBlock): tried to add block with an old difficulty of zero.")
                #print("Error in (blockChain addBlock): tried to add block with an old difficulty of zero")

        """ Timestamps must be separated by at least one second. So we will keep pushing our 
        timestamp forward by one second until this is no longer an issue. 

        Recall that the timePoints list need not be ordered, and so we require multiple 
        sweeps looking for collisions. And, unlike zero diff, this isn't an error, just part of
        the usual addition-to-blockchain process.

        Also notice that we must first re-shuffle the timestamp and then determine whether it
        is within our allowable range [M,T+2h], rather than testing before reshuffling. 
        If we attempt it in the other order, timestamps could appear outside of [M,T+2h]
        """
        #print("Test test! len(self.blocks) = " + str(len(self.blocks)) + " and self.sampleSize = " + str(self.sampleSize))
        m = min(len(self.blocks), self.sampleSize) # Using available blocks up to sampleSize
        sampleBlocks = self.blocks[-m:] # Just consider the top blocks.
        timePoints = []
        # Array that will consist of timePoints associated by index with difficulties
        if(not sampleBlocks):
            self.printToLog("Warning in (blockChain addBlock): sampleBlocks element is empty! Problematic. However, since block height is " + str(self.getBlockHeight()) + " and since we are only considering up to " + str(self.sampleSize) + " of the top blocks... could this be a sensible warning due to early blockChain issues?")
            #print("Error in (blockChain addBlock): sampleBlocks element is empty! Problematic.")
        else:
            for block in sampleBlocks: # Populate our data arrays
                timePoints.append(block[0])

            # Look for colliding timepoints.
            collision = True;
            while(collision):
                thisSweep = False;
                for s in timePoints:
                    if(not isinstance(s, int)):
                        self.printToLog("Error in (blockChain addBlock): Some non-integer timestamp has been discovered! This error should be addressed.")
                        #print("Error in (blockChain addBlock): Some non-integer timestamp has been discovered! This error should be addressed.")
                    if(timeStamp == s):
                        timeStamp = timeStamp + 1
                        thisSweep = True;
                collision = thisSweep;

        """ We may only allow timestamps in the interval [M, T+2] where M = median of the 
        timestamps of the previous timeStampSampleSize blocks, and where T is the maximum
        timestamp of the previous timeStampSampleSize blocks. """
        m = min(len(self.blocks),self.timeStampSampleSize)
        sampleBlocks = self.blocks[-m:]
        timePoints = []
        for block in sampleBlocks:
            timePoints.append(block[0])
        if(not timePoints):
            self.printToLog("Warning in (blockChain addBlock): timePoints object is empty so computing the median is inappropriate. Setting minTimeStamp to negative 7200. Notice that block height is " + str(self.getBlockHeight()) + " and so this could make sense.")
            #print("Error in (blockChain addBlock): timePoints object is empty so computing the median is inappropriate. Setting minTimeStamp to negative 7200.")
            minTimeStamp = -7200
        else:
            minTimeStamp = numpy.median(timePoints) # Median of past few blocks min.

        if(not timePoints): # Empty objects are false.
            maxTimeStamp = 7200
            self.printToLog("Warning in (blockChain addBlock): blockChain appears to be empty, so we are setting the first allowable timePoint to be 7200.")
            #print("Error in (blockChain addBlock): blockChain appears to be empty, so first allowable timePoint is 7200.")
        else:
            maxTimeStamp = max(timePoints) + 7200 # 2 hours ahead of most futuristic timestamp max.


        legitimateTimeStamp = ((minTimeStamp <= timeStamp) and (timeStamp <= maxTimeStamp))
        if(not legitimateTimeStamp):
            self.printToLog("Warning in (blockChain addBlock): Block is rejected! Time stamp outside allowable window, where timeStamp = " + str(timeStamp) + ", and the allowable window is [" + str(minTimeStamp) + "," + str(maxTimeStamp) + "].")
            print("Block is rejected! Time stamp outside allowable window, where timeStamp = " + str(timeStamp) + ", and the allowable window is [" + str(minTimeStamp) + "," + str(maxTimeStamp) + "].")
        else:            
            """ We append blocks with the timestamp and difficulty, even if timestamp has
            been reshuffled and even if difficulty is an unfortunate non-positive. """
            thisBlock = [timeStamp, daikon, okra]; # Construct block object
            self.blocks.append(thisBlock) # Append

            # Update blockchain inherent data (which will be done before calling anyway, but still)
            self.blockHeight = len(self.blocks) # Update height
            # If appropriate, re-compute difficulties.
            if(self.blockHeight % self.difficultyAdjustmentPeriod == 0): 
                self.nextDifficulty = self.getNextDifficulty()
                self.oldDifficulty = self.getOldDifficulty()
        
        validExperiment = validDifficulties and legitimateTimeStamp
        return validExperiment # If timestamp was rejected, or if difficulties were negative, return false.

###########################################################  

    def getNextDifficulty(self):
        """ Using new difficulty algorithm and the current state of the blockchain,
        compute the difficulty of the next block. Default is to return 1/target block arrival rate."""

        l = len(self.blocks)
        s = self.sampleSize
        #print("Process check in (blockChain getNextDifficulty): [l,s] = [" + str(l) + "," + str(s) + "].")
        m = min(len(self.blocks), self.sampleSize) # Using available blocks up to sampleSize
        result = 1.0/self.lambdaTarget # We will return this value if all else fails.

        if m>=2:
            """ Assuming we have at least two blocks, we can compute difficulty in the usual way, but
            with a possibly smaller sample size... """
        
            sampleBlocks = self.blocks[-m:] # Just consider the top blocks.

            # Array that will consist of timepoints.
            timePoints = []
            # Array that will consist of difficulties associated by index with the timePoints
            difficultyValues = [] 
            for block in sampleBlocks: # Populate our data arrays
                timePoints.append(block[0])
                difficultyValues.append(block[1])

            # Compute deltaT, the difference between last order statistic and first order stat.
            deltaT = 0.0
            if(not timePoints):
                if(not sampleBlocks):
                    self.printToLog("Error in (blockChain getNextDifficulty): Computing timePoints failed!!11, sample blockChain is empty!")
                    #print("Error in (blockChain getNextDifficulty): Computing timePoints failed!!11, sample blockChain is empty!")
                else:
                    self.printToLog("Error in (blockChain getNextDifficulty): Computing timePoints failed!!11, empty object. But len(sampleBlocks) = " + str(len(sampleBlocks)) + " and first timepoint is sampleBlocks[0][0] = " + sampleBlocks[0][0] + ".")
                    #print("Error in (blockChain getNextDifficulty): Computing timePoints failed!!11, empty object. But len(sampleBlocks) = " + str(len(sampleBlocks)) + " and first timepoint is sampleBlocks[0][0] = " + sampleBlocks[0][0] + ".\n")
            else:
                maxTime = float(max(timePoints))
                minTime = float(min(timePoints))
                deltaT = maxTime - minTime

            # Delta T should be positive. This ``if'' case should never occur.
            if(deltaT <= 0.0):
                self.printToLog("Error in (blockChain getNextDifficulty): negative deltaT computed, although at least two timepoints exist. This error should never occur, and if it does, we will simply set deltaT equal to 1.0 for simplicity.")
                #print("Error in (blockChain getNextDifficulty): negative deltaT computed, although at least two timepoints exist. This error should never occur, and if it does, we will simply set deltaT equal to 1.0 for simplicity.")
                deltaT = 1.0
            
            # Difficulty of every block should be positive. This ``if'' case should never occur.
            cumDiff = sum(difficultyValues) # Sum difficulty of top blocks, for computing mean.
            if(cumDiff <= 0.0):
                self.printToLog("Error in (blockChain getNextDifficulty): negative cumulative difficulty computed. This error should never occur, and if it does, we will simply set cumulative difficulty equal to m for simplicity (minimum difficulty allowable).")
                #print("Error in (blockChain getNextDifficulty): negative cumulative difficulty computed. This error should never occur, and if it does, we will simply set cumulative difficulty equal to m for simplicity (minimum difficulty allowable).")
                cummDiff = m # Minimum allowable difficulty.


            averageDifficulty = float(sum(difficultyValues))/float(m)
            lambdaHat = float(m)/float(deltaT)
            
            # result = difficulty of next block.
            result = float(lambdaHat)*float(averageDifficulty)/float(self.lambdaTarget) 
            if(result == 0.0):
                self.printToLog("Critical error in (blockChain getNextDifficulty): zero difficulty computed. We used lambdaHat " + str(float(lambdaHat)) + " and averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(float(self.lambdaTarget)) + ". To ensure smooth workflow, setting difficulty to 1 for this block, but this error must be addressed.")
                #print ("Critical error in (blockChain getNextDifficulty): zero difficulty computed. We used lambdaHat " + str(float(lambdaHat)) + " and averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(float(self.lambdaTarget)) + ". To ensure smooth workflow, setting difficulty to 1 for this block, but this error must be addressed.")
                result = 1.0/self.lambdaTarget

        elif m==1:
            """ If we only have one block, we compute difficulty `in the usual way' but there
            is no need to compute the average difficulty or anything silly like that. """

            averageDifficulty = 1.0 # If we only have one block, it's diff was 1.0
            deltaT = float(self.blocks[0][0]);
            lambdaHat = 1.0/deltaT; # With only one block, lambdaHat = 1/float(self.blocks[0][0]), ie 1/t the timestamp of the only block.
            result = lambdaHat*float(averageDifficulty)/float(self.lambdaTarget) 
            if(result == 0.0):
                self.printToLog("Warning in (blockChain getNextDifficulty): Edge case detected, possible error. With only one block, we computed a difficulty of zero because we had averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(self.lambdaTarget) + " and only one timestamp, providing mle rate " + str(math.ceil(1.0/float(self.blocks[0][0]))) + ". To ensure smooth workflow, setting difficulty to 1/target lambda for this block, but this error may need to be addressed.")
                #print ("Warning in (blockChain getNextDifficulty): Edge case detected, possible error. With only one block, we computed a difficulty of zero because we had averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(self.lambdaTarget) + " and only one timestamp, providing mle rate " + str(math.ceil(1.0/float(self.blocks[0][0]))) + ". To ensure smooth workflow, setting difficulty to 1 for this block, but this error may need to be addressed.")
                result = 1.0/self.lambdaTarget

        elif(m<=0):
            """ If the blockchain is empty, difficulty of the next block is just 1.0, the default """
            self.printToLog("Warning in (blockChain getNextDifficulty): we can't generate difficulty with " + str(m) + " blocks, so we set difficulty to 1/target lambda. Genesis block stuff.")
            #print("Warning in (blockChain getNextDifficulty): we can't generate difficulty with " + str(m) + " blocks, so we set difficulty to 1. Genesis block stuff.")
            result = 1.0/self.lambdaTarget

        result = int(math.ceil(result))
        return result

###########################################################  

    def getOldDifficulty(self):
        """ Using new difficulty algorithm and the current state of the blockchain,
        compute the difficulty of the next block. Return 1/lambdaTarget if all else
        fails. """
        result = 1.0/self.lambdaTarget
        m = 0	
        if(not self.blocks):
            self.printToLog("Error in (blockChain getOldDifficulty): Block list is empty!")
            #print("Error in (blockChain getOldDifficulty): Block list is empty!")
        else:
            m = min(len(self.blocks), self.sampleSize) 
            if(m>=2):
                sampleBlocks = self.blocks[-m:] 
                if(not sampleBlocks):
                    self.printToLog("Error in (blockChain getOldDifficulty): sample of blockchain is empty, returning difficulty 1/target lambda.")
                    result = 1.0/self.lambdaTarget
                else:    
                    timePoints = []
                    difficultyValues = [] 
                    for block in sampleBlocks: 
                        timePoints.append(block[0])
                        difficultyValues.append(block[1])

                    timePoints = sorted(timePoints) # Sort timepoints. Because cryptonote.

                    # Rather than using the whole set of m top blocks, we use the middle 
                    # m-2*numSlice blocks from that array, or about 5/6*m blocks. This is 
                    # because we discard the top and bottom 1/2*m blocks.
                    numSlice = int(math.floor(1.0/12.0*float(m))) # Number of blocks to remove from top and bottom.
                    if(not numSlice):
                        self.printToLog("Warning in (blockChain getOldDifficulty): number of blocks to be sliced off either end of the blockchain before computing difficulty (numSlice) has been computed to be zero. This strongly suggests that blockChain height is strictly less than 12. In this case, we do no slicing and just compute difficulty using every block. In fact, we have numSlice = " + str(numSlice) + " and block height = " + str(self.getBlockHeight()))
                    else:
                        timePoints = timePoints[numSlice:-numSlice]
                        difficultyValues = timePoints[numSlice:-numSlice]

                    if(not timePoints):
                        self.printToLog("Warning in (blockChain getOldDifficulty): Blockchain is so short that slicing outliers is impossible. Until blockChain has exceeded length " + str(2.0*numSlice) + ", whereas our current block height is " + str(self.getBlockHeight()) + " so simply declaring difficulty to be 1/target lambda.")
                        result = 1.0/self.lambdaTarget
                    else:
                        # Compute deltaT, the difference between last order statistic and first order stat.
                        deltaT = 0.0
                        if(not timePoints):
                            if(not sampleBlocks):
                                self.printToLog("Error in (blockChain getOldDifficulty): Computing timePoints failed!!11, sample blockChain is empty! But we should have already checked for this possibility...")
                            else:
                                self.printToLog("Error in (blockChain getOldDifficulty): Computing timePoints failed!!11, empty object. But len(sampleBlocks) = " + str(len(sampleBlocks)) + " and first timepoint is sampleBlocks[0][0] = " + str(sampleBlocks[0][0]) + " so something is certainly going wonky.")
                        else:
                            maxTime = float(max(timePoints))
                            minTime = float(min(timePoints))
                            deltaT = maxTime - minTime

                        # Delta T should be positive. This ``if'' case should never occur.
                        if(deltaT <= 0.0):
                            self.printToLog("Error in (blockChain getOldDifficulty): negative deltaT computed, although at least two timepoints exist. This error should never occur, and if it does, we will simply set deltaT equal to 1.0 for simplicity.")
                            deltaT = 1.0

                        cumDiff = sum(difficultyValues)
                        if(cumDiff <= 0.0):
                            self.printToLog("Error in (blockChain getOldDifficulty): negative cumulative difficulty computed. This error should never occur, and if it does, we will simply set cumulative difficulty equal to m for simplicity (minimum difficulty allowable).")
                            cumDiff = m
                        averageDifficulty = float(sum(difficultyValues))/float(m)
                        lambdaHat = float(m)/float(deltaT)        

                        # result = difficulty of next block.
                        result = float(lambdaHat)*float(averageDifficulty)/float(self.lambdaTarget) + float(deltaT - 1.0)/float(deltaT)
                        if(result <= 0.0):
                            self.printToLog("Critical error in (blockChain getOldDifficulty): nonpositive difficulty computed. We used lambdaHat " + str(float(lambdaHat)) + " and averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(float(self.lambdaTarget)) + ". To ensure smooth workflow, setting difficulty to 1/target lambda for this block, but this error must be addressed.")
                            result = 1.0/self.lambdaTarget
            elif(m==1):
                averageDifficulty = 1.0
                deltaT = float(self.blocks[0][0])
                lambdaHat = 1.0/deltaT; 
                result = lambdaHat*float(averageDifficulty)/float(self.lambdaTarget) + (deltaT - 1.0)/deltaT
                if(result == 0.0):
                    self.printToLog("Warning in (blockChain getOldDifficulty): Edge case detected, possible error. With only one block, we computed a difficulty of zero because we had averageDifficulty " + str(float(averageDifficulty)) + " and lambdaTarget " + str(self.lambdaTarget) + " and only one timestamp, providing mle rate " + str(math.ceil(1.0/float(self.blocks[0][0]))) + ". To ensure smooth workflow, setting difficulty to 1/target lambda for this block, but this error may need to be addressed.")
                    result = 1.0/self.lambdaTarget
            elif(m<=0):
                print("Warning in (blockChain getOldDifficulty): we can't generate difficulty with " + str(m) + " blocks, so we set difficulty to 1/target lambda. Genesis block stuff?")
                result = 1.0/self.lambdaTarget

        result = int(math.ceil(result))
        return result

#####################EOF###################################
