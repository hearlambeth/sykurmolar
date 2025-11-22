'''
triggers that force a response from sykurmolar
'''

import pyo64 as pyo
from random import uniform, sample
from mafs import incbind

if __name__ == "__main__":
	raise RuntimeError("Module relies on a pyo server being set up so cannot be run as main. Add code here for pyo server setup if I want to do this.")

durationMultiplierSimpleLoop = 1.03
maxDurationSimpleLoop = 20
minDurationSimpleLoop = 0.05 #20hz
sampleRate = 48000 # sampleRate is also defined in the main program. more reason to have some global info in a simple other script.
maxDurationSimpleLoopSamples = int(maxDurationSimpleLoop * sampleRate)

class No():

	def __init__(self):
		self.outputTrigger = pyo.Trig() # it'll never work

class Manual():

	def __init__(self):
		self.outputTrigger = pyo.Trig() # call .play() to play

class SimpleLoop():

	def __init__(self, duration):
		self.duration = duration
		self.outputTrigger = pyo.Metro(time = self.duration).play()
		self.latestTapTempo = 0 # in samples

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
			if self.duration/durationMultiplierSimpleLoop >= minDurationSimpleLoop:
				newDur = self.duration/durationMultiplierSimpleLoop
		elif amount > 0:
			if self.duration*durationMultiplierSimpleLoop <= maxDurationSimpleLoop:
				newDur = self.duration*durationMultiplierSimpleLoop
		self.updateDuration(newDur)

	def tapTempo(self, newTime):
		if newTime - self.latestTapTempo <= maxDurationSimpleLoopSamples:
			self.updateDuration((newTime - self.latestTapTempo) / sampleRate)
		self.latestTapTempo = newTime

class Swung():
	'''
	swung trigger
	takes another trigger as input, produces another trigger with a randomized delay on each
	ADD: control amount of swing
	'''

	def __init__(self, trigger, duration):
		self.inputTrigger = trigger
		self.outputTrigger = pyo.Trig()
		self.maxSwingDuration = duration/2
		self.minSwingDuration = 0.05 # 20hz
		self.swing = self.minSwingDuration #seconds - this is 20hz so minimum perceivable
		# create response to an input trigger
		self.responder = pyo.TrigFunc(self.inputTrigger, self.delayTriggerPlay)

	def updateMaxSwingDuration(self, newDuration):
		self.maxSwingDuration = newDuration/2

	def delayTriggerPlay(self):
		# set a delay to the trigger call between 0 and swing (unless maxSwingDuration)
		newDelay = uniform(0, min(self.swing, self.maxSwingDuration))
		self.delayedResponse = pyo.CallAfter(self.outputTrigger.play, time = newDelay)

	def incrementSwing(self, amount):
		# this will receive a value of -1 or 1 from knob
		# rather than divide each time ... it's 0.05s increments
		if amount == 1:
			self.swing = incbind(self.swing, 0.05, self.minSwingDuration, self.maxSwingDuration)
		elif amount == -1:
			self.swing = incbind(self.swing, -0.05, self.minSwingDuration, self.maxSwingDuration)

class Random():
	# basic random trigger

	def __init__(self, density):
		self.outputTrigger = pyo.Cloud(density = density).play()

class PeriodicInterruption():
	'''
	NOT CODED
	lets through one input continually (e.g. a Swung), and a selection from the other input for periodic intervals
	knob control over periodicity (time on vs off?)
	'''

	def __init__(self):
		return
	
class Combine():
	'''
	EITHER DOESN'T WORK OR ISN'T USED 
	combines a list of triggers to a single output trigger
	knob control over number to combine from the list - each new addition makes a random set of them
	receives the outputTriggers as triggersList
	in my application in Ammæli below, this is something of a prime phased rhythm generator
	'''
	def __init__(self, triggersList):
		self.triggersList = triggersList
		self.maxLength = len(self.triggersList)
		self.currentLength = 2
		# i don't think this is working - seems to only be one of the triggers, not all
		self.outputTrigger = pyo.Percent([self.triggersList[0], self.triggersList[1]], 100)

	def changeOutputTrigger(self):
		self.outputTrigger.setInput([self.triggersList[i-1] for i in sample(range(1, self.maxLength), self.currentLength)])

	def incrementLength(self, amount):
		if amount < 0:
			self.currentLength = incbind(self.currentLength, -1, 1, self.maxLength)
		elif amount > 0:
			self.currentLength = incbind(self.currentLength, 1, 1, self.maxLength)
		# after incrementing length, always changeOutputTrigger
		self.changeOutputTrigger()
		
	
primesLong = (2, 3, 5, 7, 11)
primesShort = (13, 17, 19, 23, 29)

class Ammæli():
	'''
	a few triggers based on a SimpleLoop's duration
	outputTrigger buttons function as a shift. knob edits.
		SimpleLoop: incrementDuration
		Swung: incrementSwing
		Combine: incrementLength
		PeriodicInterruption: interruptPeriodicity
	'''

	def __init__(self, duration, sampleCounter):
		self.duration = duration
		self.sampleCounter = sampleCounter
		self.t_SimpleLoop = SimpleLoop(self.duration)
		self.t_Swung = Swung(self.t_SimpleLoop.outputTrigger, self.duration)
		self.t_PrimesLong = [SimpleLoop(x) for x in self.calcDividedDurations(primesLong)]
		self.t_PrimesShort = [SimpleLoop(x) for x in self.calcDividedDurations(primesShort)]
		self.t_Combine = Combine([t.outputTrigger for t in self.t_PrimesLong])
		# add when coded: t_PeriodicInterruption. use t_PrimesShort

	def display(self, value):
		print(value)
		
	def calcDividedDurations(self, dividers):
		return [round(self.duration/x, 5) for x in dividers]
	
	def updateDurations(self):
		# check we got a new duration in our update of SimpleLoop, then apply it to all
		if self.t_SimpleLoop.duration != self.duration:
			self.duration = self.t_SimpleLoop.duration
			# apply to t_Primes
			newPrimesLongDurations = self.calcDividedDurations(primesLong)
			newPrimesShortDurations = self.calcDividedDurations(primesShort)
			for i in range(len(newPrimesLongDurations)):
				self.t_PrimesLong[i].updateDuration(newPrimesLongDurations[i])
			for i in range(len(newPrimesShortDurations)):
				self.t_PrimesShort[i].updateDuration(newPrimesShortDurations[i])
			# apply to t_Swung
			self.t_Swung.updateMaxSwingDuration(self.duration)
	
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

	def incrementCombineLength(self, amount):
		self.t_Combine.incrementLength(amount)