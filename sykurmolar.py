'''
on computer:
	- must run prestart then jack_start manually before script. þetta reddast
on raspberry pi:
	- add prestart (done as sudo) and jack_start (done as normal user) to processes when booting

IMPORTS
'''
# local imports
import constants, midi, midiToFunction, moli, triggers
# external imports
import pyo64 as pyo
import sys, os, shutil, random
from time import strftime

'''
SETUP
'''

'''
if len(sys.argv) < 2:
	raise RuntimeError("Must run with argument 0 or 1 (shell & jack externally VS attempted in-script)")

if str(sys.argv[1]) == '1':
	
	# run shell script
	audioEnvironmentSetup = subprocess.call(['sh', './prestart.sh'])
	if audioEnvironmentSetup != 0:
		raise RuntimeError("Must run this in sudo otherwise audio environment fails")
	# start jack'''

'''
PYO SERVER SETUP
'''

pyoServer = pyo.Server(nchnls=2, ichnls=constants.INPUT_CHANNELS, audio='jack')
#pyoServer.setInOutDevice(3)
#pyo.pa_list_devices()
pyoServer.boot()
pyoServer.start()

'''
AUDIO STREAM
'''
audioTable = pyo.DataTable(constants.AUDIO_TABLE_DURATION_SAMPLES, chnls=2)

'''
RECORDING
'''
currentRecordingNumber = 0
recording = False

def record():
	global recording, currentRecordingNumber
	if not recording:
		recording = True
		recordStart()
		print('record start')
		# send to LEDs
		midiHandler.sendButtonLEDColor('b_TR3_RECORD', 'ON')
	else:
		recording = False
		recordStop()
		currentRecordingNumber += 1
		print('record stop')
		# send to LEDs
		midiHandler.sendButtonLEDColor('b_TR3_RECORD', 'OFF')

def recordStart():
	newFileName = str(constants.RECORDED_FILE_DESTINATION_TEMP + constants.RECORDED_FILE_PREFIX + '_' + str(currentRecordingNumber) + '.wav')
	pyoServer.recordOptions(filename = newFileName)
	pyoServer.recstart()

def recordStop():
	pyoServer.recstop()

def moveRecordings():
	recordedFiles = os.listdir(constants.RECORDED_FILE_DESTINATION_TEMP)
	for file in recordedFiles:
		if file.endswith('wav'):
			shutil.move(os.path.join(constants.RECORDED_FILE_DESTINATION_TEMP, file), os.path.join(constants.RECORDED_FILE_DESTINATION_FINAL, file))


'''
SAMPLE COUNTER
'''
sampleCounterInitTrigger = pyo.Trig() # use .play() to start count
sampleCounter = pyo.Count(sampleCounterInitTrigger)

'''
LINE IN
'''

# select lineIn audio by mono or stereo
if constants.INPUT_CHANNELS == 1:
	lineInAudio = pyo.Input(0)
	lineInAudioOut = pyo.Input(0)
elif constants.INPUT_CHANNELS == 2:
	lineInAudio = pyo.Input([0,1]).mix()
	lineInAudioOut = pyo.Input([0,1]).mix()

lineInVolPortamento = pyo.SigTo(0, time=constants.PORTAMENTO_TRANSITION_SECONDS, init=0)
lineInAudioOut.mul = lineInVolPortamento

# old version: lineInAudioOutPan = pyo.SPan(lineInAudioOut).out() # CHANGE THIS TO PAN, SET A PAN TO BE A SIGTO, FN TO CHANGE THE SIGTO
lineInPanPortamento = pyo.SigTo(0.5, constants.PORTAMENTO_TRANSITION_SECONDS, init = 0.5)
lineInAudioOutPan = pyo.Pan(lineInAudioOut, pan = lineInPanPortamento).out()

lineInMuted = True
lineInBeenHeard = False

def lineInMute():
	global lineInMuted, lineInBeenHeard, lineInVolPortamento
	if not lineInMuted:
		print('muted')
		lineInVolPortamento.value = 0
		lineInMuted = True
		# send to LED
		midiHandler.sendButtonLEDColor('b_TRACK8_4', 'OFF')
	else:
		print('unmuted')
		lineInVolPortamento.value = 1
		lineInMuted = False
		lineInBeenHeard = True
		# send to LED
		midiHandler.sendButtonLEDColor('b_TRACK8_4', 'ON')

# NEW
def lineInChangePan(newValue):
	lineInPanPortamento.value = newValue

# send lineInAudio to audioTable
# uses the same trigger as sampleCounter
lineInAudioToAudioTable = pyo.TrigTableRec(lineInAudio, sampleCounterInitTrigger, audioTable)


'''
TRIGGERS - CREATION
'''

# allTriggers length = 33
# each trigger in allTriggers has an outputTrigger that can be listened to
# each trigger has as name
ammæli = (triggers.Ammæli(3, sampleCounter, name='a0'), triggers.Ammæli(8, sampleCounter, name='a1'))

allTriggers = (
	# singles (indices 0-7)
	triggers.No(),
	triggers.Manual(),
	ammæli[0].t_SimpleLoop, # 2
	ammæli[0].t_Swung,
	ammæli[0].t_Combine,
	ammæli[1].t_SimpleLoop, # 5
	ammæli[1].t_Swung,
	ammæli[1].t_Combine,
	# groupings of 5
	# indices 8-12
	triggers.Random(20, name='snigill4'), triggers.Random(7, name='snigill3'), triggers.Random(2, name='snigill2'), triggers.Random(0.4, name='snigill1'), triggers.Random(0.1, name='snigill0'),
	# 13-17
	ammæli[0].t_PrimesLong[0], ammæli[0].t_PrimesLong[1], ammæli[0].t_PrimesLong[2], ammæli[0].t_PrimesLong[3], ammæli[0].t_PrimesLong[4],
	# 18-22
	ammæli[0].t_PrimesShort[0], ammæli[0].t_PrimesShort[1], ammæli[0].t_PrimesShort[2], ammæli[0].t_PrimesShort[3], ammæli[0].t_PrimesShort[4],
	# 23-27
	ammæli[1].t_PrimesLong[0], ammæli[1].t_PrimesLong[1], ammæli[1].t_PrimesLong[2], ammæli[1].t_PrimesLong[3], ammæli[1].t_PrimesLong[4],
	# 28-32
	ammæli[1].t_PrimesShort[0], ammæli[1].t_PrimesShort[1], ammæli[1].t_PrimesShort[2], ammæli[1].t_PrimesShort[3], ammæli[1].t_PrimesShort[4]
)


'''
LINEIN RANGE FOR STARTPOINTS
'''
lineInRange = constants.LINE_IN_LOOKBACK_RANGE_MIN_SAMPLES

def updateLineInRange(new):
	global lineInRange
	# new = value from 0 to 1
	# invert new so it's a simple exponent
	# raise to the power of new, then add to min
	new = 1 - new
	exponent = int(constants.AUDIO_TABLE_DURATION_SAMPLES ** new)
	lineInRange = constants.LINE_IN_LOOKBACK_RANGE_MIN_SAMPLES + exponent

'''
STARTPOINTS
'''

class StartPoint():
	
	def __init__(self, typeOfStartPoint):
		self.startPositionSamples = 0
		if typeOfStartPoint == 'lineIn':
			self.lineInUpdate = pyo.Pattern(self.updateLineIn, time = constants.START_POINT_UPDATE_FREQUENCY_SECONDS
		)
			self.lineInUpdateTrigger = pyo.TrigFunc(sampleCounterInitTrigger, self.lineInUpdate.play)
		elif typeOfStartPoint == 'HFF':
			self.HFFUpdate = pyo.Pattern(self.updateHFF, time = constants.START_POINT_UPDATE_FREQUENCY_SECONDS
		)
			self.BankingCollapse = pyo.TrigFunc(sampleCounterInitTrigger, self.HFFUpdate.play)

	def updateLineIn(self):
		now = int(sampleCounter.get())
		lineMin = max(now - lineInRange, 1)
		lineMax = max(now - constants.LINE_IN_LOOKBACK_RANGE_MIN_SAMPLES, 1)
		self.startPositionSamples = random.randint(lineMin, lineMax)

	def updateHFF(self):
		self.startPositionSamples = random.randint(0, int(sampleCounter.get()))

	def updateToNow(self):
		# gets called by buttons to define now as new startpoint
		self.startPositionSamples = int(sampleCounter.get())
		
# create StartPoints, 0 = lineIn, 1 = helvítis fokking fokk, remainder = manual
allStartPoints = [StartPoint('lineIn'), StartPoint('HFF')]
for i in range(constants.NUMBER_OF_START_POINTS):
	allStartPoints.append(StartPoint(None))
allStartPoints = tuple(allStartPoints)

'''
SYKURMOLAR - CREATE, SELECT
'''
allSykurmolar = [moli.Sykurmoli(str(i), constants.SAMPLE_RATE, constants.BITAR_PER_SYKURMOLI, allTriggers, allStartPoints, audioTable) for i in range(constants.NUMBER_OF_SYKURMOLAR)]
allSykurmolar = tuple(allSykurmolar)
selectedSykurmolar = []

def changeSelectedSykurmolar(number):
	# select if deselected, vice versa
	# numbers start from 0
	global selectedSykurmolar # necessary?
	try:
		selectedSykurmolar.remove(number)
	except:
		selectedSykurmolar.append(number)
		selectedSykurmolar.sort()
	# send this to LEDs. result: LEDsArray is e.g. 1,0,0,0 if 0 is selected
	LEDsArray = [0 for i in range(constants.NUMBER_OF_SYKURMOLAR)]
	for i in selectedSykurmolar:
		LEDsArray[i] = 1
	midiHandler.setLEDBlockArray('selectedSykurmolar', LEDsArray, ('OFF', 'ON'))

'''
SHIFT FUNCTIONS
'''
moliKnobOptions_INDEX = 2

def moliKnobOptions_CHANGE(newIndex):
	# receives an index 0-5
 	# knob options = max, min, bias, changes
	global moliKnobOptions_INDEX
	moliKnobOptions_INDEX = newIndex
	# send this to LEDs. result: LEDsArray is e.g. 1,0,0,0 if index=0
	LEDsArray = [0 for i in range(6)]
	LEDsArray[moliKnobOptions_INDEX] = 1
	midiHandler.setLEDBlockArray('moliKnobOptions', LEDsArray, ('OFF', 'PINK_C'))

triggerKnobOptions_INDEX = None
triggerKnobOptions_NAMES = ('simple', 'swung', 'combine')

def triggerKnobOptions_CHANGE(newIndex):
	# receives 0-2 for SimpleLoop, Swung, Combine
	# these stick, and by default are at 0
	global triggerKnobOptions_INDEX
	triggerKnobOptions_INDEX = newIndex
	print('trigger knob controls: ' + triggerKnobOptions_NAMES[triggerKnobOptions_INDEX])

forceRespondOnce_TOGGLE = False

def forceRespondOnce_SHIFTDOWN():
	global forceRespondOnce_TOGGLE
	forceRespondOnce_TOGGLE = True
	print('force respond: ', forceRespondOnce_TOGGLE)

def forceRespondOnce_SHIFTUP():
	global forceRespondOnce_TOGGLE
	forceRespondOnce_TOGGLE = False
	print('force respond: ', forceRespondOnce_TOGGLE)

jumpToLimit_TOGGLE = False

def jumpToLimit_SHIFTDOWN():
	global jumpToLimit_TOGGLE
	jumpToLimit_TOGGLE = True

def jumpToLimit_SHIFTUP():
	global jumpToLimit_TOGGLE
	jumpToLimit_TOGGLE = False


'''
MIDI INTERACTION

executeFromMidiIn is the command executed when midi signal is received
where to store the LED function calls?
	if a function happens, give an LED block a value to work with
'''

nextLEDFunctionName = None

def executeFromMidiIn(data1, data2):
	global nextLEDFunctionName
	# data1 received is ([list,of,midivalues], deltatime); data2 received = None
	midiValues = data1[0]
	# pass clarifyMidiIn the data and see if we get a response or an error
	try:
		peripheralType, peripheralName, newValue = midi.clarifyMidiIn(midiValues)
		# we don't yet have a use for peripheraltype
	except:
		return
	# normal - just execute the function
	if peripheralName in midiToFunction.normal:
		executeFunctionNormal(midiToFunction.normal[peripheralName], newValue)
		#nextLEDFunctionName = midiToFunction.normal[peripheralName]
	# sykurmola - execute the function to all sykurMola
	elif peripheralName in midiToFunction.sykurmola:
		executeFunctionToSelectedSykurmolar(midiToFunction.sykurmola[peripheralName], newValue)
	# sykurmola ambiguous - execute the disambiguated function to all sykurMola
	elif peripheralName in midiToFunction.sykurmolaAmbiguous:
		disambiguateSykurmolaAmbiguousFunction(midiToFunction.sykurmolaAmbiguous[peripheralName], newValue)
	# sykurmola specific - execute the function to the specific provided sykurmoli (for the track buttons)
	elif peripheralName in midiToFunction.sykurmolaSpecific:
		executeFunctionToSpecificSykurmoli(midiToFunction.sykurmolaSpecific[peripheralName])
	# sykurmola specific fader - execute the function to the specific provided sykurmoli
	# these function names are getting a bit out of hand
	elif peripheralName in midiToFunction.sykurmolaSpecificFader:
		executeFunctionToSpecificSykurmoliFader(midiToFunction.sykurmolaSpecificFader[peripheralName], newValue)
	# trigger - execute the function to the ammæli
	elif peripheralName in midiToFunction.trigger:
		executeTriggerFunction(midiToFunction.trigger[peripheralName])
	# trigger ambiguous - execute the disambiguated function to the ammæli
	elif peripheralName in midiToFunction.triggerAmbiguous:
		disambiguateTriggerFunction(midiToFunction.triggerAmbiguous[peripheralName], newValue)
	# start point
	elif peripheralName in midiToFunction.startPoint:
		executeFunctionUpdateStartPoint(midiToFunction.startPoint[peripheralName])
	
def executeFunctionNormal(functionData, newValue):
	# if functionData is a string, execute this with or without newValue
	if type(functionData) is str:
		# do not pass newValue if its value is explicitly None
		if newValue == None:
			globals()[functionData]()
		else:
			globals()[functionData](newValue)
	elif type(functionData) is tuple:
		f, d = functionData
		globals()[str(f)](d)

def executeFunctionToSelectedSykurmolar(functionData, newValue):
	# if functionData is a string (so it's a single value), execute this with or without newValue
	if type(functionData) is str:
		# do not pass newValue if its value is explicitly None
		if newValue == None:
			for moli in selectedSykurmolar:
				getattr(allSykurmolar[moli], str(functionData))()
		else:
			# pass newValue. NEW: jumpToLimit_TOGGLE if statement
			if jumpToLimit_TOGGLE:
				newValue *= 100
			for moli in selectedSykurmolar:
				getattr(allSykurmolar[moli], str(functionData))(newValue)
	elif type(functionData) is tuple:
		f, d = functionData
		for moli in selectedSykurmolar:
			getattr(allSykurmolar[moli], str(f))(d)

def executeFunctionToSpecificSykurmoli(functionsTuple):
	sykurmoliNumber, functionName, newValue = functionsTuple
	if newValue != None:
		getattr(allSykurmolar[sykurmoliNumber], str(functionName))(newValue)
	else:
		getattr(allSykurmolar[sykurmoliNumber], str(functionName))()

def executeFunctionToSpecificSykurmoliFader(functionsTuple, newValue):
	sykurmoliNumber, functionName = functionsTuple
	getattr(allSykurmolar[sykurmoliNumber], str(functionName))(newValue)

def executeFunctionUpdateStartPoint(startPointNumber):
	getattr(allStartPoints[startPointNumber], str('updateToNow'))()

def executeTriggerFunction(functionsTuple):
	ammæliNumber, functionName = functionsTuple
	getattr(ammæli[ammæliNumber], str(functionName))()

def disambiguateSykurmolaAmbiguousFunction(functionsTuple, newValue):
	'''
	this receives a tuple from the dictionary in the following format:
	((max, min, spread, mid, bias, response), forceRespondOnce_TOGGLE)
	the first is a tuple of functions to execute dependent on moliKnobOptions_INDEX
		if a value is None, ignore
	the second is a function to execute if forceRespondOnce_TOGGLE is True
	this assumes we always have something in forceRespondOnce_TOGGLE
	'''
	mmbc, f = functionsTuple
	if forceRespondOnce_TOGGLE:
		executeFunctionNormal(f, None)
	else:
		if mmbc[moliKnobOptions_INDEX]:
			executeFunctionToSelectedSykurmolar(mmbc[moliKnobOptions_INDEX], newValue)
		
def disambiguateTriggerFunction(functionsData, newValue):
	'''
	this receives a tuple of the knob options to execute dependent on triggerKnobOptions_INDEX
	triggerKnobOptions will be None if the selection button is not held
	'''
	ammæliNumber, functionsTuple = functionsData
	if triggerKnobOptions_INDEX != None:
		getattr(ammæli[ammæliNumber], str(functionsTuple[triggerKnobOptions_INDEX]))(newValue)

'''
FULL INFO DISPLAY
'''
def displayFull():
	diskspaceRemaining = int(shutil.disk_usage("/").free/1000000)
	# clean
	print('-------------------')
	# time elapsed, basic info
	print('time:{0}/{1}m rec:{2} disk:{3}mb muted:{4}'.format(
		int(sampleCounter.get()/constants.SAMPLE_RATE/60), constants.PROGRAM_DURATION_MINUTES, recording, diskspaceRemaining, lineInMuted
	))
	# ammæli durations
	print('trigs {0}:{1}s {2}:{3}s'.format(
		ammæli[0].name, ammæli[0].duration, ammæli[1].name, ammæli[1].duration
	))
	# display full for each moli selected
	for moli in selectedSykurmolar:
		allSykurmolar[moli].displayFull()

'''
CLEAN UP WHEN WE END THE PROGRAM
'''
programEnd = False

def endProgram():
	# mute lineIn
	if not lineInMuted:
		lineInMute()
	# stop all Sykurmolar
	for moli in allSykurmolar:
		moli.stop()
	# end and move recordings
	recordStop()
	moveRecordings()
	# end audio server
	pyoServer.shutdown()
	# end midi controller
	midiHandler.end()
	# end program loop
	global programEnd
	programEnd = True
	# end program
	os._exit(0)

def e():
	# shortcut for debugging
	endProgram()

'''
START PROGRAM
'''
midiHandler = midi.MidiHandler(executeFromMidiIn)
midiHandler.startLEDs()
changeSelectedSykurmolar(0)
moliKnobOptions_CHANGE(4)
triggerKnobOptions_CHANGE(0)
sampleCounterInitTrigger.play()