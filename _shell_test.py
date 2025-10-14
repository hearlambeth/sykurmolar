# works!
'''
from time import sleep
import subprocess
commands = (
	["systemctl", "start", "cpupower.service"],
	["sysctl", "vm.swappiness=10"],
	["sysctl", "fs.inotify.max_user_watches=600000"]
)
for command in commands:
	subprocess.Popen(command)
	sleep(0.1)'''

import subprocess
audioEnvironmentSetup = subprocess.call(['sh', './start.sh'])
if audioEnvironmentSetup != 0:
	raise RuntimeError("Must run this in sudo to create the audio environment okay")