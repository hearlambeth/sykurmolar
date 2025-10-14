'''import sys

sequencesFile = str(sys.path[0] + '/sequences')
sequences = []

with open(sequencesFile, 'r') as sf:
    lines = sf.readlines()
    for line in lines:
        line = line.split(',')
        # make each an int - map to int, then make tuple
        line = tuple(map(int, line))
        sequences.append(line)



print(sequences)'''
'''
a = [0,1,2,3,4]
v = 2
reverse = a[:v]
reverse.reverse()
a = reverse + a[v:]
print(a)'''
'''
import mafs
from timeit import timeit

def oneLongList():
	mafs.randomBinomial(0.5, 500)

def oneLongerList():
	mafs.randomBinomial(0.5, 1000)

def severalShorterLists():
	[mafs.randomBinomial(0.5, 500) for i in range(10)]

def severalShorterLists2():
	[mafs.randomBinomial(0.5, 1000) for i in range(10)]

def triangular():
	[mafs.randomTriangular(0, 0.33, 0.5, 1000) for i in range(10)]

def binomial():
	[mafs.randomBinomial(0.5, 1000) for i in range(10)]


#print(timeit(triangular, number=1))
print(timeit(binomial, number=1))'''


import mafs
'''
a = [0,1,2,3,4]
mafs.shuffleSlice(a, 1, 4)
print(a)
mafs.shuffleSlice(a, 1, 4)
print(a)'''
'''
#y = mafs.randomBeta(1, 5, 0, 100)

a = mafs.MMSM(0, 10)
a.changeMinimum(20)'''


'''
def newMinimum(amount, minimum, maximum, minimumLimit, maximumLimit):
	return incbind(minimum, amount, minimumLimit, min(maximum, maximumLimit))

def newMaximum(amount, minimum, maximum, minimumLimit, maximumLimit):
	return incbind(maximum, amount, max(minimum, minimumLimit), maximumLimit)

def newSpread(amount, minimum, maximum, minimumLimit, maximumLimit):
	return newMinimum(-amount, minimum, maximum, minimumLimit, maximumLimit), newMaximum(amount, minimum, maximum, minimumLimit, maximumLimit)

def newMiddle(amount, minimum, maximum, minimumLimit, maximumLimit):
	return newMinimum(amount, minimum, maximum, minimumLimit, maximumLimit), newMaximum(amount, minimum, maximum, minimumLimit, maximumLimit)
'''

# test: integers
'''
AMOUNT = 1
MINIMUM = 5
MAXIMUM = 5
MINIMUMLIMIT = -12
MAXIMUMLIMIT = 12'''


# test: float
'''
AMOUNT = -0.05
MINIMUM = 0.7
MAXIMUM = 0.7
MINIMUMLIMIT = 0
MAXIMUMLIMIT = 1

for i in range(20):
	print(MINIMUM, MAXIMUM)
	MINIMUM, MAXIMUM = mafs.newFromSpread(AMOUNT, MINIMUM, MAXIMUM, MINIMUMLIMIT, MAXIMUMLIMIT)

AMOUNT = 0.05

for i in range(20):
	print(MINIMUM, MAXIMUM)
	MINIMUM, MAXIMUM = mafs.newFromSpread(AMOUNT, MINIMUM, MAXIMUM, MINIMUMLIMIT, MAXIMUMLIMIT)

	'''

a = mafs.randomBeta(0, 1, 0.5, 20)
print(a)
print(a[0])
print(type(a[0]))