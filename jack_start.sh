#! /usr/bin/bash
jack="/usr/bin/jackd -R -dalsa -dhw:CODEC -r48000 -p512 -n8"
echo "Starting Jack..."
if $jack; then
	echo "SUCCESS: Jack running"
else
	echo "JACK ERROR FOR SOME REASON"
	exit 1
fi
exit 0