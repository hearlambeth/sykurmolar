import os
from time import sleep
from statistics import median


vals = [
[3,0,0,0,0],
[3,1,0,0,0],
[3,2,0,0,0],
[2,2,0,0,0],
[2,3,0,0,0],
[1,3,0,0,0],
[0,3,0,0,0],
[0,3,1,0,0],
[0,3,2,0,0],
[0,2,2,0,0],
[0,2,3,0,0],
[0,1,3,0,0],
[0,0,3,0,0],
[0,0,3,1,0],
[0,0,3,2,0],
[0,0,2,2,0],
[0,0,2,3,0],
[0,0,1,3,0],
[0,0,0,3,0],
[0,0,0,3,1],
[0,0,0,3,2],
[0,0,0,2,2],
[0,0,0,2,3],
[0,0,0,1,3],
[0,0,0,0,3],
]

chars = [' ','.','o','O']

print(len(vals))
print('start')
sleep(0.5)

for n in range(len(vals)):
	newString = ''
	for c in vals[n]:
		newString += chars[c]
	print(newString, end="\r")
	sleep(0.2)

print('done ')