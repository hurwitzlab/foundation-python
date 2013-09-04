#!/usr/bin/env python
from foundation import FoundationApi
import argparse

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument("-r", "--runTag", help="Runtag for the pipeline instance")

	parser.add_argument("flag", help="Runtag for the pipeline instance")

	#parser.add_argument("delete", help="Runtag for the pipeline instance")

	args= parser.parse_args()

	if args.runTag == None:
		raise argparse.ArgumentTypeError("runTag is required to query status or delete jobs of any pipeline.")

	api = FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
    	with open('password') as f:
        	credentials = [x.strip().split(':') for x in f.readlines()]
    	for username, password in credentials:
        	api.authenticate(username, password)


	job_status = ''

	if args.flag == 'status' :
        	# returns status of all the jobs for particular run tag
		job_status = api.past_jobs()

		for result in job_status['result']:
			if result['name'] == args.runTag:
				#print str(result['id'])	
				print('Job ID: ' + str(result['id']) + '  status = ' + result['status'])


	elif args.flag == 'delete' :
		# returns status of all the jobs for particular run tag
                job_status = api.past_jobs()

                for result in job_status['result']:
                        if result['name'] == args.runTag:
                                api.kill_job(str(result['id']))
	

if __name__ == "__main__":
    main()

 
