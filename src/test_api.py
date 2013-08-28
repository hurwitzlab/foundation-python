#!/usr/bin/env python
from foundation import FoundationApi, FoundationJob, DependentJob
import time
import Queue
import threading

queue = Queue.Queue()

class ThreadJob(threading.Thread):
	"""Threaded job submit"""
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		
	def run(self):
		while True:
			# grab dependent job from queue
			try:
				job = self.queue.get(True, 2)
			except:
				if time.time() - time_of_last_run > 3:
					return
			else:
				if job.is_job_ready_to_run():
					job.submit()
					self.queue.task_done()
				time.sleep(20)
				
start = time.time()
	
def main():
	global time_of_last_run
	time_of_last_run = time.time()
	api = FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
	with open('password') as f:
		credentials = [x.strip().split(':') for x in f.readlines()]
	for username,password in credentials:	
		api.authenticate(username, password)
	# Change the file path to a file that you have access to
	inputs = {'inputFile': '/dboss/current-prot-universe.fa'}
	parameters = {'numberOfLines': '5'}
	jobs = []
	finished_jobs = []
	count = 0
	while (count < 2):
		test_job = FoundationJob.FoundationJob(api, 'head-stampede-5.97u2', 'Head test', 
					archive='true', inputs=inputs, parameters=parameters)
		jobs.append(test_job)
		count += 1
	for job in jobs:
		job.submit()
		time.sleep(2)
		job.update_status()
	for i in range(2):
		t = ThreadJob(queue)
		t.setDaemon(True)
		t.start()
	for job in jobs:
		dependent_job = DependentJob.DependentJob(api, 'head-stampede-5.97u2', 'Head dep', 
					archive='true', inputs=inputs, parameters=parameters, job_dependency=job)
		queue.put(dependent_job)
	print "Running..."
	while time.time() - time_of_last_run < 3:
		print ">> qsize %s threadCount %s" % (queue.qsize(),threading.activeCount())
		time.sleep(2)
	
	time.sleep(4)
	queue.join()
	print('All jobs finished')
	
if __name__ == "__main__":
	  main()