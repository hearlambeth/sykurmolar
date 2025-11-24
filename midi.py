'''
midi controller setup
'''

import rtmidi
from time import sleep
import sys

'''
LEDs
'''

LED_CHANNEL_BASE_BUTTON = 0x90
LED_CHANNEL_BASE_KNOB = 0xB0

LEDColors = {
	'OFF': 0,
	'ON': 1,
	'ON2': 2,
	'BLACK': 0,
	'WHITE_A': 1,
	'WHITE_B': 2,
	'WHITE_C': 3,
	'PINK_A': 56,
	'PINK_B': 57,
	'PINK_C': 58,
	'GREEN_A': 32,
	'GREEN_B': 33,
	'GREEN_C': 34,
	'FALL_A': 124,
	'FALL_B': 126,
	'FALL_C': 127,
	'FALL_D': 125,
	'YELLOW_A': 73,
	'YELLOW_B': 74,
	'YELLOW_C': 75
}

LEDKnobModes = {
	# see p26 of APC docs. currently no need for these knob LEDs.
	'OFF': 0
}

'''
LED BLOCKS
blocks of LEDs to be turned off/on. these are buttons. if i use knobs LEDs i need to add a dictionary for these.

which blocks are used to show what:
for base colors (fallback):
	triggers_, freeze, startPoints, knobMode, lineInMute
for indicating floats and integers:
	moli_Column5,6
	
in case of receiving arrays, LEDBlocks are in the order they are supposed to receive arrays. so moli_column goes from bottom to top.
'''

LEDBlocks = {
	'triggersLooping': ('b_GRID_A1', 'b_GRID_A2', 'b_GRID_A3', 'b_GRID_A4', 'b_GRID_B1', 'b_GRID_B2', 'b_GRID_B3', 'b_GRID_B4'),
	'triggersSequenceTap': ('b_GRID_C1', 'b_GRID_C2', 'b_GRID_D1', 'b_GRID_D2', 'b_GRID_E1', 'b_GRID_E2'),
	'triggersNya': ('b_GRID_C3', 'b_GRID_F1', 'b_GRID_F2', 'b_GRID_F3', 'b_GRID_F4'),
	'triggersNei': ('b_GRID_C4'),
	'triggersRandom': ('b_GRID_D3', 'b_GRID_D4', 'b_GRID_E3', 'b_GRID_E4'),
	'freeze': ('b_GRID_A6', 'b_GRID_A7', 'b_GRID_B6'),
	'startPoints': ('b_GRID_F5', 'b_GRID_F6', 'b_GRID_F7', 'b_GRID_F8', 'b_GRID_G5', 'b_GRID_G6', 'b_GRID_G7', 'b_GRID_G8', 'b_GRID_G9'),
	'moliKnobOptions': ('b_GRID_A9', 'b_GRID_B9', 'b_GRID_A8', 'b_GRID_B8', 'b_GRID_C9', 'b_GRID_D9'),
	'lineInMute': ('b_GRID_F9'),
	'moli1Column5': ('b_GRID_E1', 'b_GRID_D1', 'b_GRID_C1', 'b_GRID_B1', 'b_GRID_A1'),
	'moli2Column5': ('b_GRID_E2', 'b_GRID_D2', 'b_GRID_C2', 'b_GRID_B2', 'b_GRID_A2'),
	'moli3Column5': ('b_GRID_E3', 'b_GRID_D3', 'b_GRID_C3', 'b_GRID_B3', 'b_GRID_A3'),
	'moli4Column5': ('b_GRID_E4', 'b_GRID_D4', 'b_GRID_C4', 'b_GRID_B4', 'b_GRID_A4'),
	'moli1Column6': ('b_GRID_F1', 'b_GRID_E1', 'b_GRID_D1', 'b_GRID_C1', 'b_GRID_B1', 'b_GRID_A1'),
	'moli2Column6': ('b_GRID_F1', 'b_GRID_E2', 'b_GRID_D2', 'b_GRID_C2', 'b_GRID_B2', 'b_GRID_A2'),
	'moli3Column6': ('b_GRID_F1', 'b_GRID_E3', 'b_GRID_D3', 'b_GRID_C3', 'b_GRID_B3', 'b_GRID_A3'),
	'moli4Column6': ('b_GRID_F1', 'b_GRID_E4', 'b_GRID_D4', 'b_GRID_C4', 'b_GRID_B4', 'b_GRID_A4'),
	'mainGrid': (
		'b_GRID_A1', 'b_GRID_A2', 'b_GRID_A3', 'b_GRID_A4', 'b_GRID_A5', 'b_GRID_A6', 'b_GRID_A7', 'b_GRID_A8',
		'b_GRID_B1', 'b_GRID_B2', 'b_GRID_B3', 'b_GRID_B4', 'b_GRID_B5', 'b_GRID_B6', 'b_GRID_B7', 'b_GRID_B8',
		'b_GRID_C1', 'b_GRID_C2', 'b_GRID_C3', 'b_GRID_C4', 'b_GRID_C5', 'b_GRID_C6', 'b_GRID_C7', 'b_GRID_C8',
		'b_GRID_D1', 'b_GRID_D2', 'b_GRID_D3', 'b_GRID_D4', 'b_GRID_D5', 'b_GRID_D6', 'b_GRID_D7', 'b_GRID_D8'),
	'inuse_RGB': (
		'b_GRID_A1', 'b_GRID_A3', 'b_GRID_A4', 'b_GRID_A5', 'b_GRID_A9',
		'b_GRID_B1', 'b_GRID_B2', 'b_GRID_B3', 'b_GRID_B4', 'b_GRID_B5', 'b_GRID_B7', 'b_GRID_B9',
		'b_GRID_C1', 'b_GRID_C2', 'b_GRID_C3', 'b_GRID_C4', 'b_GRID_C5', 'b_GRID_C7', 'b_GRID_C9',
		'b_GRID_D1', 'b_GRID_D3', 'b_GRID_D4', 'b_GRID_D5', 'b_GRID_D7', 'b_GRID_D9',
		'b_GRID_E1', 'b_GRID_E2', 'b_GRID_E3', 'b_GRID_E4', 'b_GRID_E5', 'b_GRID_E7', 'b_GRID_E9'
	),
	'inuse_MONO': (
		'b_GRID_F5', 'b_GRID_F6', 'b_GRID_F7', 'b_GRID_F8', 'b_GRID_F9',
		'b_GRID_G5', 'b_GRID_G6', 'b_GRID_G7', 'b_GRID_G8', 'b_GRID_G9',
		'b_TRACK1_1', 'b_TRACK1_2', 'b_TRACK1_3', 'b_TRACK1_4', 
		'b_TRACK2_1', 'b_TRACK2_2', 'b_TRACK2_3', 'b_TRACK2_4', 
		'b_TRACK3_1', 'b_TRACK3_2', 'b_TRACK3_3', 'b_TRACK3_4', 
		'b_TRACK4_1', 'b_TRACK4_2', 'b_TRACK4_3', 'b_TRACK4_4'
	),
	'selectedSykurmolar': ('b_GRID_G1', 'b_GRID_G2', 'b_GRID_G3', 'b_GRID_G4')
}

'''
MIDIHANDLER class
class to handle incoming and outgoing midi signals
'''

class MidiHandler():

	def __init__(self, callbackFunctionName):
		self.callbackFunctionName = callbackFunctionName
		self.midiIn = rtmidi.MidiIn()
		self.midiOut = rtmidi.MidiOut()
		# find and open correct midi ports
		try:
			self.midiIn.open_port(
				[i for i, s in enumerate(self.midiIn.get_ports()) if 'APC40' in s][0])
		except:
			raise ConnectionError('MidiHandler: Error finding MIDI port in (check that APC40 is connected. Ports found: ' + str(self.midiIn.get_ports()))
		try:
			self.midiOut.open_port(
				[i for i, s in enumerate(self.midiOut.get_ports()) if 'APC40' in s][0])
		except:
			raise ConnectionError('MidiHandler: Error finding MIDI port out (check that APC40 is connected. Ports found: ' + str(self.midiOut.get_ports()))           
		self.startCallBackThread()
		# sysex message to control LEDs myself = 0x42
		self.midiOut.send_message([0xF0,0x47,0x00,0x29,0x60,0x00,0x04,0x42,0x00,0x00,0x00,0xF7])
		# allow to receive sysex messages
		self.midiIn.ignore_types(sysex=False)
		# create the program loop if necessary
		'''if __name__ == "__main__":
			self.programEnd = 0
			while not self.programEnd:
				pass
				sleep(1)'''
	
	def startCallBackThread(self):
		# create callback thread to receive midi (this is always running)
		# this being in place from the beginning MAY stop the error "MidiInAlsa: message queue limit reached",
		# as callback thread stops the messages from going to the queue
		# see http://www.music.mcgill.ca/~gary/rtmidi/
		self.midiIn.set_callback(self.callbackFunctionName)
	
	def startLEDs(self):
		# turn knob, button LEDs off
		self.offAllKnobLEDs()
		self.offAllButtonLEDs()
		# set the fallback colors
		self.setLEDBlockUniform('inuse_RGB', 'PINK_A')
		self.setLEDBlockUniform('inuse_MONO', 'ON')
	
	def end(self):
		# turn off all button LEDs - this takes a second
		self.offAllButtonLEDs()
		# terminate midi connections
		self.midiIn.close_port()
		self.midiOut.close_port()
		self.midiIn.delete()
		self.midiOut.delete()
		if __name__ == "__main__":
			self.programEnd = 1
			sys.exit()

	def sendLEDMessage(self, name, status):
		for x in buttons:
			if x.name == name:
				if status == "on":
					self.midiOut.send_message(x.setLEDOn())
				elif status == "off":
					self.midiOut.send_message(x.setLEDOff())

	def sendButtonLEDColor(self, buttonName, colorName):
		for button in buttons:
			if button.name == buttonName:
				self.midiOut.send_message(button.setLEDColor(colorName))

	def offAllButtonLEDs(self):
		for button in buttons:
			self.midiOut.send_message(button.setLEDOff())

	def offAllKnobLEDs(self):
		for knob in knobs:
			self.midiOut.send_message(knob.setLEDOff())

	def setLEDBlockUniform(self, blockName, colorName):
		for LED in LEDBlocks[blockName]:
			self.sendButtonLEDColor(LED, colorName)

	def setLEDBlockArray(self, blockName, colorNumbersArray, colorNamesArray):
		'''
		receives
			blockName: name of the block, as stored in LEDBlocks
			colorNumbersArray: for each LED in the block, index within colorNamesArray
			colorNamesArray: names of colors to use, referred to as indices by colorNumbersArray
			example: 'freeze', (0,0,1), ('WHITE_A', 'WHITE_C')
		'''
		blockArray = LEDBlocks[blockName]
		for i in range(len(blockArray)):
			self.sendButtonLEDColor(blockArray[i], colorNamesArray[colorNumbersArray[i]])


def clarifyMidiIn(data1):
	# identify matching button/knob/fader
	# Locations.index returns the index where the location is first found
	# this is then given to the button/knob/fader
	# TO IDENTIFY NOTES:
	#print(data1)
	try:
		i = knobLocations.index([data1[0], data1[1]])
		update = knobs[i].updateValue(data1[2])
		if update[0]:
			# return only if scale condition of updateValue is met
			# update[i] = the change
			return 'knob', knobs[i].name, update[1]
	except:
		pass
	try:
		i = buttonLocations.index(data1)
		# buttons explicitly return None
		return 'button', buttons[i].name, None
	except:
		pass
	try:
		i = faderLocations.index([data1[0], data1[1]])
		return 'fader', faders[i].name, faders[i].updateValue(data1[2])
	except:
		pass 

'''
buttons, knobs, faders - what I am calling peripherals

'''

class Button():
		
	def __init__(self, name, location):
		self.name = name
		self.location = location
		# interpret LED output values
		self.LEDChannel = int(LED_CHANNEL_BASE_BUTTON + (self.location[0] - 144))
		self.LEDLocation = int(self.location[1])

	def interact(self):
		print(self.name)

	def setLEDColor(self, colorName):
		return self.LEDChannel, self.LEDLocation, LEDColors[colorName]
	
	def setLEDOff(self):
		return self.LEDChannel, self.LEDLocation, LEDColors['OFF']


class Knob():

	def __init__(self, name, location, isAbsolute=True, scale=1):
		self.name = name
		self.location = location
		self.isAbsolute = isAbsolute
		self.scale = scale
		self.currentValue = self._initValue()
		self.scaleProgress = 0
		# derive LED output value
		# (a year later: ah, a magic number '8'. who knows where that came from)
		self.LEDControlID = int(self.location[1] + 8)

	def interact(self):
		print(self.name)

	def _initValue(self):
	    # update currentValue to the initial value. not sure how to do this yet so returns 0.
		return 0

	def updateValue(self, newValue):
		# find change that occurred, update currentValue if relevant
		if self.isAbsolute:
			# absolute knobs reliably send the next number each time
			if newValue == 127:
				change = 1
			elif newValue == 0:
				change = -1
			elif newValue > self.currentValue:
				change = 1
			elif newValue < self.currentValue:
				change = -1
			self.currentValue = newValue
		elif not self.isAbsolute:
			# relative knob sends 1 or higher for a right turn, 127 or lower for a left turn. unclear what possible pivot is.
			if newValue <= 63:
				change = 1
			elif newValue >= 64:
				change = -1
		# apply scaling to determine if outputs that function should apply
		# return 0 or 1 and the change.
		# if 0: scale not met. if 1: scale met. interpretMidiIn can ignore if scale is not met.
		if self.scale == 1:
			return 1, change
		else:
			self.scaleProgress += change
			if abs(self.scaleProgress) == self.scale:
				self.scaleProgress = 0
				return 1, change
			else:
				return 0, change
	
	def setLEDOff(self):
	    # we are not using knob LEDs so this is the only settable value
		return LED_CHANNEL_BASE_KNOB, self.LEDControlID, LEDKnobModes['OFF']

class Fader():

	def __init__(self, name, location):
		self.name = name
		self.location = location
		self.currentValue = self._initValue()

	def interact(self):
		print(self.name)

	def _initValue(self):
	    # update currentValue to the initial value. not sure how to do this yet so returns 0.
		return 0

	def updateValue(self, newValue):
		self.currentValue = newValue
		# argument becomes a float from 0 to 1 reflecting position along 0-127
		# rounded to 2dp.
		return round(self.currentValue/127, 2)

'''
create the buttons, knobs, faders
'''

buttons = (
	# name, loc
	# 3rd data point indicates its status, 127 = press down (so press up can be ignored). 0 = press up, so shift up can be added
	# GRID letter = row, number = column, A1:G9
	Button('b_GRID_A1', [144, 32, 127]),
	Button('b_GRID_A2', [144, 33, 127]),
	Button('b_GRID_A3', [144, 34, 127]),
	Button('b_GRID_A4', [144, 35, 127]),
	Button('b_GRID_A5', [144, 36, 127]),
	Button('b_GRID_A6', [144, 37, 127]),
	Button('b_GRID_A7', [144, 38, 127]),
	Button('b_GRID_A8', [144, 39, 127]),
	Button('b_GRID_A9', [144, 82, 127]),
	Button('b_GRID_B1', [144, 24, 127]),
	Button('b_GRID_B2', [144, 25, 127]),
	Button('b_GRID_B3', [144, 26, 127]),
	Button('b_GRID_B4', [144, 27, 127]),
	Button('b_GRID_B5', [144, 28, 127]),
	Button('b_GRID_B6', [144, 29, 127]),
	Button('b_GRID_B7', [144, 30, 127]),
	Button('b_GRID_B8', [144, 31, 127]),
	Button('b_GRID_B9', [144, 83, 127]),
	Button('b_GRID_C1', [144, 16, 127]),
	Button('b_GRID_C2', [144, 17, 127]),
	Button('b_GRID_C3', [144, 18, 127]),
	Button('b_GRID_C4', [144, 19, 127]),
	Button('b_GRID_C5', [144, 20, 127]),
	Button('b_GRID_C6', [144, 21, 127]),
	Button('b_GRID_C7', [144, 22, 127]),
	Button('b_GRID_C8', [144, 23, 127]),
	Button('b_GRID_C9', [144, 84, 127]),
	Button('b_GRID_D1', [144, 8, 127]),
	Button('b_GRID_D2', [144, 9, 127]),
	Button('b_GRID_D3', [144, 10, 127]),
	Button('b_GRID_D4', [144, 11, 127]),
	Button('b_GRID_D5', [144, 12, 127]),
	Button('b_GRID_D6', [144, 13, 127]),
	Button('b_GRID_D7', [144, 14, 127]),
	Button('b_GRID_D8', [144, 15, 127]),
	Button('b_GRID_D9', [144, 85, 127]),
	Button('b_GRID_E1', [144, 0, 127]),
	Button('b_GRID_E2', [144, 1, 127]),
	Button('b_GRID_E3', [144, 2, 127]),
	Button('b_GRID_E4', [144, 3, 127]),
	Button('b_GRID_E5', [144, 4, 127]),
	Button('b_GRID_E6', [144, 5, 127]),
	Button('b_GRID_E7', [144, 6, 127]),
	Button('b_GRID_E8', [144, 7, 127]),
	Button('b_GRID_E9', [144, 86, 127]),
	Button('b_GRID_E9-up', [128, 86, 0]),
	Button('b_GRID_F1', [144, 52, 127]),
	Button('b_GRID_F2', [145, 52, 127]),
	Button('b_GRID_F3', [146, 52, 127]),
	Button('b_GRID_F4', [147, 52, 127]),
	Button('b_GRID_F5', [148, 52, 127]),
	Button('b_GRID_F6', [149, 52, 127]),
	Button('b_GRID_F7', [150, 52, 127]),
	Button('b_GRID_F8', [151, 52, 127]),
	Button('b_GRID_F9', [144, 81, 127]),
	Button('b_GRID_F9-up', [128, 81, 127]),
	Button('b_GRID_G1', [144, 51, 127]),
	Button('b_GRID_G2', [145, 51, 127]),
	Button('b_GRID_G3', [146, 51, 127]),
	Button('b_GRID_G4', [147, 51, 127]),
	Button('b_GRID_G5', [148, 51, 127]),
	Button('b_GRID_G6', [149, 51, 127]),
	Button('b_GRID_G7', [150, 51, 127]),
	Button('b_GRID_G8', [151, 51, 127]),
	Button('b_GRID_G9', [144, 80, 127]),
	# TRACK 1-8, numbered l-r top-bottom so NUM A|B S rec
	Button('b_TRACK1_1', [144, 50, 127]),
	Button('b_TRACK1_2', [144, 66, 127]),
	Button('b_TRACK1_3', [144, 49, 127]),
	Button('b_TRACK1_4', [144, 48, 127]),
	Button('b_TRACK2_1', [145, 50, 127]),
	Button('b_TRACK2_2', [145, 66, 127]),
	Button('b_TRACK2_3', [145, 49, 127]),
	Button('b_TRACK2_4', [145, 48, 127]),
	Button('b_TRACK3_1', [146, 50, 127]),
	Button('b_TRACK3_2', [146, 66, 127]),
	Button('b_TRACK3_3', [146, 49, 127]),
	Button('b_TRACK3_4', [146, 48, 127]),
	Button('b_TRACK4_1', [147, 50, 127]),
	Button('b_TRACK4_2', [147, 66, 127]),
	Button('b_TRACK4_3', [147, 49, 127]),
	Button('b_TRACK4_4', [147, 48, 127]),
	Button('b_TRACK5_1', [148, 50, 127]),
	Button('b_TRACK5_2', [148, 66, 127]),
	Button('b_TRACK5_3', [148, 49, 127]),
	Button('b_TRACK5_4', [148, 48, 127]),
	Button('b_TRACK6_1', [149, 50, 127]),
	Button('b_TRACK6_2', [149, 66, 127]),
	Button('b_TRACK6_3', [149, 49, 127]),
	Button('b_TRACK6_4', [149, 48, 127]),
	Button('b_TRACK7_1', [150, 50, 127]),
	Button('b_TRACK7_2', [150, 66, 127]),
	Button('b_TRACK7_3', [150, 49, 127]),
	Button('b_TRACK7_4', [150, 48, 127]),
	Button('b_TRACK8_1', [151, 50, 127]),
	Button('b_TRACK8_2', [151, 66, 127]),
	Button('b_TRACK8_3', [151, 49, 127]),
	Button('b_TRACK8_4', [151, 48, 127]),
	# top right, left to right and top to bottom
	Button('b_TR1_PAN', [144, 87, 127]),
	Button('b_TR2_PLAY', [144, 91, 127]),
	Button('b_TR3_RECORD', [144, 93, 127]),
	Button('b_TR4_SESSION', [144, 102, 127]),
	Button('b_TR5_SENDS', [144, 88, 127]),
	Button('b_TR6_METRONOME', [144, 90, 127]),
	Button('b_TR7_TAPTEMPO', [144, 99, 127]),
	Button('b_TR8_USER', [144, 89, 127]),
	Button('b_TR9_NUDGE_MINUS', [144, 100, 127]),
	Button('b_TR10_NUDGE_PLUS', [144, 101, 127]),
	# bottom right
	Button('b_BOTTOMRIGHT_1', [144, 58, 127]),
	Button('b_BOTTOMRIGHT_2', [144, 59, 127]),
	Button('b_BOTTOMRIGHT_3', [144, 60, 127]),
	Button('b_BOTTOMRIGHT_4', [144, 61, 127]),
	Button('b_BOTTOMRIGHT_5', [144, 62, 127]),
	Button('b_BOTTOMRIGHT_6', [144, 63, 127]),
	Button('b_BOTTOMRIGHT_7', [144, 64, 127]),
	Button('b_BOTTOMRIGHT_8', [144, 65, 127]),
	Button('b_SHIFT', [144, 98, 127]),
	Button('b_BANK', [144, 103, 127]),
	Button('b_BANKSELECT_UP', [144, 94, 127]),
	Button('b_BANKSELECT_DOWN', [144, 95, 127]),
	Button('b_BANKSELECT_LEFT', [144, 97, 127]),
	Button('b_BANKSELECT_RIGHT', [144, 96, 127])
)

knobs = (
	# name, loc, [isAbsolute, scale]
	# absolute Knobs
	# 3rd data point declares its absolute value, range 0 to 127
	# top row
	Knob('k_TOP_1', [176, 48], scale=5),
	Knob('k_TOP_2', [176, 49], scale=5),
	Knob('k_TOP_3', [176, 50], scale=5),
	Knob('k_TOP_4', [176, 51], scale=5),
	Knob('k_TOP_5', [176, 52], scale=5),
	Knob('k_TOP_6', [176, 53], scale=5),
	Knob('k_TOP_7', [176, 54], scale=5),
	Knob('k_TOP_8', [176, 55], scale=2),
	# right
	Knob('k_RIGHT_1', [176, 16], scale=2),
	Knob('k_RIGHT_2', [176, 17], scale=2),
	Knob('k_RIGHT_3', [176, 18], scale=2),
	Knob('k_RIGHT_4', [176, 19], scale=2),
	Knob('k_RIGHT_5', [176, 20], scale=2),
	Knob('k_RIGHT_6', [176, 21], scale=2),
	Knob('k_RIGHT_7', [176, 22], scale=2),
	Knob('k_RIGHT_8', [176, 23], scale=2),
	# relative knobs
	# 3rd data point declares its relative value, 127 = left, 1 = right
	# CUE_LEVEL = middle, TEMPO = top right
	Knob('k_CUE_LEVEL', [176, 47], isAbsolute=False, scale=5),
	Knob('k_TEMPO', [176, 13], isAbsolute=False)
)

faders = (
	# 3rd data point declares its absolute value, range 0 to 127
	# name, loc
	Fader('f_1', [176, 7]),
	Fader('f_2', [177, 7]),
	Fader('f_3', [178, 7]),
	Fader('f_4', [179, 7]),
	Fader('f_5', [180, 7]),
	Fader('f_6', [181, 7]),
	Fader('f_7', [182, 7]),
	Fader('f_8', [183, 7]),
	Fader('f_9', [176, 14]),
	Fader('f_AB', [176, 15])
)

'''
store the locations of the buttons, knobs and faders as a tuple for easy access
'''

# make lists so we can use list comprehension
buttonLocations = [button.location for button in buttons]
knobLocations = [knob.location for knob in knobs]
faderLocations = [fader.location for fader in faders]

# turn these into tuples
buttonLocations = tuple(buttonLocations)
knobLocations = tuple(knobLocations)
faderLocations = tuple(faderLocations)
'''
def test(data1, data2):
	print(data1)
	print('uh')
mh = MidiHandler(callbackFunctionName='test')'''