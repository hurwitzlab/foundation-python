#!/usr/bin/env python
import requests, FoundationApi

class FoundationJob:
	"""Foundation Job class"""
	api = FoundationApi.FoundationApi
	# softwareName
	software_name = ''
	# jobName
	job_name = ''
	# processorCount
	processor_count = 1
	# maxMemory in Gigabytes
	max_memory = 1
	# requestedTime
	requested_time = '1:00:00'
	# callbackURL
	callback_url = ''
	# archive
	archive = ''
	# archivePath 
	archive_path = ''
	# inputs
	inputs = {}
	# parameters
	parameters = {}
	# outputs
	outputs = {}
	# softwareName
	software_name = ''
	# job status
	job_status = ''
	
	def __init__(self, api, software_name, job_name, processor_count=1, max_memory=1, requested_time='1:00:00',
				callback_url='', archive='false', archive_path='', inputs=[], outputs=[], parameters=[]):
		self.api = api
		self.software_name = software_name
		self.job_name = job_name
		self.processor_count = processor_count
		self.max_memory = max_memory
		self.requested_time = requested_time
		self.callback_url = callback_url
		self.archive = archive
		self.archive_path = archive_path
		self.inputs = inputs
		self.outputs = outputs
		self.parameters = parameters
	
	def __eq__(self, other):
		if other.job_status['result']['id'] == self.job_status['result']['id']:
			return True
		else:
			return False
		
	def submit(self):
		self.job_status = self.api.run_job(self)
		
	def update_status(self):
		self.job_status = self.api.job_status(self.job_status['result']['id'])
		return self.job_status;