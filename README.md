# sykurmolar/sugarcubes

a sampling/looping program that uses an apc40 mkii to perform partially controllable, randomized playback of live sound. i control the limitations and degree of randomness of many variables of a few discrete groups (sykurmolar) of sound playback devices (bitar). it has a set of triggers the devices respond to.

this is very much for my own purposes. it contains bits of icelandic. it is here for an extra backup and for version control. it is not good or clean code or configurable for hardware other than my own. 

in use in some form live since 2024. built on lessons from previous loopers using pyo and computer keyboard controllers, 2017-2021.

# requirements

- linux
- audio interface
- apc40 mkii
- python libraries: pyo64, rtmidi, a few mathematical ones

# usage (laptop)

1. cd to folder containing sykurmolar.py

2. run bash script to create a better audio environment
```
sudo bash prestart.sh
```

3. run bash script to initiate jack
```
bash jack_start.sh
```

4. in a separate terminal, run sykurmolar.py interactively
```
/usr/bin/python3.10 -i "sykurmolar.py"
```

# to do

- migrate to raspberry pi
	- get pi soundcard, screen, shield, mount all to midi controller
	- add flag to specify device used (computer, raspberry pi)
	- tailor text output to raspberry pi screen space limitations
	- pi boot routine: shell scripts, then sykurmolar
- improve visual feedback of sounds occurring (esp. LEDs)
- improve text output generally (done triggers, displayFull, more?)
- print more/fix labels
- make helvítis fokking fokk move every trigger - how? create a list of start points all over the shop?
- add limiter so a direct recording can be useful
- make trigger type that loops randomized complex rhythms
- make trigger type that loops tapped rhythms
- trigger type "combine" - abandon?
- learn how to make use of individual response values for each parameter
- make a constants file to place all constants
- fix bug: sometimes some knob LEDs fail to turn off on start
- (long term) preset save, start. save all sykurmolar variables to a json, loaded like newAll.