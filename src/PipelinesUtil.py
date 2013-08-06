#!/usr/bin/env python
from foundation import FoundationApi
from optparse import OptionParser

import fileinput
import os
import time

def main():

	parser = OptionParser()
	parser.add_option("-u", "--username", dest="username",
                  help="Username", type="string")
	parser.add_option("-p", "--password", dest="password",
                  help="Password", type="string")
	parser.add_option("-P", "--poll", dest="poll",
                  help="To pollover job id in dependency file", type="string")
	parser.add_option("-s", "--status", dest="status",
                  help="To look for status of jobs for a run tag", type="string")

	parser.add_option("-c", "--clean", dest="clean",
                  help="To clean run tag files for pipeline", type="string")

	parser.add_option("-r", "--runTag", dest="runTag",
                  help="Runtag for the application instance", type="string")

	parser.add_option("-o", "--output", dest="output",
                  help="To look for list of output files", type="string")


	(options, args) = parser.parse_args()

	if options.username == None :
                raise TypeError('username missing from command-line.')

        if options.password == None :
                raise TypeError('password missing from command-line.')

        if options.runTag == None :
                raise TypeError('runTag missing from command-line.')

	api = FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
	api.authenticate(options.username, options.password)

	job_status = ''
	job_output = ''

	if options.output == 'true':
        	# returns status of all the jobs for particular run tag
		for line in fileinput.input([options.runTag + '.all']):
			job_output = api.list_files('/dchouras')
                	print(job_output)

	elif options.poll == 'true':
        	# returns status of all the jobs for particular run tag
        	for line in fileinput.input([options.runTag + '.dependency']):
			while True :
				job_status = api.job_status(line)
				if job_status['result']['status'] == 'ARCHIVING_FINISHED':
					# delete dependency file
					os.remove(options.runTag + '.dependency')			
					break
                		elif job_status['result']['status'] == 'FAILED':
					# delete dependency file
                                	os.remove(options.runTag + '.dependency')
					fo = open(options.runTag + '.failed', "a")
					fo.write( str(job_status['result']['id']) + "\n")
					break
				else:
                			time.sleep(10)
			

	elif options.clean == 'true':
		os.remove(options.runTag + '.all')
		os.remove(options.runTag + '.dependency')
		os.remove(options.runTag + '.failed')

	else:	
        	# returns status of all the jobs for particular run tag
		for line in fileinput.input([options.runTag + '.all']):
			job_status = api.job_status(line)
                	print('Job ID: ' + str(job_status['result']['id']) + ' status = ' + job_status['result']['status'])

if __name__ == "__main__":
    main()

 
