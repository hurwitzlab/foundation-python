#!/usr/bin/env python
from foundation import FoundationApi
import argparse

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument("-r", "--runTag", help="Runtag for the pipeline instance")

	args= parser.parse_args()

	api = FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
    	with open('password') as f:
        	credentials = [x.strip().split(':') for x in f.readlines()]
    	for username, password in credentials:
        	api.authenticate(username, password)


	job_status = ''

	if args.runTag != None :
        	# returns status of all the jobs for particular run tag
		job_status = api.past_jobs()

		for result in job_status['result']:
			if result['name'] == args.runTag:
				#print str(result['id'])	
				print('Job ID: ' + str(result['id']) + '  status = ' + result['status'])

if __name__ == "__main__":
    main()

 
