#!/usr/bin/env python
from subprocess import call

condor_submit = open('tmp.submit', 'w')
file_list = ['file1','file2','file3']
static_args = "-c 0.6 -aS 0.8 -g 1 -n 4 -d 0"
condor_header = """
Universe       = vanilla
Executable     = /usr/local2/cd-hit-v4.6.1-2012-08-27/cd-hit
Input   = /dev/null
"""
condor_submit.write(condor_header + '\n')
for f in file_list:
	condor_submit.write('Output = ' + f + '.out\n')
	condor_submit.write('Error = ' + f + '.error\n')
	condor_submit.write('Arguments = -i ' + f + '.fa -o' + f + 'out.fa' + static_args + '\n')
	condor_submit.write('queue\n')
