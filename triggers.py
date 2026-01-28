'''
triggers that force a response from sykurmolar

every class has to have:
	self.outputTrigger = pyo.Trig() object
	self.name (with a default)
'''
# local
import constants
from mafs import incbind, iterate, randomBinomial, pointsToDifference
# external
import pyo64 as pyo
from random import sample
from numpy.random import uniform

class No():

	def __init__(self, name='nei'):
		self.outputTrigger = pyo.Trig() # it'll never work
		self.name = name

class Manual():
	# for universal nya!
	# we have individual nya!, and nya! shifts to nei

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
		self.beatCount = 2
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
		self.rhythm = uniform(0, 1, constants.SWING_RHYTHM_MAX_BEATS).tolist()
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
		self.beatCount = incbind(self.beatCount, amount, 2, constants.SWING_RHYTHM_MAX_BEATS)
		self.updateDelays()

	def updateDuration(self, new):
		# receive new duration, store it, update delays
		self.duration = new
		self.updateDelays()

	def updateDelays(self):
		# recalculate list of delay durations based on rhythm * swing * duration
		self.delays = [j * self.swing * self.duration for j in self.rhythm[:self.beatCount]]


class Swung():
	'''
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

class Combination():
	'''
	combination of two (or more) input triggers, output as a single trigger

	attempt: mixes the inputs (which is a list) into a single stream
	as this is hopefully identical to the streams (a trig is 0s with a 1 in), outputTrigger shouldn't need changing
	'''

	def __init__(self, inputs, name='combo'):
		#inputs = [inputs[i-1].outputTrigger for i in range(len(inputs))] # grab triggers
		inputs = [x.outputTrigger for x in inputs] # grab triggers
		self.outputTrigger = pyo.Mix(inputs)
		self.name = name

class TappedRhythm():
	'''
	records and loops a tapped rhythm
	controls:
		'tap' begins tapping a rhythm, or appends a rhythm if within the timeout window
		'tapAndUse' ends tapping a rhythm and uses it, if within the timeout window
		'incrementDuration', for use by knob, slows or speeds the rhythm
		'nullNewRhythm' nullifies a new rhythm, effectively a cancel button
		'resetRhythmNow' (could be used by a button) resets rhythm to beginning

	we could add a swung trigger taking this as the input
	'''
	def __init__(self, sampleCounter, name='rhythm'):
		self.sampleCounter = sampleCounter
		self.currentRhythm = [constants.TAPRHYTHM_TIMEOUT_SAMPLES] # repeats longest
		# newRhythm is set at timeout, otherwise making a rhythm shortly after booting will incorporate program init time as a beat
		self.newRhythm = [-constants.TAPRHYTHM_TIMEOUT_SAMPLES]
		# Seq is number of time, so if time is 1 sample, i can hand Seq sequences of samples
		self.outputTrigger = pyo.Seq(time=constants.SAMPLE_RATE_IN_SECONDS, seq=self.currentRhythm).play()
		self.name = name

	def display(self, value):
		print(value)

	def nullNewRhythm(self):
		'''
		cancel the rhythm
		used to cancel a tapped rhythm in-progress
		'''
		self.newRhythm = [0]
	
	def setRhythm(self, newList):
		'''
		give the trigger object the new list, reset the new rhythm
		'''
		self.outputTrigger.setSeq(newList)
		self.nullNewRhythm()

	def resetRhythmNow(self):
		self.outputTrigger.stop()
		self.outputTrigger.play()

	def tap(self):
		'''
		begins a tapped rhythm, or appends if not timed out
		'''
		print('tap!')
		now = self.sampleCounter.get()
		diff = now - self.newRhythm[-1]
		print(diff)
		# if tap has timed out, replace the newRhythm list
		if diff >= constants.TAPRHYTHM_TIMEOUT_SAMPLES:
			self.newRhythm = [now]
		# otherwise, append to newRhythm list
		elif diff < constants.TAPRHYTHM_TIMEOUT_SAMPLES:
			self.newRhythm.append(now)

	def tapAndGo(self):
		'''
		tap rhythm, and then try to use it
		if i press this after a timeout, nothing happens
		'''
		now = self.sampleCounter.get()
		diff = now - self.newRhythm[-1]
		# if tap has timed out, IGNORE
		if diff >= constants.TAPRHYTHM_TIMEOUT_SAMPLES:
			return
		# otherwise, proceed
		elif diff < constants.TAPRHYTHM_TIMEOUT_SAMPLES:
			# append now to newRhythm list
			self.newRhythm.append(now)
			# turn newRhythm list into a difference between times, and pass it to currentRhythm
			self.currentRhythm = pointsToDifference(self.newRhythm)
			# give this to trigger and reset
			self.setRhythm(self.currentRhythm)
			self.resetRhythmNow()
			self.display(self.currentRhythm)


	def incrementDuration(self, amount):
		'''
		used by knob to change speed of all beats simultaneously
		multiply/divide rhythm by common value
		tests result against limits before implementing
		'''
		# receives -1, 1
		if amount < 0:
			# divide down
			currentRhythmCandidate = [int(i/constants.TAPRHYTHM_DURATION_MULTIPLIER) for i in self.currentRhythm]
			# test if low limit is exceeded, exit if so
			for i in currentRhythmCandidate:
				if i < constants.TINY_DUR_SAMPLES:
					return
		elif amount > 0:
			# multiply up
			currentRhythmCandidate = [int(i*constants.TAPRHYTHM_DURATION_MULTIPLIER) for i in self.currentRhythm]
			# test if high limited is exceeded, exit if so
			for i in currentRhythmCandidate:
				if i > constants.TAPRHYTHM_TIMEOUT_SAMPLES:
					return
		# if we reached here, we got a usable new currentRhythmCandidate, so apply it
		self.currentRhythm = currentRhythmCandidate
		self.setRhythm(self.currentRhythm)
		#self.resetRhythmNow()

	
class Ammæli():
	'''
	a few triggers based on a SimpleLoop's duration
	outputTrigger buttons function as a shift. knob edits.
		SimpleLoop: incrementDuration
		Swung: incrementSwing (also changes SwungRhythm)
		SwungRhythm: incrementSwungRhythmBeats
	'''

	def __init__(self, duration, sampleCounter, name='ammæli'):
		self.name = name
		self.duration = duration
		self.sampleCounter = sampleCounter
		self.t_SimpleLoop = SimpleLoop(self.duration, name=self.name+'_simple')
		self.t_Swung = Swung(self.t_SimpleLoop.outputTrigger, self.duration, name=self.name+'_swung')
		self.t_SwungRhythm = SwungRhythm(self.t_SimpleLoop.outputTrigger, self.duration, name=self.name+'_swythm')
		self.t_Primes = [SimpleLoop(x, name=self.name+'_prime') for x in self.calcDividedDurations(constants.PRIMES)]
		
	def display(self, value):
		print(value)
		
	def calcDividedDurations(self, dividers):
		return [round(self.duration/x, 5) for x in dividers]
	
	def updateDurations(self):
		# check we got a new duration in our update of SimpleLoop, then apply it to all
		if self.t_SimpleLoop.duration != self.duration:
			self.duration = self.t_SimpleLoop.duration
			# apply to t_Primes
			newPrimesDurations = self.calcDividedDurations(constants.PRIMES)
			for i in range(len(newPrimesDurations)):
				self.t_Primes[i].updateDuration(newPrimesDurations[i])
			# apply to t_Swung
			self.t_Swung.updateDuration(self.duration)
			# apply to t_SwungRhythm
			self.t_SwungRhythm.updateDuration(self.duration)

	# centrally updating values - otherwise calling functions with getattr might not work

	def tapTempo(self):
		self.t_SimpleLoop.tapTempo(self.sampleCounter.get())
		self.updateDurations()

	def newSwungRhythm(self):
		self.t_SwungRhythm.newRhythm()
		self.display("SWUNGERT")

	def incrementDuration(self, amount):
		self.t_SimpleLoop.incrementDuration(amount)
		self.updateDurations()
		self.display(self.duration)

	def incrementSwing(self, amount):
		self.t_Swung.incrementSwing(amount)
		self.t_SwungRhythm.incrementSwing(amount)
		self.display(self.t_Swung.swing)

	def incrementSwungRhythmBeats(self, amount):
		self.t_SwungRhythm.incrementBeatCount(amount)
		self.display(self.t_SwungRhythm.beatCount)