# difficulty

Testing difficulty algorithms by simulating the Poisson process construction of a blockchain given a hashrate-over-time

The code takes an instance of the `hashRate` object as input, which represents some a priori piecewise constant function in time, and uses an instance of the `simulation` object together with this instance of the `hashRate` object to create a stochastically generated instance of the `blockChain` object, which is then printed to a file.

To run the whole rig, first `compile blockChain.py`, `hashrate.py`, `simulation.py`, and then compile `simulator.py`. Output file will be stored as `data/output.csv` in the form of a sequence of integer timestamps (in seconds) together with difficulty scores (also integer, although they are computed as floats then rounded down in this code). Setting `DIFFICULTY_FORMULA = "bitcoin"` in `Constants.py` will use all bitcoin default parameter values, and setting `DIFFICULTY_FORMULA = "bitmonero"` will use all Monero default parameter values. Otherwise, parameter values will be

`LAMBDA_TARGET   = 1.0/180.0 # Target block arrival rate`

`DIFF_ADJ_PERIOD = 36        # Adjust difficulty every this many blcoks`

`DIFF_SAMPLE_SIZE = 72       # Use this many blocks to compute next difficulty.`

`TIME_SAMPLE_SIZE = 72       # Use this many blocks to compute lower bound on timestamp`

# Controlling hash rate

The hash rate is a partition of the interval `[0, MAX_RUN_TIME]` together with a hashrate value on each subinterval. To change default input instance of `hashRate` object, open Constants.py... the object `TIME_EXAMPLE` represents the partition:

`0.0 = TIME_EXAMPLE[0] < TIME_EXAMPLE[1] < ... < TIME_EXAMPLE[n-1] < TIME_EXAMPLE[n] = MAX_RUN_TIME`

and the object `VALUES_EXAMPLE` represents a sequence of floats representing hash values on the subintervals

`VALUES_EXAMPLE[0], VALUES_EXAMPLE[1], ..., VALUES_EXAMPLE[n-1]`

such that, for any float `clock`, if `TIME_EXAMPLE[i] <= clock` and `clock < TIME_EXAMPLE[i+1]` then the network hashrate is precisely `VALUES_EXAMPLE[i]`. If no such index exists, the network hashrate is assumed to be 1.

The hashRate object will do things like return the hashrate function evaluated at a particular point in time, and will return the next changepoint that occurs after a particular point in time.

# Example

For example, to represent a Monero-style blockchain created from a hash rate that lasts four days such that, for the first day the network hashrate is 10000.0, the second day the network hashrate is 100.0, the third day the network hashrate is 3.14159, and the last day the network hashrate is 1000000.0, then we would open Constants.py and change the following variables to

`DIFFICULTY_FORMULA = "bitmonero"`

`MAX_RUN_TIME = 345600.0 # 4 days in seconds`

`TIME_EXAMPLE = [0.0, 86400.0, 172800.0, 259200.0, MAX_RUN_TIME] # Day by day timepoints`

`VALUES_EXAMPLE = [10000.0, 100.0, 3.14159, 1000000.0] # Hashrates on each day.`

Note that it would be inappropriate to investigate bitcoin with these choices, because difficulty only updates every 2 weeks. 

Executing `hashRate` method `getNextChangePoint(clock)` will return the first hash changepoint event greater than `clock`, so `getNextChangePoint(50.0)` will return 86400.0, and `getNextChangePoint(86400.0)` will return 172800.0. Executing `hashRate` method `getFunctionValue(clock)` will return the network hash rate at time `clock`, so `getFunctionValue(173000.0)` will return 3.14159.

# Example

For another example, to represent a Bitcoin-style blockchain created from a hash rate that lasts 2 years such that, each month, the hashrate doubles from the previous month, starting with an initial hashrate of 1000.0, we would open Constants.py and use

`DIFFICULTY_FORMULA = "bitcoin"`
`MAX_RUN_TIME = 63110000.0 # 2 years in seconds`
`TIME_EXAMPLE = [MAX_RUN_TIME*float(x)/12.0 for x in range(13)] # Timepoints of monthly hashrate change`
`VALUES_EXAMPLE = [1000.0*math.pow(2.0,float(x)) for x in range(12)] # Hashrates on each changepoint`

Executing `hashRate` method `getNextChangePoint(clock)` will return the first hash changepoint event greater than `clock`, so `6.3` months into the simulation, `getNextChangePoint(16567400.0)` will return  `18408200.0` (`7` months in seconds). As before, executing `hashRate` method `getFunctionValue(clock)` will return the network hash rate at time `clock`, so `6.3` months into the simulation, `getFunctionValue(16567400.0)` will return `1000.0*(2.0^5.0) = 32000.0`

# How it all works 

The `simulation` object essentially consists of a `clock`, a `blockChain` object, and a `hashRate` object. When `simulation.runSim()` is executed, a Poisson process using the `hashRate` object is used to determine a stochastically generated `blockChain` object. Blocks arrive at a rate `hash rate value`/`difficulty` (measured in arrivals per second); when `hashRate` changes, this block arrival rate changes, and when a block arrives, difficulty is re-computed and this block arrival rate changes. 

So, for `0.0 <= clock < MAX_RUN_TIME`, we check for which event occurs first: a block arrival or a hashrate change. If a block arrives first, we roll time forward to this block arrival. Otherwise, we roll time forward to the next hash changepoint. Either way, we recompute block arrival rates and repeat until clock exceeds `MAX_RUN_TIME`.

See above for a description of the `hashRate` object, which is used to compute block arrival rate. Notice block arrival rate also requires the current difficulty score (see below).

The `blockChain` object essentially consists of (1) a sequence of ordered pairs `[[T_0, D_0], [T_1, D_1], ...]` representing block timestamps and difficulty scores, and (2) a current difficulty score. Current difficulty score is 1 whenever the current sequence of timestamps is smaller than `DIFF_SAMPLE_SIZE`, and otherwise, current difficulty score is computed from the top `DIFF_SAMPLE_SIZE` elements from the sequence of ordered pairs. However, due to ease of data management and symmetry with the way we stored data in the hashRate object, we store the timestamps `[T_0, T_1, ...]` and the difficulties `[D_0, D_1, ...]` separately; this way, the index of interest is block height.

The `blockChain` object will do things like (1) add a block of a given timestamp, (2) re-compute next difficulty, and (3) write it's sequence of timestamps and difficulties to a file. Notice that it won't add just any old block with any old timestamp; if a timestamp is 2 hours ahead of the highest timestamp, or if it is behind the median of the last `TIME_SAMPLE_SIZE` blocks, then the block is ignored by the network; this is the only event in which both block chain and hash rate remain unchanged despite the fact that time rolls forward

# TODO 

Check issues for better list of todo stuff.

Until we know everything works, the attack policy is not totally implemented. If you push your timestamps ahead by a bit and for now it may look like difficulty should drop, but a little later on it will look like difficulty should increase, so you will have a net zero effect on difficulty in the long run.  Hence, we investigate non-constant manipulations. For example, a sawtooth function added to your timestamps may have an effect.


