'''
constants, for easy updating
'''

import sys, os
from time import strftime

# audio setup
#	jack
#	cli version of this: /usr/bin/jackd -v -R -dalsa -dhw:CODEC -r48000 -p512 -n8
#	JACK_DRIVER and JACK_DEVICE are only referenced in the unused jackSetup.py file
JACK_DRIVER = "alsa"
JACK_DEVICE = "hw:codec"
PERIODS_PER_BUFFER = 8
BUFFER_SIZE = 512
SAMPLE_RATE = 48000
SAMPLE_RATE_IN_SECONDS = 1/SAMPLE_RATE
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
TINY_DUR_SECONDS = 0.05 # 20hz
TINY_DUR_SAMPLES = int(TINY_DUR_SECONDS * SAMPLE_RATE)
PRIMES = (5, 7, 11, 13, 17, 19, 23) # len: 7
SIMPLELOOP_DURATION_MULTIPLIER = 1.03
SIMPLELOOP_DURATION_MAX_SECONDS = 20
SIMPLELOOP_DURATION_MAX_SAMPLES = int(SIMPLELOOP_DURATION_MAX_SECONDS * SAMPLE_RATE)
TAPRHYTHM_DURATION_MULTIPLIER = 1.03
TAPRHYTHM_TIMEOUT_SECONDS = 10
TAPRHYTHM_TIMEOUT_SAMPLES = int(TAPRHYTHM_TIMEOUT_SECONDS * SAMPLE_RATE)
SWING_INCREMENT = 0.1 # out of 1
SWING_MAX = 0.95
SWING_MIN = 0.05
SWING_RHYTHM_MAX_BEATS = 100

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

