'''
calculations
'''

import numpy
from math import isclose
from random import randrange

'''
PROBABILITY DISTRIBUTIONS
'''

def randomBinomial(bias, size):
	'''
	binomial distribution - a peak around the bias
	returns a list of size 'size'
	'''
	return list(numpy.random.binomial(n = 1, p = bias, size = size))

#sd = 0.05 # standard deviation

'''
def randomTruncNormal(minimum, maximum, bias, size):
	# UNUSED
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
		).tolist()'''
	
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
	# deprecated in favor of randomTruncNormal (now also unused)
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
	# presumably there's a prebuilt function for faster iterating a long list
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