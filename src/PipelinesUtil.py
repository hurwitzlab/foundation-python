#!/usr/bin/env python
import FoundationApi
import OptionParser
import fileinput
import os

def main():

	parser = OptionParser()
	parser.add_option("-user", "--username", dest="username",
                  help="Username", type="string")
	parser.add_option("-pwd", "--password", dest="password",
                  help="Password", type="string")
	parser.add_option("-p", "--poll", dest="poll",
                  help="To pollover job id in dependency file", type="string")
	parser.add_option("-s", "--status", dest="status",
                  help="To look for status of jobs for a run tag", type="string")

	parser.add_option("-c", "--clean", dest="clean",
                  help="To clean run tag files for pipeline", type="string")

	parser.add_option("-r", "--runTag", dest="runTag",
                  help="Runtag for the application instance", type="string")


	(options, args) = parser.parse_args()

	api = FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
	api.authenticate(options.username, options.password)

	job_status = ''

	if options.status == 'true':
        	# returns status of all the jobs for particular run tag
		for line in fileinput.input([options.runTag + '.all']):
			job_status = api.job_status(line)
                	print('Job ID: ' + str(job_status['result']['id']) + 'status = ' + job_status['result']['status'])

	if options.poll == 'true':
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
					fo.write( job_status['result']['id'] + "\n")
					break
				else:
                			time.sleep(10)
			

	if options.clean == 'true':
		os.remove(options.runTag + '.all')
		os.remove(options.runTag + '.dependency')
		os.remove(options.runTag + '.failed')

if __name__ == "__main__":
    main()

 
