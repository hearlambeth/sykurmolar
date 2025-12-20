'''
triggers that force a response from sykurmolar

every class has to have:
	self.outputTrigger = pyo.Trig() object
	self.name (with a default)
'''
# local
import constants
from mafs import incbind, iterate, randomBinomial
# external
import pyo64 as pyo
from random import sample
from numpy.random import uniform

class No():

	def __init__(self, name='nei'):
		self.outputTrigger = pyo.Trig() # it'll never work
		self.name = name

class Manual():

	def __init__(self, name='manual'):
		self.outputTrigger = pyo.Trig() # call .play() to play
		self.name = name

class SimpleLoop():

	def __init__(self, duration, name='simple'):
		self.duration = duration
		self.outputTrigger = pyo.Metro(time = self.duration).play()
		self.latestTapTempo = 0 # in samples
		self.name = name

	def updateDuration(self, new):
		new = round(new, 5)
		self.duration = new
		self.outputTrigger.setTime(new)
		self.resetTriggerNow()

	def resetTriggerNow(self):
		self.outputTrigger.stop()
		self.outputTrigger.play()
	
	def incrementDuration(self, amount):
		newDur = self.duration
		if amount < 0:
			if self.duration/constants.SIMPLELOOP_DURATION_MULTIPLIER >= constants.TINY_DUR_SECONDS:
				newDur = self.duration/constants.SIMPLELOOP_DURATION_MULTIPLIER
		elif amount > 0:
			if self.duration*constants.SIMPLELOOP_DURATION_MULTIPLIER <= constants.SIMPLELOOP_DURATION_MAX_SECONDS:
				newDur = self.duration*constants.SIMPLELOOP_DURATION_MULTIPLIER
		self.updateDuration(newDur)

	def tapTempo(self, newTime):
		if newTime - self.latestTapTempo <= constants.SIMPLELOOP_DURATION_MAX_SAMPLES:
			self.updateDuration((newTime - self.latestTapTempo) / constants.SAMPLE_RATE)
		self.latestTapTempo = newTime

class SwungRhythm():
	'''
	swung trigger, but as looped rhythm
	rhythm is central: same rhythm can be maintained even when swing and duration change, therefore:
		duration change creates an overall tempo shift
		swing change creates a kind of warping

	rhythm = list of values from 0 to 1 that determines the rhythm. long enough for max beats.
		recalced using new rhythm button
	incrementing swing changes the swing amount alone
	incrementing beatCount changes window of rhythm to iterate through
	receiving duration updates duration
	'''

	def __init__(self, trigger, duration, name='rhythm'):
		self.inputTrigger = trigger
		self.outputTrigger = pyo.Trig()
		self.i = 0 # index for moving through the swing delay amounts
		self.duration = duration
		self.swing = constants.SWING_MIN
		self.beatCount = 1
		self.rhythm = []
		self.newRhythm()
		self.delays = []
		self.updateDelays()
		# create response to an input trigger
		self.responder = pyo.TrigFunc(self.inputTrigger, self.delayTriggerPlay)
		self.name = name

	def delayTriggerPlay(self):
		# receiving a trigger,
		# iterate to next index (do this first in case in the index became out of bounds)
		self.i = iterate(self.i, self.beatCount - 1)
		# play the output trigger after duration
		self.delayedResponse = pyo.CallAfter(self.outputTrigger.play, time = self.delays[self.i])
		

	def newRhythm(self):
		# generate fresh rhythm
		self.rhythm = uniform(0, 1, constants.SWING_RHYTHM_MAX_BEATS)
		self.updateDelays()

	def incrementSwing(self, amount):
		# receives a value of -1 or 1 from knob
		if amount == 1:
			self.swing = incbind(self.swing, constants.SWING_INCREMENT, constants.SWING_MIN, constants.SWING_MAX)
		elif amount == -1:
			self.swing = incbind(self.swing, 0 - constants.SWING_INCREMENT, constants.SWING_MIN, constants.SWING_MAX)
		# then update delays
		self.updateDelays()

	def incrementBeatCount(self, amount):
		# receives a value of -1 or 1 from knob
		self.beatCount = incbind(self.beats, amount, 1, constants.SWING_RHYTHM_MAX_BEATS)
		self.updateDelays()

	def updateDuration(self, new):
		# receive new duration, store it, update delays
		self.duration = new
		self.updateDelays()

	def updateDelays(self):
		# recalculate list of delay durations based on rhythm * swing * duration
		self.delays = [j * self.swing * self.duration for j in self.rhythm[:self.beatCount-1]]


class Swung():
	'''
	TEST ME
	swung trigger
	takes another trigger as input, produces another trigger with a randomized delay on each
	'''

	def __init__(self, trigger, duration, name='swung'):
		self.inputTrigger = trigger
		self.outputTrigger = pyo.Trig()
		self.i = 0 # index for moving through the swing delay amounts
		self.swing = constants.SWING_MIN
		self.duration = duration
		self.delays = []
		self.updateDelays()
		# create response to an input trigger
		self.responder = pyo.TrigFunc(self.inputTrigger, self.delayTriggerPlay)
		self.name = name

	def delayTriggerPlay(self):
		# receiving a trigger,
		# play the output trigger after duration
		self.delayedResponse = pyo.CallAfter(self.outputTrigger.play, time = self.delays[self.i])
		# iterate to next index
		self.i = iterate(self.i, constants.VARIABLES_LIST_LENGTH - 1)

	def incrementSwing(self, amount):
		# receives a value of -1 or 1 from knob
		if amount == 1:
			self.swing = incbind(self.swing, constants.SWING_INCREMENT, constants.SWING_MIN, constants.SWING_MAX)
		elif amount == -1:
			self.swing = incbind(self.swing, 0 - constants.SWING_INCREMENT, constants.SWING_MIN, constants.SWING_MAX)
		# then update delays
		self.updateDelays()

	def updateDuration(self, new):
		# receive new duration, store it, update delays
		self.duration = new
		self.updateDelays()

	def updateDelays(self):
		# recalculate list of delay durations based on swing and duration
		self.delays = uniform(0, self.swing * self.duration, constants.VARIABLES_LIST_LENGTH).tolist()


class Random():
	# basic random trigger

	def __init__(self, density, name='snigill'):
		self.outputTrigger = pyo.Cloud(density = density).play()
		self.name = name

class TappedRhythm():
	'''
	records and loops a tapped rhythm
	'''
	pass


	
class Combine():
	'''
	REDO as a complex rhythm generator in some form
		knob increases number of beats
		based on swung, but looping
	THIS DOESN'T WORK and is probably not useful
	combines a list of triggers to a single output trigger
	knob control over number to combine from the list - each new addition makes a random set of them
	receives the outputTriggers as triggersList
	in my application in Ammæli below, this is something of a prime phased rhythm generator
	'''
	def __init__(self, triggersList, name='combine'):
		self.triggersList = triggersList
		self.maxLength = len(self.triggersList)
		self.currentLength = 2
		# i don't think this is working - seems to only be one of the triggers, not all
		self.outputTrigger = pyo.Percent([self.triggersList[0], self.triggersList[1]], 100)
		self.name = name

	def changeOutputTrigger(self):
		self.outputTrigger.setInput([self.triggersList[i-1] for i in sample(range(1, self.maxLength), self.currentLength)])

	def incrementLength(self, amount):
		if amount < 0:
			self.currentLength = incbind(self.currentLength, -1, 1, self.maxLength)
		elif amount > 0:
			self.currentLength = incbind(self.currentLength, 1, 1, self.maxLength)
		# after incrementing length, always changeOutputTrigger
		self.changeOutputTrigger()
		
		
class Ammæli():
	'''
	a few triggers based on a SimpleLoop's duration
	outputTrigger buttons function as a shift. knob edits.
		SimpleLoop: incrementDuration
		Swung: incrementSwing
		Combine: incrementLength
	'''

	def __init__(self, duration, sampleCounter, name='ammæli'):
		self.name = name
		self.duration = duration
		self.sampleCounter = sampleCounter
		self.t_SimpleLoop = SimpleLoop(self.duration, name=self.name+'_simple')
		self.t_Swung = Swung(self.t_SimpleLoop.outputTrigger, self.duration, name=self.name+'_swung')
		self.t_SwungRhythm = None
		self.t_PrimesLong = [SimpleLoop(x, name=self.name+'_priime') for x in self.calcDividedDurations(constants.PRIIMES)]
		self.t_PrimesShort = [SimpleLoop(x, name=self.name+'_prime') for x in self.calcDividedDurations(constants.PRIMES)]
		self.t_Combine = Combine([t.outputTrigger for t in self.t_PrimesLong])
		


	def display(self, value):
		print(value)
		
	def calcDividedDurations(self, dividers):
		return [round(self.duration/x, 5) for x in dividers]
	
	def updateDurations(self):
		# check we got a new duration in our update of SimpleLoop, then apply it to all
		if self.t_SimpleLoop.duration != self.duration:
			self.duration = self.t_SimpleLoop.duration
			# apply to t_Primes
			newPrimesLongDurations = self.calcDividedDurations(constants.PRIIMES)
			newPrimesShortDurations = self.calcDividedDurations(constants.PRIMES)
			for i in range(len(newPrimesLongDurations)):
				self.t_PrimesLong[i].updateDuration(newPrimesLongDurations[i])
			for i in range(len(newPrimesShortDurations)):
				self.t_PrimesShort[i].updateDuration(newPrimesShortDurations[i])
			# apply to t_Swung
			self.t_Swung.updateDuration(self.duration)
	
	# centrally updating values - otherwise calling functions with getattr might not work

	def tapTempo(self):
		self.t_SimpleLoop.tapTempo(self.sampleCounter.get())
		self.updateDurations()

	def incrementDuration(self, amount):
		self.t_SimpleLoop.incrementDuration(amount)
		self.updateDurations()
		self.display(self.duration)

	def incrementSwing(self, amount):
		self.t_Swung.incrementSwing(amount)
		self.display(self.t_Swung.swing)

	def incrementSwungRhythmBeats(self, amount):
		pass

	def incrementCombineLength(self, amount):
		self.t_Combine.incrementLength(amount)