import constants
import jack_server
# emulating cli: "/usr/bin/jackd -R -dalsa -dhw:CODEC -r48000 -p512 -n8"

jackServer = jack_server.Server(
		realtime=True,
		driver=constants.JACK_DRIVER,
		device=constants.JACK_DEVICE,
		rate=constants.SAMPLE_RATE,
		period=constants.BUFFER_SIZE,
		nperiods=constants.PERIODS_PER_BUFFER
	)

def start():
	jackServer.start()

def stop():
	jackServer.stop()