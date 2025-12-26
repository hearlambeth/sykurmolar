'''
dictionaries mapping midi buttons/knobs/faders to specific functions
'''

normal = {
	# a single string or a 2-tuple
	# if a tuple, the first is the function, second is the data
	'b_GRID_A8': ('moliKnobOptions_CHANGE', 2),
	'b_GRID_A9': ('moliKnobOptions_CHANGE', 0),
	'b_GRID_B2': ('triggerKnobOptions_CHANGE', 0),
	'b_GRID_B8': ('moliKnobOptions_CHANGE', 3),
	'b_GRID_B9': ('moliKnobOptions_CHANGE', 1),
	'b_GRID_C9': ('moliKnobOptions_CHANGE', 4),
	'b_GRID_D2': ('triggerKnobOptions_CHANGE', 1),
	'b_GRID_D9': ('moliKnobOptions_CHANGE', 5),
	'b_GRID_E2': ('triggerKnobOptions_CHANGE', 2),
	'b_GRID_E9': 'forceRespondOnce_SHIFTDOWN',
	'b_GRID_E9-up': 'forceRespondOnce_SHIFTUP',
	'b_GRID_F9': 'jumpToLimit_SHIFTDOWN',
	'b_GRID_F9-up': 'jumpToLimit_SHIFTUP',
	'b_GRID_G1': ('changeSelectedSykurmolar', 0),
	'b_GRID_G2': ('changeSelectedSykurmolar', 1),
	'b_GRID_G3': ('changeSelectedSykurmolar', 2),
	'b_GRID_G4': ('changeSelectedSykurmolar', 3),
	# individual track buttons
	'b_TRACK8_4': 'lineInMute',
	# fader
	'f_AB': 'lineInChangePan',
	# top right
	'b_TR2_PLAY': 'displayFull',
	'b_TR3_RECORD': 'record',
	'b_TR4_SESSION': 'endProgram'
}

sykurmola = {
	# a single string or a 2-tuple
	# if a tuple, the first is the function, second is the data
	'b_GRID_A4': ('changeTriggerSource', 12),
	'b_GRID_A5': ('changeTriggerSource', 1),
	'b_GRID_A6': ('changeStartPointOffsetMax', 50),
	'b_GRID_B1': ('changeTriggerSource', 2),
	'b_GRID_B3': ('changeTriggerSource', 5),
	'b_GRID_B4': ('changeTriggerSource', 11),
	'b_GRID_B6': ('changeStartPointOffsetMax', 200),
	'b_GRID_B7': 'shuffleFreezeVariables',
	'b_GRID_C1': ('changeTriggerSourceChoice', (13,19)),
	'b_GRID_C3': ('changeTriggerSourceChoice', (20,26)),
	'b_GRID_C4': ('changeTriggerSource', 10),
	'b_GRID_C6': ('changeStartPointOffsetMax', 1000),
	'b_GRID_C7': 'reverseFreezeVariables',
	'b_GRID_D1': ('changeTriggerSource', 3),
	'b_GRID_D3': ('changeTriggerSource', 6),
	'b_GRID_D4': ('changeTriggerSource', 9),
	'b_GRID_D6': ('changeStartPointOffsetMax', 5000),
	'b_GRID_D7': 'freezeOn',
	'b_GRID_E1': ('changeTriggerSource', 4),
	'b_GRID_E3': ('changeTriggerSource', 7),
	'b_GRID_E4': ('changeTriggerSource', 8),
	'b_GRID_E6': ('changeStartPointOffsetMax', 24000),
	'b_GRID_E7': 'freezeOff',
	'b_GRID_G5': ('changeStartPointIndex', 1),
	'b_GRID_G6': ('changeStartPointIndex', 2),
	'b_GRID_G7': ('changeStartPointIndex', 3),
	'b_GRID_G8': ('changeStartPointIndex', 4),
	'b_GRID_G9': ('changeStartPointIndex', 0),
	'b_TR7_TAPTEMPO': 'stop',
	'b_TR10_NUDGE_PLUS': 'reset',
	'b_BOTTOMRIGHT_1': ('changePitchMacroMultiplier', 3),
	'b_BOTTOMRIGHT_2': 'resetPitchMicro',
	'b_BOTTOMRIGHT_3': ('changePitchMacroMultiplier', 9),
	'b_BOTTOMRIGHT_4': ('changePitchMacroMultiplier', 10),
	'b_BOTTOMRIGHT_5': ('changePitchMacroMultiplier', 4),
	'b_BOTTOMRIGHT_6': ('changePitchMacroMultiplier', 5),
	'b_BOTTOMRIGHT_7': ('changePitchMacroMultiplier', 7),
	'b_BOTTOMRIGHT_8': ('changePitchMacroMultiplier', 12),
	'b_SHIFT': ('changePitchMacroMultiplier', 19),
	'b_BANK': ('changePitchMacroMultiplier', 14),
	'k_TOP_6': 'changeGlobalResponse',
	'k_TOP_7': 'changeFreezeLength',
	'k_CUE_LEVEL': 'changeLineInInterruptBias',
	'k_TEMPO': 'changeActiveBitar'
}

sykurmolaAmbiguous = {
	# a tuple in the format: ((max, min, spread, mid, bias, changes), forceRespondOnce_TOGGLE),
	# where each is the name of a function
	# provide None if none
	'k_RIGHT_1': (('changePanMax', 'changePanMin', 'changePanSpread', 'changePanMid', 'changePanBias', 'changePanResponse'), 'doForceRespondPanOnce'),
	'k_RIGHT_2': ((None, None, None, None, 'changeDirectionBias', 'changeDirectionResponse'), 'doForceRespondDirectionOnce'),
	'k_RIGHT_3': ((None, None, None, None, 'changeLengthBias', 'changeLengthResponse'), 'doForceRespondLengthOnce'),
	'k_RIGHT_4': ((None, None, None, None, 'changeEndarBias', 'changeEndarResponse'), 'doForceRespondEndarOnce'),
	'k_RIGHT_5': (('changePitchMacroMax', 'changePitchMacroMin', 'changePitchMacroSpread', 'changePitchMacroMid', 'changePitchMacroBias', 'changePitchMacroResponse'), 'doForceRespondPitchMacroOnce'),
	'k_RIGHT_6': (('changePitchMicroMax', 'changePitchMicroMin', 'changePitchMicroSpread', 'changePitchMicroMid', 'changePitchMicroBias', 'changePitchMicroResponse'), 'doForceRespondPitchMicroOnce'),
	'k_RIGHT_7': ((None, None, None, None, 'changeAudibleBias', 'changeAudibleResponse'), 'doForceRespondAudibleOnce'),
	'k_RIGHT_8': (('changeVolumeMax', 'changeVolumeMin', 'changeVolumeSpread', 'changeVolumeMid', 'changeVolumeBias', 'changeVolumeResponse'), 'doForceRespondVolumeOnce')
}

triggerAmmæli = {
	# a tuple in the format: (ammæliNumber, function)
	'b_GRID_A1': (0, 'tapTempo'),
	'b_GRID_A3': (1, 'tapTempo'),
	'b_GRID_F1': (0, 'newSwungRhythm'),
	'b_GRID_F3': (1, 'newSwungRhythm')
}

triggerAmmæliAmbiguous = {
	# a tuple in the format: (ammæliNumber, functionsTuple)
	'k_TOP_1': (0, ('incrementDuration', 'incrementSwing', 'incrementSwungRhythmBeats')),
	'k_TOP_3': (1, ('incrementDuration', 'incrementSwing', 'incrementSwungRhythmBeats'))
}

triggerTappedRhythm = {
	'b_GRID_B5': 'tap',
	'b_GRID_C5': 'tapAndGo',
	'b_GRID_D5': 'nullNewRhythm',
	'k_TOP_5': 'incrementDuration'
}

startPoint = {
	'b_GRID_F5': 1,
	'b_GRID_F6': 2,
	'b_GRID_F7': 3,
	'b_GRID_F8': 4
}

sykurmolaSpecific = {
	# takes a tuple: number of Sykurmolar (0-) to apply to, function name, function data to pass
	# will apply to allSykurmolar[number]
	'b_TRACK1_1': (0, 'nya', None),
	'b_TRACK1_2': (0, 'changeTriggerSource', 0),
	'b_TRACK1_3': (0, 'stop', None),
	'b_TRACK1_4': (0, 'reset', None),
	'b_TRACK2_1': (1, 'nya', None),
	'b_TRACK2_2': (1, 'changeTriggerSource', 0),
	'b_TRACK2_3': (1, 'stop', None),
	'b_TRACK2_4': (1, 'reset', None),
	'b_TRACK3_1': (2, 'nya', None),
	'b_TRACK3_2': (2, 'changeTriggerSource', 0),
	'b_TRACK3_3': (2, 'stop', None),
	'b_TRACK3_4': (2, 'reset', None),
	'b_TRACK4_1': (3, 'nya', None),
	'b_TRACK4_2': (3, 'changeTriggerSource', 0),
	'b_TRACK4_3': (3, 'stop', None),
	'b_TRACK4_4': (3, 'reset', None)
}

sykurmolaSpecificFader = {
	# takes a tuple: number of Sykurmolar (0-) to apply to, function name
	'f_1': (0, 'changeVolume'),
	'f_2': (1, 'changeVolume'),
	'f_3': (2, 'changeVolume'),
	'f_4': (3, 'changeVolume')
}