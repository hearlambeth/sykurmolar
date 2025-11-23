'''
constants, for easy updating
NOT YET REPLACING OTHER CODE
'''

import sys, os
from time import strftime

# audio setup
#	jack
#	cli version of this: /usr/bin/jackd -v -R -dalsa -dhw:CODEC -r48000 -p512 -n8
PERIODS_PER_BUFFER = 8
BUFFER_SIZE = 512
SAMPLE_RATE = 48000
# 	general
INPUT_CHANNELS = 1
OUTPUT_CHANNELS = 2
PROGRAM_DURATION_MINUTES = 45
AUDIO_TABLE_DURATION_SAMPLES = SAMPLE_RATE * PROGRAM_DURATION_MINUTES * 60

# recording
RECORDED_FILE_PREFIX = str(strftime("%y%m%d") + "-" + strftime("%H%M%S"))
RECORDED_FILE_DESTINATION_FINAL = os.path.join(sys.path[0],'recordings')
RECORDED_FILE_DESTINATION_TEMP = '/dev/shm/'

# numbers of instances of classes. only bitar can be freely changed due to midi controller layout.
NUMBER_OF_START_POINTS = 4
NUMBER_OF_SYKURMOLAR = 4
BITAR_PER_SYKURMOLI = 10

# trigger
PRIIMES = (2, 3, 5, 7, 11)
PRIMES = (13, 17, 19, 23, 29)
SIMPLELOOP_DURATION_MULTIPLIER = 1.03
SIMPLELOOP_DURATION_MAX_SECONDS = 20
SIMPLELOOP_DURATION_MIN_SECONDS = 0.05 #20hz
SIMPLELOOP_DURATION_MAX_SAMPLES = int(SIMPLELOOP_DURATION_MAX_SECONDS * SAMPLE_RATE)

# other
LINE_IN_LOOKBACK_RANGE_MIN_SECONDS = 2.6 # defines the time before now that StartPoint of type lineIn can pick
LINE_IN_LOOKBACK_RANGE_MIN_SAMPLES = int(LINE_IN_LOOKBACK_RANGE_MIN_SECONDS * SAMPLE_RATE)
START_POINT_UPDATE_FREQUENCY_SECONDS = 1
PORTAMENTO_TRANSITION_SECONDS = 0.005 #0.005
ENDALAUS_FADE_SECONDS = 0.01
FREEZE_LENGTH_MAX = 100
VARIABLES_LIST_LENGTH = 1000 # randomBinomial is quite a bit faster at 500 vs 1000
KNOB_DIV = 20 # amount the knob's passed value gets divided by. basically how granular can i be with turns.
#	unreasonable caps. at octave multiplication, min = ~11 samples/second, max = entire 45m table in under a second
PITCH_MIN = -12
PITCH_MAX = 12

