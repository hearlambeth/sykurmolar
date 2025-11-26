'''
a Sykurmoli is a collection of Bitar
Biti is the audio player itself, which receives instructions from Sykurmoli as to its new values and states
Sykurmoli creates new values on receipt of a trigger
'''
# local
import mafs, constants
# external
import pyo64 as pyo
import random
from numpy.random import randint

'''
ENDALAUSIR & ENDANLEGIR BITAR

two classes with the same functions
Endalaus contains a set of objects for endless playback
Endanlegur contains a set of objects for looping playback
'''

class BitiEndalaus():

	def __init__(self, sampleRate, audioTable):
		self.sampleRate = sampleRate
		self.audioTableDurationSamples = audioTable.size
        # create sets of two objects, so each envelope can run to end when changing position
		# positions = distance along table, normalised to between 0 and 1
		self.positions = [pyo.Linseg([(0, 0), (1, 1)]).stop(), pyo.Linseg([(0, 0), (1, 1)]).stop()]
		self.envelopes = [pyo.Fader(constants.ENDALAUS_FADE_SECONDS, constants.ENDALAUS_FADE_SECONDS), pyo.Fader(constants.ENDALAUS_FADE_SECONDS, constants.ENDALAUS_FADE_SECONDS)]
		self.readers = [pyo.Pointer2(table = audioTable, index = self.positions[0], mul = self.envelopes[0]), 
			pyo.Pointer2(table = audioTable, index = self.positions[1], mul = self.envelopes[1])]
		self.panPortamentos = [pyo.SigTo(0.5, constants.PORTAMENTO_TRANSITION_SECONDS, init = 0.5), pyo.SigTo(0.5, constants.PORTAMENTO_TRANSITION_SECONDS, init = 0.5)]
		self.volPortamentos = [pyo.SigTo(1, constants.PORTAMENTO_TRANSITION_SECONDS, init = 1), pyo.SigTo(1, constants.PORTAMENTO_TRANSITION_SECONDS, init = 1)]
		self.envelopes[0].mul = self.volPortamentos[0]
		self.envelopes[1].mul = self.volPortamentos[1]
		self.outs = [pyo.Pan(self.readers[0], pan = self.panPortamentos[0]), pyo.Pan(self.readers[1], pan = self.panPortamentos[1])]
		# self.outs = [pyo.Pan(self.readers[0], pan = self.panPortamentos[0]).out(), pyo.Pan(self.readers[1], pan = self.panPortamentos[1]).out()] - simple output, bypassing Mixer
		self.currentSetIndex = 0
		# initial values
		self.direction = 1
		self.length = 1
		self.pan = 1
		self.pitchMacro = 1
		self.pitchMicro = 0
		self.rate = 1
		self.startPoint = 1
		self.volume = 1

	def play(self):
		#self.positions[self.currentSetIndex].stop()
		self.positions[self.currentSetIndex].play()
		self.envelopes[self.currentSetIndex].play()

	def stop(self):
		# i stop the envelope, but not the positions, as this would sound as an audio glitch
		self.envelopes[self.currentSetIndex].stop()
		# switch currentSetIndex
		self.currentSetIndex = 1 - self.currentSetIndex

	def changeDirection(self, new):
		self.direction = new
		self._changeTrajectory()

	def changeLength(self, new):
		self.length = new
		# ignores

	def changePan(self, new):
		self.pan = new
		self.panPortamentos[self.currentSetIndex].value = new

	def changePitchMacro(self, new):
		self.pitchMacro = new
		self.rate = mafs.newRate(self.pitchMacro, self.pitchMicro)
		self._changeTrajectory()

	def changePitchMicro(self, new):
		self.pitchMicro = new
		self.rate = mafs.newRate(self.pitchMacro, self.pitchMicro)
		self._changeTrajectory()
	
	def changeRate(self, new):
		self.rate = new
		self._changeTrajectory()

	def changeStartPoint(self, new):
		self.startPoint = new
		self._changeTrajectory()

	def changeVolume(self, new):
		self.volume = new
		#self.envelopes[self.currentSetIndex].mul = new
		self.volPortamentos[self.currentSetIndex].value = new

	def _changeTrajectory(self):
		# direction, rate, startPoint are all dependent on each other, so need to be centrally calculated
		# (on my revision here i don't fully understand the LinSeg parameters)
		# if forward, duration is everything in front; if reverse, duration is everything behind
		if self.direction == 1:
			duration = self.audioTableDurationSamples - self.startPoint
		elif self.direction == 0:
			duration = self.startPoint
		# change duration to seconds(?)
		duration /= self.rate
		duration /= self.sampleRate
		# make a normalised version of startPoint (between 0 and 1?)
		startPointNormalised = self.startPoint / self.audioTableDurationSamples
		# update positions: (time1, position1), (time2, position2)
		# position1 and position2 are normalised between 0 and 1
		self.positions[self.currentSetIndex].list = [
			(0, startPointNormalised), (duration, self.direction)]

class BitiEndanlegur():

	def __init__(self, sampleRate, audioTable):
		self.sampleRate = sampleRate
		self.looper = pyo.Looper(table = audioTable, start = 0, dur = 0.1, startfromloop = True).stop() # startfromloop otherwise it'll start from the beginning each time
		self.pitchPortamento = pyo.SigTo(1, constants.PORTAMENTO_TRANSITION_SECONDS, init = 1)
		self.looper.pitch = self.pitchPortamento
		self.volPortamento = pyo.SigTo(1, constants.PORTAMENTO_TRANSITION_SECONDS, init = 1)
		self.looper.mul = self.volPortamento
		self.panPortamento = pyo.SigTo(0.5, constants.PORTAMENTO_TRANSITION_SECONDS, init = 0.5)
		self.out = pyo.Pan(self.looper, pan = self.panPortamento)
		#self.out = pyo.Pan(self.looper, pan = self.panPortamento).out() - simple output, bypassing Mixer
		# initial values
		self.direction = 1
		self.length = 1
		self.pan = 1
		self.pitchMacro = 1
		self.pitchMicro = 0
		self.rate = 1
		self.startPoint = 1
		self.volume = 1

	def play(self):
		self.looper.play()

	def stop(self):
		self.looper.stop()

	def changeDirection(self, new):
		self.direction = new
		# convert to looper mode: 1 = forwards, 2 = backwards
		self.looper.mode = int(2 - new)

	def changeLength(self, new):
		self.length = new
		self.looper.dur = new

	def changePan(self, new):
		self.pan = new
		self.panPortamento.value = new

	def changePitchMacro(self, new):
		self.pitchMacro = new
		self.rate = mafs.newRate(self.pitchMacro, self.pitchMicro)
		self.pitchPortamento.value = self.rate

	def changePitchMicro(self, new):
		self.pitchMicro = new
		self.rate = mafs.newRate(self.pitchMacro, self.pitchMicro)
		self.pitchPortamento.value = self.rate

	def changeRate(self, new):
		self.rate = new
		self.pitchPortamento.value = new

	def changeStartPoint(self, new):
		self.startPoint = new
		self.looper.start = float(new / self.sampleRate)

	def changeVolume(self, new):
		self.volume = new
		self.volPortamento.value = new



'''
SYKURMOLI
a collection of Bitar, sending instructions to these after trigger inputs

(fill in description of variable limits here)

to clarify:
variables:
	StartPoint settings
	recSourcesInUse, recSourceToChange, recSourceBias -> startPointLineInInterrupt
'''

class Sykurmoli():

	def __init__(self, name, sampleRate, numberOfBitar, triggers, startPoints, audioTable):
		self.name = str(name)
		self.sampleRate = sampleRate
		self.numberOfBitar = numberOfBitar
		self.triggers = triggers
		self.startPoints = startPoints
		self.audioTable = audioTable
		self.startPointOffsetMax = int(self.sampleRate/2)
		self.startPointOffset = self.startPointOffsetMax
		self.createBitar()
		self.setInitialValues()
		self.createTriggerObjects()
		self.newAll()
		self.stop()

	def setInitialValues(self):
		self.noOfActiveBitar = 1
		self.endingBitar = []
		self.respondsToTriggerIndex = 0
		self.startPointIndex = 0 # 0 = lineIn
		self.lineInInterruptBias = 0
		self.pitchMacroMultiplier = 12
		# alphabetically-arranged bias/response/(min/max) sets
		self.audibleBias = 1
		self.audibleResponse = 1
		self.directionBias = 1
		self.directionResponse = 1
		self.endarBias = 0
		self.endarResponse = 1
		self.globalResponse = 1
		self.lengthBias = 0.5
		self.lengthResponse = 1
		self.panBias = 0.5
		self.panResponse = 1
		self.panMax = 0.5
		self.panMin = 0.5
		self.pitchMacroBias = 0.5
		self.pitchMacroResponse = 1
		self.pitchMacroMin = 0
		self.pitchMacroMax = 0
		self.pitchMicroBias = 0.5
		self.pitchMicroResponse = 1
		self.pitchMicroMin = 0
		self.pitchMicroMax = 0
		self.startPointResponse = 1
		self.volumeBias = 0.5
		self.volumeResponse = 1
		self.volumeMin = 1
		self.volumeMax = 1
		# indices to move through our lists
		# one for values, one mobile so freeze will not cause it to also be looped
		self.i = 0
		self.iMobile = 0 # one that keeps moving
		# freeze
		self.freeze = False
		self.freezeLength = 1
		self.freezeCounter = 1
		self.freezeResetIndex = 0 # gets set when freeze is turned on
		# forced override of response values, so next will always respond
		self.forceRespondAudibleOnce = 0
		self.forceRespondDirectionOnce = 0
		self.forceRespondEndarOnce = 0
		self.forceRespondLengthOnce = 0
		self.forceRespondPanOnce = 0
		self.forceRespondPitchMacroOnce = 0
		self.forceRespondPitchMicroOnce = 0
		self.forceRespondStartPointOnce = 0
		self.forceRespondVolumeOnce = 0

	def display(self, newText, newValue=None):
		# display a single data point
		if newValue != None:
			print('[' + self.name + '] ' + str(newText) + ' ' + str(newValue))
		else:
			print('[' + self.name + '] ' + str(newText))

	def displayFull(self):
		# display a fuller set of info about the sykurmoli
		# line1: name
		print('--- sykurmoli {0} ---'.format(self.name))
		# line2: top info
		print('bitar:{0} trig:{1} start:{2} freeze:{3}'.format(
			self.noOfActiveBitar, self.triggers[self.respondsToTriggerIndex].name, self.startPointIndex, self.freezeLength
		))
		# bias sets with max/min/bias/change
		print('pan\t{0:.2f} {1:.2f} [{2:.2f} {3:.2f}]\nPI[x{4}]\t{5:.2f} {6:.2f} [{7:.2f} {8:.2f}]\npi\t{9:.2f} {10:.2f} [{11:.2f} {12:.2f}]\nvol\t{13:.2f} {14:.2f} [{15:.2f} {16:.2f}]'.format(
			self.panMax, self.panMin, self.panBias, self.panResponse,
			self.pitchMacroMultiplier, self.pitchMacroMax, self.pitchMacroMin, self.pitchMacroBias, self.pitchMacroResponse,
			self.pitchMicroMax, self.pitchMicroMin, self.pitchMicroBias, self.pitchMicroResponse,
			self.volumeMax, self.volumeMin, self.volumeBias, self.volumeResponse
		))
		# bias sets with just bias/change
		print('heyran\t{0:.2f} {1:.2f}\nendar\t{2:.2f} {3:.2f}\nlengd\t{4:.2f} {5:.2f}\ndir\t{6:.2f} {7:.2f}'.format(
			self.audibleBias, self.audibleResponse, self.endarBias, self.endarResponse,
			self.lengthBias, self.lengthResponse, self.directionBias, self.directionResponse
		))
	
	# MAKE, STOP, RESET BITAR

	def createBitar(self):
		# create bitar
		self.bitar = [[BitiEndalaus(self.sampleRate, self.audioTable), BitiEndanlegur(self.sampleRate, self.audioTable)] for i in range(self.numberOfBitar)]
		# mix them
		self.out = pyo.Mixer(outs=1, chnls=2).out() # one output made of 2 channels
		# mixer setup - add inputs
		for biti in self.bitar:
			self.out.addInput(voice=None, input=biti[0].outs[0])
			self.out.addInput(voice=None, input=biti[0].outs[1])
			self.out.addInput(voice=None, input=biti[1].out)
		# mixer setup - send inputs to output
		for key in self.out.getKeys():
			self.out.setAmp(key, 0, 1)
		# assign volume control 
		self.volPortamento = pyo.SigTo(1, constants.PORTAMENTO_TRANSITION_SECONDS, init = 1)
		self.out.mul = self.volPortamento

	def changeVolume(self, new):
		# overall volume for fader control
		self.volPortamento.value = new
	
	def stop(self):
		self.changeTriggerSource(0)
		# stop ALL bitar
		for biti in self.bitar:
			biti[0].stop()
			biti[1].stop()

	def reset(self):
		self.stop()
		self.setInitialValues()
		self.newAll()

	def resetForceRespondOnce(self):
		self.forceRespondAudibleOnce = 0
		self.forceRespondDirectionOnce = 0
		self.forceRespondEndarOnce = 0
		self.forceRespondLengthOnce = 0
		self.forceRespondPanOnce = 0
		self.forceRespondPitchMacroOnce = 0
		self.forceRespondPitchMicroOnce = 0
		self.forceRespondStartPointOnce = 0
		self.forceRespondVolumeOnce = 0

	# TRIGGERS
	# the nyaTrigger exists here because i want to be able to call

	def createTriggerObjects(self):
		self.triggerResponder = pyo.TrigFunc(self.triggers[self.respondsToTriggerIndex].outputTrigger, self.respondToTrigger)
		# though this is maybe redundant - respondToTrigger could just be called -
		# we have a trigger here in case we want it to be used elsewhere, like in a tapped rhythm
		self.nyaTrigger = pyo.Trig().stop()
		self.nyaResponder = pyo.TrigFunc(self.nyaTrigger, self.respondToTrigger)

	def changeTriggerSource(self, index):
		# ignore if out of range
		if index < len(self.triggers):
			self.respondsToTriggerIndex = index
			self.triggerResponder.setInput(self.triggers[index].outputTrigger, fadetime = 0)
			self.display('t_' + self.triggers[index].name)

	def changeTriggerSourceChoice(self, rangeTuple):
		# choose across a range of trigger sources
		self.changeTriggerSource(random.randint(rangeTuple[0], rangeTuple[1]))

	def nya(self):
		# play the trigger then set source to NoTrigger
		self.nyaTrigger.play()
		self.display('nya!')
		self.changeTriggerSource(0)

	# FREEZE

	def pickNewFreezeIndex(self):
		self.freezeResetIndex = self.i

	def freezeOn(self):
		self.pickNewFreezeIndex()
		self.freezeCounter = 1
		self.freeze = True
		self.display('f_','on')

	def freezeOff(self):
		self.freezeCounter = 1
		self.freeze = False
		self.display('f_','off')

	def changeFreezeLength(self, amount):
		self.freezeLength = mafs.incbind(self.freezeLength, amount, 1, constants.FREEZE_LENGTH_MAX)
		self.display('f_lengd', self.freezeLength)

	def reverseFreezeVariables(self):
		# get our first indices, e.g. [998, 999, 0, 1] and reversed version [1, 0, 999, 998]
		ind = mafs.generateIndicesList(self.freezeResetIndex, constants.VARIABLES_LIST_LENGTH - 1, self.freezeLength)
		indR = ind[::-1]
		# swap the values using x, y = y, x
		for i, v in enumerate(ind):
			# swap values once, stop once the two values cross (otherwise it will reverse all values again!)
			if v < indR[i]:
				for n in range(self.numberOfBitar):
					self.audibleList[n][v], self.audibleList[n][indR[i]] = self.audibleList[n][indR[i]], self.audibleList[n][v]
					self.directionList[n][v], self.directionList[n][indR[i]] = self.directionList[n][indR[i]], self.directionList[n][v]
					self.endarList[n][v], self.endarList[n][indR[i]] = self.endarList[n][indR[i]], self.endarList[n][v]
					self.lengthList[n][v], self.lengthList[n][indR[i]] = self.lengthList[n][indR[i]], self.lengthList[n][v]
					self.panList[n][v], self.panList[n][indR[i]] = self.panList[n][indR[i]], self.panList[n][v]
					self.pitchMacroList[n][v], self.pitchMacroList[n][indR[i]] = self.pitchMacroList[n][indR[i]], self.pitchMacroList[n][v] 
					self.pitchMicroList[n][v], self.pitchMicroList[n][indR[i]] = self.pitchMicroList[n][indR[i]], self.pitchMicroList[n][v]
					self.startPointIndices[n][v], self.startPointIndices[n][indR[i]] = self.startPointIndices[n][indR[i]], self.startPointIndices[n][v]
					self.startPointList[n][v], self.startPointList[n][indR[i]] = self.startPointList[n][indR[i]], self.startPointList[n][v]
					self.volumeList[n][v], self.volumeList[n][indR[i]] = self.volumeList[n][indR[i]], self.volumeList[n][v]
			else:
				break
		self.display('f_reverse')
	
	def shuffleFreezeVariables(self):
		# see reverse, but shuffled list instead
		# get our first indices, e.g. [998, 999, 0, 1] and shuffled version
		ind = mafs.generateIndicesList(self.freezeResetIndex, constants.VARIABLES_LIST_LENGTH - 1, self.freezeLength)
		indR = list(ind) # a copy
		random.shuffle(indR)
		# swap the values using x, y = y, x
		# probably swaps them more than is necessary but that's okay?
		for i, v in enumerate(ind):
			for n in range(self.numberOfBitar):
				self.audibleList[n][v], self.audibleList[n][indR[i]] = self.audibleList[n][indR[i]], self.audibleList[n][v]
				self.directionList[n][v], self.directionList[n][indR[i]] = self.directionList[n][indR[i]], self.directionList[n][v]
				self.endarList[n][v], self.endarList[n][indR[i]] = self.endarList[n][indR[i]], self.endarList[n][v]
				self.lengthList[n][v], self.lengthList[n][indR[i]] = self.lengthList[n][indR[i]], self.lengthList[n][v]
				self.panList[n][v], self.panList[n][indR[i]] = self.panList[n][indR[i]], self.panList[n][v]
				self.pitchMacroList[n][v], self.pitchMacroList[n][indR[i]] = self.pitchMacroList[n][indR[i]], self.pitchMacroList[n][v] 
				self.pitchMicroList[n][v], self.pitchMicroList[n][indR[i]] = self.pitchMicroList[n][indR[i]], self.pitchMicroList[n][v]
				self.startPointIndices[n][v], self.startPointIndices[n][indR[i]] = self.startPointIndices[n][indR[i]], self.startPointIndices[n][v]
				self.startPointList[n][v], self.startPointList[n][indR[i]] = self.startPointList[n][indR[i]], self.startPointList[n][v]
				self.volumeList[n][v], self.volumeList[n][indR[i]] = self.volumeList[n][indR[i]], self.volumeList[n][v]
		self.display('f_shuffle')


	# OTHER

	def changeActiveBitar(self, amount):
		# queue to end any bitar that are being removed on next trigger
		if amount < 0:
			self.endingBitar.append(self.noOfActiveBitar - 1)
		# increment & bind the bitar
		self.noOfActiveBitar = int(mafs.incbind(self.noOfActiveBitar, amount, 1, self.numberOfBitar))
		self.display('bitar', self.noOfActiveBitar)

	def resetPitchMicro(self):
		self.pitchMicroMin = 0
		self.pitchMicroMax = 0
		self.createPitchMicroList()
		self.display('pitch reset')

	def changePitchMacroMultiplier(self, new):
		# receives some fixed values from buttons
		self.pitchMacroMultiplier = new
		self.createPitchMacroList()
		self.display('PITCH mul', new)

	def changeStartPointIndex(self, index):
		self.startPointIndex = index
		self.createStartPointIndices()
		self.createStartPointList()
		self.display('startindex', index)

	def changeStartPointOffsetMax(self, amount):
		# receives an amount, which is one of: 200, 5000, 24000
		self.startPointOffset = amount
		self.createStartPointList()
		self.display('startrange', self.startPointOffset)

	def newStartPoint(self, startPointIndex):
		# takes a start point index and returns a sample position with randomization
		return self.startPoints[startPointIndex].startPositionSamples + randint(0 - self.startPointOffset, high = self.startPointOffset + 1)
	
	def createBitaEndTracker(self):
		'''
		creates a list to track if BitiEndalaus (0) or BitiEndanlegur (1) is active
		this list is created on reset and then maintained during respondToTrigger
		this allows respondToTrigger to apply updates only to the relevant set of audio objects
		short name because i use this frequently
		assumes i make bias start at 0 or 1
		'''
		self.be = [self.endarBias for i in range(self.numberOfBitar)]

    # BIAS/RESPONSE CALCULATIONS

	def newAll(self):
		# sibelius crashed
		self.createAudibleList()
		self.createDirectionList()
		self.createEndarList()
		self.createLengthList()
		self.createPanList()
		self.createPitchMacroList()
		self.createPitchMicroList()
		self.createStartPointIndices()
		self.createStartPointList()
		self.createVolumeList()
		self.createGlobalResponseList()
		self.createAudibleResponseList()
		self.createDirectionResponseList()
		self.createEndarResponseList()
		self.createLengthResponseList()
		self.createPanResponseList()
		self.createPitchMacroResponseList()
		self.createPitchMicroResponseList()
		self.createStartPointResponseList()
		self.createVolumeResponseList()
		self.createBitaEndTracker()
	
	#	BIAS

	def createAudibleList(self):
		self.audibleList = [mafs.randomBinomial(self.audibleBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createDirectionList(self):
		self.directionList = [mafs.randomBinomial(self.directionBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createEndarList(self):
		self.endarList = [mafs.randomBinomial(self.endarBias, constants.VARIABLES_LIST_LENGTH)  for i in range(self.numberOfBitar)]

	def createLengthList(self):
		# for the time being, do use triangular, but replace it soon
		# old code created ranges and set lengths as uniform distributions across those ranges:
		# <0.33: 0.05 to 0.2; <0.66: 0.1 to 1; else, 0.5 to 3
		# on tests, even bias of 0.01 goes nowhere near the minimum and contains values over 0.5
		self.lengthList = [mafs.randomBeta(0, 1, self.lengthBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createPanList(self):
		#panMin = max(self.panCenter - self.panSpread, 0)
		#panMax = min(self.panCenter + self.panSpread, 1)
		self.panList = [mafs.randomBeta(self.panMin, self.panMax, self.panBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createPitchMacroList(self):
		self.pitchMacroList = [
			[int(round(j, 0)) * self.pitchMacroMultiplier for j in mafs.randomBeta(self.pitchMacroMin, self.pitchMacroMax, self.pitchMacroBias, constants.VARIABLES_LIST_LENGTH)]
			  for i in range(self.numberOfBitar)
			  ]
		'''= a bunch of these: pitchMacro = mafs.randomTriangular(self.pitchMacroMin, self.pitchMacroMax, self.pitchMacroBias, VARIABLESLISTLENGTH)
		# set each value to a whole floored integer, then multiply by the macromultiplier
		self.pitchMacroList = [int(round(i, 0)) * self.pitchMacroMultiplier for i in pitchMacro]'''

	def createPitchMicroList(self):
		self.pitchMicroList = [mafs.randomBeta(self.pitchMicroMin, self.pitchMicroMax, self.pitchMicroBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createStartPointList(self):
		'''
		startPointList is a generic list of start points based on the index
		'''
		s = self.startPoints[self.startPointIndex].startPositionSamples
		self.startPointList = [
				#self.newStartPoint(self.startPointIndex) for j in range(VARIABLESLISTLENGTH)
				randint(low = s - self.startPointOffset, high = s + self.startPointOffset, size = constants.VARIABLES_LIST_LENGTH).tolist() for i in range(self.numberOfBitar)
		]

	def createStartPointIndices(self):
		# set of values to determine whether to poll from startPointList or 
		# (if index = 0) get new line value
		# if startPointIndex is actually 0 ... just returns 0
		if self.startPointIndex == 0:
			self.startPointIndices = [[0 for j in range(constants.VARIABLES_LIST_LENGTH)] for i in range(self.numberOfBitar)]
		else:
			self.startPointIndices = [
				[
					self.startPointIndex if j else 0 for j in mafs.randomBinomial(1 - self.lineInInterruptBias, constants.VARIABLES_LIST_LENGTH)
					]
				for i in range(self.numberOfBitar)
			]
	
	def createVolumeList(self):
		self.volumeList = [mafs.randomBeta(self.volumeMin, self.volumeMax, self.volumeBias, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	#	RESPONSE

	def createGlobalResponseList(self):
		self.globalResponseList = [mafs.randomBinomial(self.globalResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createAudibleResponseList(self):
		self.audibleResponseList = [mafs.randomBinomial(self.audibleResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createDirectionResponseList(self):
		self.directionResponseList = [mafs.randomBinomial(self.directionResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createEndarResponseList(self):
		self.endarResponseList = [mafs.randomBinomial(self.endarResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createLengthResponseList(self):
		self.lengthResponseList = [mafs.randomBinomial(self.lengthResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createPanResponseList(self):
		self.panResponseList = [mafs.randomBinomial(self.panResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createPitchMacroResponseList(self):
		self.pitchMacroResponseList = [mafs.randomBinomial(self.pitchMacroResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createPitchMicroResponseList(self):
		self.pitchMicroResponseList = [mafs.randomBinomial(self.pitchMicroResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createStartPointResponseList(self):
		self.startPointResponseList = [mafs.randomBinomial(self.startPointResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	def createVolumeResponseList(self):
		self.volumeResponseList = [mafs.randomBinomial(self.volumeResponse, constants.VARIABLES_LIST_LENGTH) for i in range(self.numberOfBitar)]

	# 	CHANGING 'BIAS'

	def changeAudibleBias(self, amount):
		new = mafs.incbind(self.audibleBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.audibleBias:
			self.audibleBias = new
			self.createAudibleList()
		self.display('audible_bias', self.audibleBias)

	def changeDirectionBias(self, amount):
		new = mafs.incbind(self.directionBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.directionBias:
			self.directionBias = new
			self.createDirectionList()
		self.display('direction_bias', self.directionBias)

	def changeEndarBias(self, amount):
		new = mafs.incbind(self.endarBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.endarBias:
			self.endarBias = new
			self.createEndarList()
		self.display('endar_bias', self.endarBias)

	def changeLengthBias(self, amount):
		new = mafs.incbind(self.lengthBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.lengthBias:
			self.lengthBias = new
			self.createLengthList()
		self.display('lengd_bias', self.lengthBias)

	def changeLineInInterruptBias(self, amount):
		# bias but not a set - doesn't have a "changes" pair
		# create just startPointIndices, which tells us in respondToTrigger to create a new start value based on current position
		new = mafs.incbind(self.lineInInterruptBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.lineInInterruptBias:
			self.lineInInterruptBias = new
			self.createStartPointIndices()
		self.display('línuleiki', self.lineInInterruptBias)


	def changePanBias(self, amount):
		new = mafs.incbind(self.panBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.panBias:
			self.panBias = new
			self.createPanList()
		self.display('pönnukaka_bias', self.panBias)

	def changePitchMacroBias(self, amount):
		new = mafs.incbind(self.pitchMacroBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.pitchMacroBias:
			self.pitchMacroBias = new
			self.createPitchMacroList()
		self.display('PITCH_bias', self.pitchMacroBias)

	def changePitchMicroBias(self, amount):
		new = mafs.incbind(self.pitchMicroBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.pitchMicroBias:
			self.pitchMicroBias = new
			self.createPitchMicroList()
		self.display('pitch_bias', self.pitchMicroBias)

	def changeVolumeBias(self, amount):
		new = mafs.incbind(self.volumeBias, amount / constants.KNOB_DIV, 0, 1)
		if new != self.volumeBias:
			self.volumeBias = new
			self.createVolumeList()
		self.display('volume_bias', self.volumeBias)

	# 	CHANGING 'RESPONSE'

	def changeGlobalResponse(self, amount):
		new = mafs.incbind(self.globalResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.globalResponse:
			self.globalResponse = new
			self.createGlobalResponseList()
		self.display('allt_sv', self.globalResponse)

	def changeAudibleResponse(self, amount):
		new = mafs.incbind(self.audibleResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.audibleResponse:
			self.audibleResponse = new
			self.createAudibleResponseList()
		self.display('audible_sv', self.audibleResponse)

	def changeDirectionResponse(self, amount):
		new = mafs.incbind(self.directionResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.directionResponse:
			self.directionResponse = new
			self.createDirectionResponseList()
		self.display('direction_sv', self.directionResponse)

	def changeEndarResponse(self, amount):
		new = mafs.incbind(self.endarResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.endarResponse:
			self.endarResponse = new
			self.createEndarResponseList()
		self.display('endar_sv', self.endarResponse)

	def changeLengthResponse(self, amount):
		new = mafs.incbind(self.lengthResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.lengthResponse:
			self.lengthResponse = new
			self.createLengthResponseList()
		self.display('lengd_sv', self.lengthResponse)

	def changePanResponse(self, amount):
		new = mafs.incbind(self.panResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.panResponse:
			self.panResponse = new
			self.createPanResponseList()
		self.display('pönnukaka_sv', self.panResponse)

	def changePitchMacroResponse(self, amount):
		new = mafs.incbind(self.pitchMacroResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.pitchMacroResponse:
			self.pitchMacroResponse = new
			self.createPitchMacroResponseList()
		self.display('PITCH_sv', self.pitchMacroResponse)

	def changePitchMicroResponse(self, amount):
		new = mafs.incbind(self.pitchMicroResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.pitchMicroResponse:
			self.pitchMicroResponse = new
			self.createPitchMicroResponseList()
		self.display('pitch_sv', self.pitchMicroResponse)

	def changeStartPointResponse(self, amount):
		new = mafs.incbind(self.startPointResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.startPointResponse:
			self.startPointResponse = new
			self.createStartPointResponseList()
		self.display('startpoint_sv', self.startPointResponse)

	def changeVolumeResponse(self, amount):
		new = mafs.incbind(self.volumeResponse, amount / constants.KNOB_DIV, 0, 1)
		if new != self.volumeResponse:
			self.volumeResponse = new
			self.createVolumeResponseList()
		self.display('volume_sv', self.volumeResponse)

	# 	CHANGING ADDITIONAL VARIABLES IN BIAS/RESPONSE SETS: max, min, spread, mid
	# these only apply to some. not: audible, direction, endar, length
	# with Mid, only checking if Min changed, as Min and Max move together

	# 		PAN

	def changePanMin(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMinimum(amount, self.panMin, self.panMax, 0, 1)
		if new != self.panMin:
			self.panMin = new
			self.createPanList()
		self.display('pönnuköku_min', self.panMin)

	def changePanMax(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMaximum(amount, self.panMin, self.panMax, 0, 1)
		if new != self.panMax:
			self.panMax = new
			self.createPanList()
		self.display('pönnuköku_max', self.panMax)

	def changePanMid(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromMiddle(amount, self.panMin, self.panMax, 0, 1)
		if newMin != self.panMin:
			self.panMin, self.panMax = newMin, newMax
			self.createPanList()
		self.display('pönnuköku_min', self.panMin)
		self.display('pönnuköku_max', self.panMax)

	def changePanSpread(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromSpread(amount, self.panMin, self.panMax, 0, 1)
		if newMin != self.panMin or newMax != self.panMax:
			self.panMin, self.panMax = newMin, newMax
			self.createPanList()
		self.display('pönnuköku_min', self.panMin)
		self.display('pönnuköku_max', self.panMax)

	# 		PITCHMACRO

	def changePitchMacroMin(self, amount):
		# amount unchanged
		new = mafs.newMinimum(amount, self.pitchMacroMin, self.pitchMacroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if new != self.pitchMacroMin:
			self.pitchMacroMin = new
			self.createPitchMacroList()
		self.display('PITCH_min', self.pitchMacroMin)

	def changePitchMacroMax(self, amount):
		# amount unchanged
		new = mafs.newMaximum(amount, self.pitchMacroMin, self.pitchMacroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if new != self.pitchMacroMax:
			self.pitchMacroMax = new
			self.createPitchMacroList()
		self.display('PITCH_max', self.pitchMacroMax)

	def changePitchMacroMid(self, amount):
		# amount unchanged
		newMin, newMax = mafs.newFromMiddle(amount, self.pitchMacroMin, self.pitchMacroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if newMin != self.pitchMacroMin:
			self.pitchMacroMin, self.pitchMacroMax = newMin, newMax
			self.createPitchMacroList()
		self.display('PITCH_min', self.pitchMacroMin)
		self.display('PITCH_max', self.pitchMacroMax)

	def changePitchMacroSpread(self, amount):
		# amount unchanged
		newMin, newMax = mafs.newFromSpread(amount, self.pitchMacroMin, self.pitchMacroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if newMin != self.pitchMacroMin or newMax != self.pitchMacroMax:
			self.pitchMacroMin, self.pitchMacroMax = newMin, newMax
			self.createPitchMacroList()
		self.display('PITCH_min', self.pitchMacroMin)
		self.display('PITCH_max', self.pitchMacroMax)

	# 		PITCHMICRO

	def changePitchMicroMin(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMinimum(amount, self.pitchMicroMin, self.pitchMicroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if new != self.pitchMicroMin:
			self.pitchMicroMin = new
			self.createPitchMicroList()
		self.display('pitch_min', self.pitchMicroMin)

	def changePitchMicroMax(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMaximum(amount, self.pitchMicroMin, self.pitchMicroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if new != self.pitchMicroMax:
			self.pitchMicroMax = new
			self.createPitchMicroList()
		self.display('pitch_max', self.pitchMicroMax)

	def changePitchMicroMid(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromMiddle(amount, self.pitchMicroMin, self.pitchMicroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if newMin != self.pitchMicroMin:
			self.pitchMicroMin, self.pitchMicroMax = newMin, newMax
			self.createPitchMicroList()
		self.display('pitch_min', self.pitchMicroMin)
		self.display('pitch_max', self.pitchMicroMax)

	def changePitchMicroSpread(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromSpread(amount, self.pitchMicroMin, self.pitchMicroMax, constants.PITCH_MIN, constants.PITCH_MAX)
		if newMin != self.pitchMicroMin or newMax != self.pitchMicroMax:
			self.pitchMicroMin, self.pitchMicroMax = newMin, newMax
			self.createPitchMacroList()
		self.display('pitch_min', self.pitchMicroMin)
		self.display('pitch_max', self.pitchMicroMax)

	# 		VOLUME

	def changeVolumeMin(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMinimum(amount, self.volumeMin, self.volumeMax, 0, 1)
		if new != self.volumeMin:
			self.volumeMin = new
			self.createVolumeList()
		self.display('volume_min', self.volumeMin)

	def changeVolumeMax(self, amount):
		amount /= constants.KNOB_DIV
		new = mafs.newMaximum(amount, self.volumeMin, self.volumeMax, 0, 1)
		if new != self.volumeMax:
			self.volumeMax = new
			self.createVolumeList()
		self.display('volume_max', self.volumeMax)

	def changeVolumeMid(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromMiddle(amount, self.volumeMin, self.volumeMax, 0, 1)
		if newMin != self.volumeMin:
			self.volumeMin, self.volumeMax = newMin, newMax
			self.createPanList()
		self.display('volume_min', self.volumeMin)
		self.display('volume_max', self.volumeMax)

	def changeVolumeSpread(self, amount):
		amount /= constants.KNOB_DIV
		newMin, newMax = mafs.newFromSpread(amount, self.volumeMin, self.volumeMax, 0, 1)
		if newMin != self.volumeMin or newMax != self.volumeMin:
			self.volumeMin, self.volumeMax = newMin, newMax
			self.createPanList()
		self.display('volume_min', self.volumeMin)
		self.display('volume_max', self.volumeMax)

	# 	FORCE RESPOND ONCE
	def doForceRespondAudibleOnce(self):
		self.forceRespondAudibleOnce = 1
		self.display('sv1_audible')

	def doForceRespondDirectionOnce(self):
		self.forceRespondDirectionOnce = 1
		self.display('sv1_direction')

	def doForceRespondEndarOnce(self):
		self.forceRespondEndarOnce = 1
		self.display('sv1_endar')

	def doForceRespondLengthOnce(self):
		self.forceRespondLengthOnce = 1
		self.display('sv1_lengd')

	def doForceRespondPanOnce(self):
		self.forceRespondPanOnce = 1
		self.display('sv1_pönnukaka')

	def doForceRespondPitchMacroOnce(self):
		self.forceRespondPitchMacroOnce = 1
		self.display('sv1_PITCH')

	def doForceRespondPitchMicroOnce(self):
		self.forceRespondPitchMicroOnce = 1
		self.display('sv1_pitch')

	def doForceRespondStartPointOnce(self):
		self.forceRespondStartPointOnce = 1
		self.display('sv1_startpoint')

	def doForceRespondVolumeOnce(self):
		self.forceRespondVolumeOnce = 1
		self.display('sv1_volume')

	# RESPOND TO TRIGGER

	def respondToTrigger(self):

		# ITERATE INDICES
		'''
		INDICES: WHAT ARE THEY?
		i = main index, gets reset by freeze
		iMobile = mobile index, always moves, for cases where we want independence (like response)
		'''
		# main index
		if not self.freeze:
			self.i = mafs.iterate(self.i, constants.VARIABLES_LIST_LENGTH - 1)
		elif self.freeze:
			# if freezing, iterate forward or jump back to the freeze reset
			self.freezeCounter += 1
			if self.freezeCounter > self.freezeLength:
				self.freezeCounter = 1
				self.i = self.freezeResetIndex
			else:
				self.i = mafs.iterate(self.i, constants.VARIABLES_LIST_LENGTH - 1)
		# mobile index
		self.iMobile = mafs.iterate(self.iMobile, constants.VARIABLES_LIST_LENGTH - 1)

		# STOP ENDING BITAR
		# endingBitar are no longer in activeBitar so need stopping explicitly
		if self.endingBitar:
			for i in self.endingBitar:
				self.bitar[i][self.be[i]].stop()
			# reset endingBitar for use next time
			self.endingBitar = []

		
		# end active ones that are globally responsive
		'''for i in range(self.noOfActiveBitar):
			if self.globalResponseList[i][self.iMobile]:
				self.bitar[i][self.be[i]].stop()'''

		# WORK ON RESPONSIVE BITAR
		'''
		fuller explanation of these:
		for active ones, if responding:
			if this biti is responsive from responseList at response index OR forced to respond:
				for the biti's specific endar, change from list at index
		'''
		for i in range(self.noOfActiveBitar):
			if self.globalResponseList[i][self.iMobile]:
				
				# STOP TO APPLY CHANGES
				self.bitar[i][self.be[i]].stop()

				# IF AUDIBLE, DO SOMETHING, OTHERWISE DON'T BOTHER
				if self.audibleResponseList[i][self.iMobile] or self.forceRespondAudibleOnce:
					if self.audibleList[i][self.i]:

						# update endar first, as this is which audio objects to update throughout
						if self.endarResponseList[i][self.iMobile] or self.forceRespondEndarOnce:
							# apply endar to tracker
							self.be[i] = self.endarList[i][self.i]

						'''
						for each:
							- if responsive, proceed
							- if the new value is different, proceed with making a change
						'''
						# update startPoint
						if self.startPointResponseList[i][self.iMobile] or self.forceRespondStartPointOnce:
							if self.startPointIndices[i][self.i] == 0:
								self.bitar[i][self.be[i]].changeStartPoint(self.newStartPoint(0))
							else:
								if self.bitar[i][self.be[i]].startPoint != self.startPointList[i][self.i]:
									self.bitar[i][self.be[i]].changeStartPoint(self.startPointList[i][self.i])

						# update direction
						if self.directionResponseList[i][self.iMobile] or self.forceRespondDirectionOnce:
							if self.bitar[i][self.be[i]].direction != self.directionList[i][self.i]:
								self.bitar[i][self.be[i]].changeDirection(self.directionList[i][self.i])
						
						# update length
						if self.lengthResponseList[i][self.iMobile] or self.forceRespondLengthOnce:
							if self.bitar[i][self.be[i]].length != self.lengthList[i][self.i]:
								self.bitar[i][self.be[i]].changeLength(self.lengthList[i][self.i])

						# update pan
						if self.panResponseList[i][self.iMobile] or self.forceRespondPanOnce:
							if self.bitar[i][self.be[i]].pan != self.panList[i][self.i]:
								self.bitar[i][self.be[i]].changePan(self.panList[i][self.i])

						# update volume
						if self.volumeResponseList[i][self.iMobile] or self.forceRespondVolumeOnce:
							if self.bitar[i][self.be[i]].volume != self.volumeList[i][self.i]:
								self.bitar[i][self.be[i]].changeVolume(self.volumeList[i][self.i])

						# update pitchMacro
						if self.pitchMacroResponseList[i][self.iMobile] or self.forceRespondPitchMacroOnce:
							if self.bitar[i][self.be[i]].pitchMacro != self.pitchMacroList[i][self.i]:
								self.bitar[i][self.be[i]].changePitchMacro(self.pitchMacroList[i][self.i])

						# update pitchMicro
						if self.pitchMicroResponseList[i][self.iMobile] or self.forceRespondPitchMicroOnce:
							if self.bitar[i][self.be[i]].pitchMicro != self.pitchMicroList[i][self.i]:
								self.bitar[i][self.be[i]].changePitchMicro(self.pitchMicroList[i][self.i])
						
						# PLAY
						self.bitar[i][self.be[i]].play()

		'''
		# PLAY
		for i in range(self.noOfActiveBitar):
			if self.globalResponseList[i][self.i]:
				self.bitar[i][self.be[i]].play()'''
		
		self.resetForceRespondOnce()