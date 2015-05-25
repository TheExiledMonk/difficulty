from Constants import *
import os
import math
import errno

""" 
Continuous-time function, piecewise constant on some partition of an interval of the form [a,b).

To partition interval [a,b) into n subintervals, we use something like
a = time[0] < time[1] < ... < time[n-1] < time[n] = b
and so we require n+1 floats.

To determine the function value on each of n subintervals, we only need n floats.
When t < time[0], function value will be ONE. We assume at least 1 h/s is always happening.
When time[0] <= t < time[1], function value will be values[0]
When time[i] <= t < time[i+1], 0 <= i < n, function values will be values[i]
When time[n] <= t, function value will be ONE.

This class will return the index of the interval t lies within.
It will also either endpoint of the interval it lies within.
It will also return the function value of the interval it lies within.
"""

class hashRate:

    ## Class attributes ##
    ## The class itself will return these values if called, i.e. hashRate.time returns [0.0] etc.
    ## These also cause the default values of specific instances of this class.

    time = TIME_EXAMPLE # N+1
    values = VALUES_EXAMPLE   # N
    description = DESC_EXAMPLE # Simple alphanum, no space description
    maxTime = MAX_RUN_TIME
    logFileName = HASHRATE_LOGFILE

    def __init__(self, params=None):
        # time, values, description, maxTime

        paramsAreEmptyObject = not params # True if params is empty
        paramsAreNone = (params==None)    # True if params==None, when params ahven't been passed in at all.
        paramsPassedIn = not(paramsAreEmptyObject or paramsAreNone) # True if something nonempty was passed

        if(paramsPassedIn):
            ## User-defined instance attributes ##
            #print("Here are the parameters used to initialize hashrate. params = " + str(params))
            self.time = params[0]
            self.values = params[1]
            self.description = params[2]
            self.maxTime = params[3]

        isDescStr = isinstance(self.description,str)
        self.make_sure_path_exists("logs")
        if(isDescStr):
            self.logFileName = "logs/hashRate" + self.description + str(self.maxTime) + "Log.log"
        else:
            self.logFileName = "logs/hashRate" + str(self.description) + str(self.maxTime) + "Log.log"
        self.logFile = open(self.logFileName,"w") # Clear the log file 
        self.logFile.close() # Clear the log file

        if(not isDescStr):
            self.printToLog("Error in (blockChain __init__): Description of hash rate function not string.")

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

    def getIndexRightEndpoint(self, t=None):
        """ Return index of first entry in self.time that is greater than t or False if none exist. """ 
        resultIndex = False
        if(t==None):
            self.printToLog("Error in (hashRate getIndexRightEndpoint): Can't find right endpoint for time t=None. Silly.")
        elif(t < self.time[-1]):
            # Note that if t >= self.time[-1], there is no righthand endpoint, so we return false.
            # Inside this case, we are guaranteed a righthand endpoint.
            resultIndex = 0
            while(self.time[resultIndex] <= t):
                 resultIndex = resultIndex + 1
        return resultIndex
    
    ###########################################################

    def getNextChangePoint(self, t=None):
        """ Return time stamp of first entry in self.time that is greater than t or False if none exist. """ 
        result = False
        if(t==None):
            self.printToLog("Error in (hashRate getIndexRightEndpoint): Can't find right endpoint for time t=None. Silly.")
        elif(t < self.time[-1]):
            # Note that if t >= self.time[-1], there is no righthand endpoint, so we return false.
            # Inside this case, we are guaranteed a righthand endpoint.
            nextChangePointIndex = self.getIndexRightEndpoint(t)
            result = self.time[nextChangePointIndex]
#        else:
#            print("Time has exceeded support, so hash rate should be 1. But we have no more hcangepoints. In fact, time = " + str(t) + " and our last timepoint was " + str(self.time[-1]))
        return result
    
    ###########################################################

    def getIndexLeftEndpoint(self, t=None):
        """ Return index of last entry in self.time that is less than or equal to t, or False if none exist. """ 
        resultIndex = False
        if(t==None):
            self.printToLog("Error in (hashRate getIndexLeftEndpoint): Can't find left endpoint for time t=None. Silly.")
        elif(t >= self.time[0]):
            # Note that if t < self.time[0], there is no lefthand endpoint, so we return false.
            # Inside this case, we are guaranteed a righthand endpoint.
            resultIndex = 0
            weCanStop = False
            while(resultIndex < len(self.time) and not weCanStop):
                if(self.time[resultIndex] <= t):
                    resultIndex = resultIndex + 1
                else:
                    weCanStop = True
                    resultIndex = resultIndex - 1
        return resultIndex
    
    ###########################################################

    def getFunctionValue(self, t=None):
        """ Return hash function value at time t, or false if not possible for some reason. """
        resultValue = False
        if(t==None):
            self.printToLog("Error in (hashRate getFunctionValue): Can't find function value for time t=None. Silly.")
        elif(not isinstance(t,float)):
            self.printToLog("Error in (hashRate getFunctionValue): Can't fund function value at non-float time t = " + str(t))
        elif(t< 0.0 or t >= self.maxTime):
            resultValue = 1.0
            self.printToLog("Error in (hashRate getFunctionValue): Tried to get hashrate outside of [0, maxTime] at time t = " + str(t))
        else:
            resultIndex = 0
            resultValue = 1.0
            weCanStop = False
            while(resultIndex < len(self.values) and not weCanStop):
                if(self.time[resultIndex] <= t and self.time[resultIndex+1] > t):
                     resultValue = self.values[resultIndex]
                     weCanStop = True
                else:
                     resultIndex = resultIndex + 1
            if( not weCanStop):
                self.printToLog("Error in (hashRate getFunctionValue): time t is within [0, maxTime], but no hashrate function value was returned.")
        return resultValue
