# sykurmolar/sugarcubes

a sampling/looping program that uses an apc40 mkii to perform partially controllable, randomized playback of live sound. i control the limitations and degree of randomness of many variables of a few discrete groups (sykurmolar) of sound playback devices (bitar). it has a set of triggers the devices respond to.

this is very much for my own purposes. it contains bits of icelandic. it is here for an extra backup and for version control. it is not good or clean code or configurable for hardware other than my own. 

in use in some form live since 2024. built on lessons from previous loopers using pyo and computer keyboard controllers, 2017-2021.

# broadly ...

- the program constantly records my live playing to an audiostream, which caps at 45 minutes.
- sections of the audiostream can be played back, either at defineable points (like sampling) or a constantly-moving time just behind the live playing.
- the audio is played back using sets (sykurmolar) of playback devices (bitar, up to 10 playing at any time per set). there is control - randomized within configurable limitations - over whether they loop by themselves, their direction, their pitch/speed, their volume, etc. pitch/speed includes the ability to make stacked 4ths, 5ths etc, and to offset by a small amount to create a chorus effect.
- the playback happens using triggers, some of them rhythmic and some very random. these include tappable rhythms, simple and swung looped beats, generated rhythms, prime subdivisions, and random clouds of varying density.
- at any time, sykurmolar can change their triggers, including to stop receiving triggers (so audio can "run away" by itself). sykurmolar can be set to ignore triggers a certain percentage of the time, or certain parameters can be set to ignore changes.
- parameters can change freely (always going to a new value every trigger) or can loop through a certain length of values (e.g. always choosing the next of 3 values, then looping back).
- there are faders for the sum volume of sykurmolar.
- the output may be recorded to disk any number of times during the session.

# requirements, simplified

- linux
- audio interface
- apc40 mkii
- python libraries: pyo, rtmidi, numpy, jack_server (unused)

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
python -i "sykurmolar.py"
```

# installation on Raspberry Pi 5 running PatchboxOS

this describes, messily, the steps to a successful installation and causing it to start on boot.

1. make new Patchbox, set jack config, set realtime kernel
2. use pyenv to get python3.10.14, which is the version used in the original sykurmolar creation. it probably also works on 3.11.
	- download, following: https://github.com/pyenv/pyenv?tab=readme-ov-file#a-getting-pyenv (at step D follow instructions for apt https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
	- install 3.10.14 with `pyenv install 3.10.14`
	- set this to default python with `pyenv global 3.10.14`
3. get requirements to build pyo with sources: `sudo apt-get install libjack-jackd2-dev libsndfile1 libsndfile1-dev`
(probably old problems: i previously tried libsndfile, which was a more complicated build: https://github.com/libsndfile/libsndfile; i also previously used libjack-dev, which gets uninstalled by blokas-jack)
4. build pyo from sources, with flags to use jack, double precision (pyo64) and minimal (no portmidi etc.): `python -m build --config-setting="--build-option=--use-jack" --config-setting="--build-option=--use-double" --config-setting="--build-option=--minimal"` and install wheel - however it's named - e.g. `pip install dist/pyo-1.0.6-cp310-cp310-linux_aarch64.whl`*
5. sudo apt install blokas-jack (if this was uninstalled earlier by pyo dependencies), and reboot
6. install sykurmolar here using `git clone ...`
7. install other dependencies using `pip install -r requirements.txt`
8. `mkdir recordings` in sykurmolar directory, to have somewhere to put recordings
9. make the script start whenever the console starts. in the home directory, `nano .bashrc` and append to end the command to run the code: `/home/patch/.pyenv/shims/python3.10 -i ./sykurmolar/sykurmolar.py`

patchbox module and systemd both cannot run interactive python scripts in console, so .bashrc was my solution. thanks to zuggamasta & giedrius: https://community.blokas.io/t/creating-a-module-to-install-and-launch-python/5965/

*unclear problem: this resulted in: "ModuleNotFoundError: No module named 'pyo._pyo'" from "/home/patch/pyo/pyo/lib/_core.py", line 48 line: from .._pyo import *; i did pip install -i https://test.pypi.org/simple/ pyo==1.0.5, and then it worked, but the version shows as 1.0.6. not sure what happened here. may have been fixed by a reboot.

INCOMPLETE! next:
- get a Pisound soundcard, a screen (I2C OLED display, eg https://www.pishop.us/product/1-32inch-oled-display-module-128x96-spi-i2c/?searchid=0&search_query=i2c+oled+display), and a shield
- test extremes (all sykurmolar, 10 bitar, speedy snail) to evaluate if components of prestart.sh are necessary to include. on usb interface, it did not handle even one 10-bitar sykurmolar on speedy snail very well, but light use was fine.
- does this Pi have wifi? is it disabled when jack is running?

# label printing

on libreoffice, zoom to 131% to see exact paper size. print with OCR A font size 17. this did not match the old labels. :(

# to do

- further tailor text output to raspberry pi screen space limitations
- improve visual feedback of sounds occurring (esp. LEDs)
- improve text output generally - add more trigger info to displayFull
- helvítis fokking fokk cannot work right now. commented out. way to make it work would be to make a dynamic list of past absolute sample values.
- add limiter so a direct recording can be more useful. either:
	- sum all moli mixers and direct out in sykurmolar.py
	- separately record each moli to individual wavs. intensive.
	- nevermind, just use cassettes
- add swing to tapped rhythm? too much?
- learn how to make use of individual response values for each parameter
- fix bug: sometimes some knob LEDs fail to turn off on start. trying: do it again.
- fix bug: endar still click. did i mess up a fadeout/fadein time?
- fix bug: forceRespondOnce_TOGGLE doesn't seem to do anything. did i remove this feature? did i not implement it properly?
- how to release cursor after program end? - fix added
- (long term) preset save, start. save all sykurmolar variables to a json, loaded like newAll.