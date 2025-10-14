import numpy
from scipy.stats import truncnorm
from math import ceil, isclose
from random import randrange
from sympy import prevprime

'''
PROBABILITY DISTRIBUTIONS
'''

def randomBinomial(bias, size):
	# binomial distribution - a peak around the bias
	# returns a list of size 'size'
	return list(numpy.random.binomial(n = 1, p = bias, size = size))

#sd = 0.05 # standard deviation

def randomTruncNormal(minimum, maximum, bias, size):
	# truncated normal distribution between minimum and maximum
	# to increase the sharpness of the peak/decrease the range, reduce sd
	# from here: https://stackoverflow.com/questions/18441779/how-to-specify-upper-and-lower-limits-when-using-numpy-random-normal
	truncrange = maximum - minimum
	# if there is no difference between min and max, just provide this
	if truncrange == 0:
		return [minimum for i in range(size)]
	else:
		# set bias between max and min
		bias = (truncrange) * bias + minimum
		# scale standard deviation for range
		sd = 0.05 * truncrange
		# create distribution
		return truncnorm.rvs(
			(minimum-bias)/sd, (maximum-bias)/sd, loc=bias, scale=sd, size=size
		).tolist()
	
def randomBeta(minimum, maximum, bias, size):
	'''
	returns beta probability distribution scaled between maximum and minimum
	bias gets scaled between 1,5, 1,1 and 5,1
	this produces an exponential curve at the limits and a uniform distribution at 0.5
	increasing the multiplier to bias (from 8) would increase the peak of the exponential curve
	'''
	# transform bias into a range from -4 to +4
	bias = 0.5 - bias
	bias *= 8
	# use our bias to assign alpha and beta
	if bias == 0:
		a, b = 1, 1
	elif bias < 0:
		a, b = 1 + abs(bias), 1
	elif bias > 0:
		a, b = 1, 1 + bias
	# calc beta distribution between 0 and 1
	beta = numpy.random.beta(a, b, size).tolist()
	# scale it all between minimum and maximum
	betaRange = maximum - minimum
	return [(i * betaRange) + minimum for i in beta]

	
	

def randomTriangular(minimum, maximum, bias, size):
	# deprecated in favor of randomTruncNormal
	# ! consider replacing with arcsine - from scipy.stats import arcsine 
	# triangular distribution
	# but: if minimum is maximum, picks this number; if bias is at extremes, picks extreme
	# mode places bias between minimum and maximum
	# returns a list of size 'size'
	if minimum == maximum:
		return [maximum for i in range(size)]
	elif bias == 1:
		return [maximum for i in range(size)]
	elif bias == 0:
		return [minimum for i in range(size)]
	else:
		mode = ((maximum - minimum) * bias) + minimum
		triangular = numpy.random.triangular(minimum, mode, maximum, size = size)
		triangular = list(triangular)
		triangular = [float(i) for i in triangular]
		return triangular

		

'''
HANDLING NUMBERS IN MINIMUM, MAXIMUM, BOUND SITUATIONS
'''

def incbind(number, amount, minimum, maximum):
	# increment and bind
	# returns number + amount (incl. negative amount), bound between minimum and maximum
	# provides it as a nice, rounded number
	# MAXMINMINMAXMAXMINMINMAXAXA
	new = max(minimum, min(maximum, number + amount))
	if type(new) == int:
		return new
	elif type(new) == float:
		return round(new, 5)
	#previously just did: return max(minimum, min(maximum, number + amount))

def newMinimum(amount, minimum, maximum, minimumLimit, maximumLimit):
	return incbind(minimum, amount, minimumLimit, min(maximum, maximumLimit))

def newMaximum(amount, minimum, maximum, minimumLimit, maximumLimit):
	return incbind(maximum, amount, max(minimum, minimumLimit), maximumLimit)

def newFromSpread(amount, minimum, maximum, minimumLimit, maximumLimit):
	# returns a minimum and maximum from an adjusted spread
	# spread in one direction is allowed to expand even if other direction hits limit
	trialMinimum = newMinimum(-amount, minimum, maximum, minimumLimit, maximumLimit)
	trialMaximum = newMaximum(amount, minimum, maximum, minimumLimit, maximumLimit)
	if trialMaximum > trialMinimum or isclose(trialMinimum, trialMaximum):
		return trialMinimum, trialMaximum
	else:
		return minimum, maximum

def newFromMiddle(amount, minimum, maximum, minimumLimit, maximumLimit):
	# returns a minimum and maximum from an adjusted middle
	# this maintains spread, i.e. if spread would shrink, both minimum and maximum are unaffected
	# nudge minimum and maximum with amount
	trialMinimum = incbind(minimum, amount, minimumLimit, maximumLimit)
	trialMaximum = incbind(maximum, amount, minimumLimit, maximumLimit)
	spread = maximum - minimum
	if isclose(trialMaximum - trialMinimum, spread):
		# if spread stays the same (or extremely close, as these can be floats), return the new result
		return trialMinimum, trialMaximum
	else:
		# if the spread would shrink, return what was passed
		return minimum, maximum


def iterate(currentIndex, maxIndex):
	# find out if there's a prebuilt function for faster iterating a long list
	currentIndex += 1
	if currentIndex > maxIndex:
		currentIndex = 0
	return currentIndex

def generateIndicesList(startIndex, maxIndex, length):
	# returns a list of length length, beginning with startIndex,
	# and running past maxIndex if necessary
	index = startIndex
	indices = []
	while length > 0:
		indices.append(index)
		length -= 1
		index += 1
		if index > maxIndex:
			index = 0
	return indices


class iterator():
	# literally making this so i don't have to define my max point each time
	def __init__(self, maxIndex):
		self.maxIndex = maxIndex
	def i(self, currentIndex):
		currentIndex += 1
		if currentIndex > self.maxIndex:
			currentIndex = 0
		return currentIndex

def shuffleSlice(liszt, start, end):
	# a Knuth shuffle adapted from https://stackoverflow.com/questions/9557182/python-shuffle-only-some-elements-of-a-list
    i = start
    while (i < end - 1):
        idx = randrange(i, end)
        liszt[i], liszt[idx] = liszt[idx], liszt[i]
        i += 1

def newRate(macro, micro):
	return 2**((macro + micro)/12)

def newVolume(volume, audible):
	if not audible:
		return 0
	else:
		return volume

def sign(number):
	if number < 0:
		return '-'
	else:
		return '+'
		
'''

MIDI
airport project. incomplete. not sure if this is legible 
as a display mechanism.

FLOATTOFIVE
displays a float from 0-1 as lights along 5 LEDs
first list shows all the LED values
'''

floatFiveOrig = [
	[3,0,0,0,0],
	[3,1,0,0,0],
	[3,2,0,0,0],
	[2,2,0,0,0],
	[2,3,0,0,0],
	[1,3,0,0,0],
	[0,3,0,0,0],
	[0,3,1,0,0],
	[0,3,2,0,0],
	[0,2,2,0,0],
	[0,2,3,0,0],
	[0,1,3,0,0],
	[0,0,3,0,0],
	[0,0,3,1,0],
	[0,0,3,2,0],
	[0,0,2,2,0],
	[0,0,2,3,0],
	[0,0,1,3,0],
	[0,0,0,3,0],
	[0,0,0,3,1],
	[0,0,0,3,2],
	[0,0,0,2,2],
	[0,0,0,2,3],
	[0,0,0,1,3],
	[0,0,0,0,3],
]

# modify floatFive to a precreated dictionary from 0.00 to 1.00
# this is a bit clunky - hard to make both 0 and 1 to work in a simple equation

floatFiveLookup = dict()

def _floatToFivePreprocess():
	global floatFiveLookup
	all2dp = [float('{:.2f}'.format(i/100)) for i in range(100)]
	for x in all2dp:
		new = (x/1) * (len(floatFiveOrig) - 1)
		new = ceil(new)
		new = min(new, len(floatFiveOrig) - 2)
		floatFiveLookup.update({x:floatFiveOrig[new]})
	floatFiveLookup.update({1.00: floatFiveOrig[-1]})

_floatToFivePreprocess()

# precalculations for floatToFive

def floatToFive(f):
	if f < 0 or f > 1:
		return ValueError('error: floatToFive takes 0 to 1 only')
	f2dp = float('{:.2f}'.format(f))
	return f2dp, floatFiveLookup.get(f2dp)

'''
INTTOFIVEBINARY
displays an integer (-31 to 31) as least significant first signed binary
returns a list of six integers: sign (3 or 4), 5 bits (least significant first, using 1 or 2)
'''

intToFiveBinaryLookup = dict()

def _intToFiveBinaryPreprocess():
	global intToFiveBinaryLookup
	for i in range(-31, 32):
		# determine sign
		if i < 0:
			sign = 3
		else:
			sign = 4
		# absolute of binary, knock off first two characters, e.g.: 0b0 -> 0
		binary = str(bin(abs(i)))[2:]
		# pad to 5 characters
		binary = binary.zfill(5)
		# make it a list and add 1 to each character
		binary = [int(c) + 1 for c in binary]
		# reverse character order
		binary.reverse()
		# add the sign to the beginning
		binary.insert(0, sign)
		intToFiveBinaryLookup.update({i:binary})

_intToFiveBinaryPreprocess()

def intToFiveBinary(i):
	if abs(i) > 31:
		return ValueError('error: intToFiveBinary takes -31 to 31 only')
	return i, intToFiveBinaryLookup.get(i)


'''
INTTOFIVEDECIMAL
displays an integer (-15 to 15) using 3 colors and blank as groups of 5, with sign
returns a list of six integers: six (4 or 5), 5 bits (using 0-3)
'''

intToFiveDecimal1Lookup = dict()

def _intToFiveDecimal1Preprocess():
	global intToFiveDecimal1Lookup
	for i in range(-15, 16):
		# determine sign
		if i < 0:
			sign = 4
		else:
			sign = 5
		# make it using base and remainder
		j = abs(i)
		base = int(j / 5)
		baseRemainder = j % 5
		result = [base for x in range(5)]
		for k in range(baseRemainder):
			result[k] += 1
		# add sign
		result.insert(0, sign)
		intToFiveDecimal1Lookup.update({i:result})

_intToFiveDecimal1Preprocess()

#print(intToFiveDecimal1Lookup)

def intToFiveDecimal1(i):
	if abs(i) > 15:
		return ValueError('error: intToFiveDecimal1 takes -15 to 15 only')
	return i, intToFiveDecimal1Lookup.get(i)

'''
INTTOFIVEDECIMAL2
displays an integer (-99 to 99) using 3 colors as groups of five, with a sign, and an additional light to show additions of 10
0-9 uses: 0-2
additions of ten (1-9): 3-5, 6-8, 9-11
sign: 12, 13
'''

''' incomplete
intToFiveDecimal2Lookup = {
    0: [0,0,0,0,0],
    1: [1,0,0,0,0],
    2: [1,1,0,0,0],
    3: [1,1,1,0,0],
    4: [1,1,1,1,0],
    5: [1,1,1,1,1],
    6: [2,1,1,1,1],
    7: [2,2,1,1,1],
    8: [2,2,2,1,1],
    9: [2,2,2,2,1],
    10: [2,2,2,2,2],
    11: [3,2,2,2,2]
}

intToFiveDecimal2Lookup = dict()

def _intToFiveDecimal2Preprocess():
    global intToFiveDecimal2Lookup
    for i in range(-99, 100):
        # determine sign
        if i < 0:
            sign = 12
        else:
            sign = 13
        j = abs(i)
        # determine tens
        tens = int(j / 10)
        base5 = 


def intToFiveDecimal2(i):
	if abs(i) > 30:
		return ValueError('error: intToFiveDecimal2 takes -29 to 29 only')
	# determine sign
	if i < 0:
		sign = 1
	else: 
		sign = 2
	i = abs(i)
	base10 = int(i / 10)
	base10Remainder = i % 10
	base5 = int(base10Remainder / 5)
	base5Remainder = base10Remainder % 5
	#return base10, base10Remainder, base5, base5Remainder
	result = [int((base10+1)*3) for x in range(5)]
	for y in range((len(result))):
		result[y] += base5
	for z in range(base5Remainder):
		result[z] += 1
	# add sign
	result.insert(0, sign)
	return base10, base10Remainder, base5, base5Remainder, result

'''
'''
testing
for i in range(-15,16):
	print(intToFiveDecimal(i))
	sleep(0.2)
for i in range(-31, 32):
	print(intToFive(i))
	sleep(0.2)'''

'''
CALCULATING THE PRIME RANGES OF TRIGGERS' PRIME DIVISIONS
'''

def PrimeDivisionBallparks(maxSeconds, minSeconds, sampleRate, targetSamples):
	# variables
	maxSeconds = maxSeconds
	minSeconds = minSeconds
	sampleRate = sampleRate
	# create dictionary keys which will be 1 to max duration plus min duration
	keyDurations = [i + 1 for i in range(maxSeconds)]
	keyDurations.append(0) # using 0 instead of minSeconds so i can select based on the time rounding down to 0
	keyDurations.sort()
	# low targets we want to hit. for each of these we want to generate a few random prime divisors above it
	targetSamples = targetSamples
	outputDictionary = {}
	# recursive prevprimes to get the next few
	for key in keyDurations:
		value = []
		for i in targetSamples:
			value.append(prevprime(key * sampleRate / i))
			value.append(prevprime(value[-1]))
			value.append(prevprime(value[-1]))
		outputDictionary[key] = value
	return outputDictionary

#print(PrimeDivisionBallparks(10, 0.3, 48000, (100, 500, 2000)))