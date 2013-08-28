#!/usr/bin/env python
import Queue
import threading
import Requests
import time

queue = Queue.Queue()

class ThreadJob(threading.Thread):
	"""Threaded job submit"""
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		
	def run(self):
		while True:
			# grab dependent job from queue
			job = self.queue.get()
			
			if job.is_ready_to_run:
				job.submit()
				self.queue.task_done()
				
	start = time.time()
	
	def main():
			
