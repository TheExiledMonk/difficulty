""" The hashrate class, which is a time-series object; ping with time, return with value.
Data is piecewise constant between timepoints.

__Variables: 
time                  ~ array of time points, which are floats and will be converted later.
values                ~ array of function values at those time points 
description           ~ string describing the hash rate time series.
maxTime               ~ domain of hashRate time function is [0.0, maxTime]
																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																										
__Functions:
describe(text)        ~ Attach string description
getNextHashEvent(t)   ~ Return time point of next change in hash level (least element 
                        of array time greater than t)
getCurrentHashRate(t) ~ Return hash rate/function value at time t

getOrderedPairs       ~ returns [[t_0, h_0], [t_1, h_1], ...]

"""

import os
import math


class hashRate:
    def __init__(self, time, values, description, maxTime):
        """ Typical __init__ function. First verify that `time' and `values' are 
        nonempty and of the same dimension. Then, pad them on either end with the
        required prefix [t,h] = [0,1] and the required appendix [maxTime,1]."""
        self.maxTime = float(maxTime) # Always good to go.

        self.logFileName = "logs/hashRateLog.log"
        temp = open(self.logFileName, "w")
        temp.close()
        self.printToLog("Beginning new hash rate construction log.")

        # Quick check to make sure `time' and `values' are nonempty and same dimension.
        l = len(time);
        s = len(values);
        m = min(l,s);
        if(m <= 0):
            self.printToLog("Warning in (hashRate __init__): Empty time series data. Problematic, yo. Inventing a dumb hashRate.")
            #print("Empty time series data. Problematic, yo. Inventing a dumb hashRate.")
            time = [0.0,356.1,720.6]
            values =[1,720,76000]
        elif(l != s): 
            self.printToLog("Error in (hashRate __init__):Dimension mismatch. using only the timepoints available.")
            #print("Dimension mismatch. using only the timepoints available.")
            time = time[:m]
            values = values[:m]
        # Now we know `time' and `values' are nonempty and the correct dimension.

        orderedTime = sorted(time)
        if(time != orderedTime):
            self.printToLog("Warning in (hashRate __init__):Proposed timepoints for constructing hashrate are out of order. Re-ordering.")
            time = orderedTime     

        # Padding the hash rate function on either endpoint to be properly formatted, if necessary.
        if(time[0]!=0.0):
            #print("Since first timepoint is not provided, we are assuming H(t)=1 until the first provided timepoint.")
            self.printToLog("Warning in (hashRate __init__): Since first timepoint is not provided, we are assuming H(t)=1 until the first provided timepoint.")
            time.insert(0,0.0)
            values.insert(0,1)
            m=m+1
        if(time[-1]>=self.maxTime):
            self.printToLog("Warning in (hashRate __init__): Support of proposed hashrate exceeds [0, maxTime].")
            #print("Warning in (hashRate __init__): Final timepoint outside of [0, maxTime], so no further padding is necessary (although this is a bit worrying.")
        elif(time[-1]< self.maxTime):
            self.printToLog("Warning in (hashrate __init__): Appending [maxTime+1, lastHashRate] to the hashRate for bookkeeping reasons.")
            #print("Appending [maxTime+1, lastHashRate] to the hashRate for bookkeeping reasons.")
            timeToAppend = self.maxTime + 1.0
            time.append(timeToAppend)
            v = values[-1]
            values.append(v)

        if(not description): # empty strings are ``false''
            description = "This time series lacks a description."

        self.time = time
        self.values = values
        self.description = description

###########################################################

    def printToLog(self, text):
        self.logFile = open(self.logFileName, "a")
        if(not self.logFile):
            print("Error in (hashRate __printToLog__): Log file is an empty object!")
        else:
            self.logFile.write(text + "\n")
        self.logFile.close()
    
###########################################################

    def describe(self, text):
        """ Attach string description to object."""
        if(not text):
            self.printToLog("Warning in (hashRate __init__):Tried to change description to empty string. Changing description to default.")
            text = "This time series lacks a description."
        self.description = text

###########################################################

    def getNextHashEventTime(self, t):
        """ Given a time t, we return the timePoint of the next hashRate change. """
        result = -1.0

        # Quick error catching issue! Verify time query is valid.
        if(t>=self.maxTime or t < 0.0): 
            # Return maxTime if input t is too large
            self.printToLog("Warning in (hashRate getNextHashEventTime): querying hash event time for occurrences outside support [0, maxTime]. Returning the endpoint of this interval that is nearest to the user's query time. In particular, user wanted to know first changepoint in hash rate after time " + str(t) + " but our support is [0, " + str(self.maxTime) + "].")
            if(t < 0.0): result = 0.0
            else: result = self.maxTime
        else:
            # Otherwise, input t lies in one of the partition intervals! Find the nearest subinterval endpoint greater than query time
            for i in range(len(self.time)-1):
                if self.time[i] <= t and t < self.time[i+1]:
                    result = self.time[i+1]

        if(result == -1.0):
            # Error catching...
            # Worst case, we should have 0 <= result <= maxTime so we should never enter this `if'
            if(self.time[0] <=t and t < self.time[-1]):
                self.printToLog("Error in (hashRate getNextHashEventTime): no time index returned, although t is definitely in our domain.")
                #print("Error in (hashRate getNextHashEventTime): no time index returned, although t is definitely in our domain.")
            else:
                self.printToLog("Error in (hashRate getNextHashEventTime): It appears as if t is not in our time domain. Here is t: " + str(t) + " and here is self.time[0]: " + str(self.time[0]) + " and here is self.time[-1]: " + str(self.time[-1]))
                #print("Error in (hashRate getNextHashEventTime): It appears as if t is not in our time domain. Here is t: " + str(t) + " and here is self.time[0]: " + str(self.time[0]) + " and here is self.time[-1]: " + str(self.time[-1]))

        return result

###########################################################

    def getCurrentHashRate(self, t):
        """ Given an input t, return the hashrate at that timepoint.  """
        result = -1
        t = int(math.ceil(t))

        # Quick error catching issue! Verify time query is valid.
        if(t >= self.maxTime or t < 0): 
            self.printToLog("Error in (hashRate getCurrentHashRate): querying hash rate for occurrences outside support [0, maxTime]. Returning the hash rate value at the endpoint of this interval that is nearest to the user's query time. In particular,user wanted to know hashrate at time " + str(t) + " but our support is [0, " + str(self.maxTime) + "].")

            #print("Error in (hashRate getCurrentHashRate): querying hash rate at timepoint beyond simulation time. For convenience, returning hashrate of 1.")
            if(t < 0): 
                result = 1
            else:
                result = self.values[-1]
        else:
            for i in range(len(self.time)-1):
                if self.time[i] <= t and t < self.time[i+1]:
                    result = self.values[i]

        if(result == -1):
            # Error catching...
            # We should never have result = -1, just like in getNextHashEventTime
            if(self.time[0] <=t and t < self.time[-1]):
                self.printToLog("Error in (hashRate getCurrentHashRate): no time index returned, although t is definitely in our domain.")
                #print("Error in (hashRate getCurrentHashRate): no time index returned, although t is definitely in our domain.")
            else:
                self.printToLog("Error in (hashRate getCurrentHashRate): It appears as if t is not in our time domain. Here is t: " + str(t) + " and here is self.time[0]: " + str(self.time[0]) + " and here is self.time[-1]: " + str(self.time[-1]))
                
                #print("Error in (hashRate getCurrentHashRate): It appears as if t is not in our time domain. Here is t: " + str(t) + " and here is self.time[0]: " + str(self.time[0]) + " and here is self.time[-1]: " + str(self.time[-1]))

        return result
