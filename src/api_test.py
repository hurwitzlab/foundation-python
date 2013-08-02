#!/usr/bin/env python
from foundation import FoundationApi, FoundationJob
import time

api = FoundationApi.FoundationApi()
# Put in your iPlant userid and password
api.authenticate('dboss', 'XXXXXXXX')
# Change the file path to a file that you have access to
inputs = {'inputFile': '/dboss/current-prot-universe.fa'}
parameters = {'numberOfLines': '5'}
jobs = []
finished_jobs = []
failed_jobs = []
count = 0
while (count < 5):
	test_job = FoundationJob.FoundationJob(api, 'head-stampede-5.97u2', 'Head test', 
				archive='true', inputs=inputs, parameters=parameters)
	jobs.append(test_job)
	count += 1
for job in jobs:
	job.submit()
while (len(jobs) > 0):
	for job in jobs:
		job.update_status()
		if job.job_status['result']['status'] == 'ARCHIVING_FINISHED':
			finished_jobs.append(job)
			jobs.remove(job)
		elif job.job_status['result']['status'] == 'FAILED':
			print('Job ID: ' + str(job.job_status['result']['id']) + 'status = ' + job.job_status['result']['status'])
			failed_jobs.append(job)
			jobs.remove(job)
		else:
			# we need to remove the failed job ids as well.
			print('Job ID: ' + str(job.job_status['result']['id']) + 'status = ' + job.job_status['result']['status'])
		time.sleep(1)
	time.sleep(10)
print('All jobs have finished!')
