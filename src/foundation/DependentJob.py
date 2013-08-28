#!/usr/bin/env python
import FoundationJob

class DependentJob(FoundationJob.FoundationJob):
	job_dependency = ''
	def __init__(self, api, software_name, job_name, job_dependency, processor_count=1, max_memory=1, requested_time='1:00:00',
				callback_url='', archive='false', archive_path='', inputs=[], outputs=[], parameters=[]):
		super(DependentJob, self).__init__(api=api, software_name=software_name, job_name=job_name,
		 		processor_count=processor_count, max_memory=max_memory, requested_time=requested_time,
				callback_url=callback_url, archive=archive, archive_path=archive_path, inputs=inputs, outputs=outputs, parameters=parameters)
		self.job_dependency = job_dependency
		
	def job_dependencies_failed(self):
		if self.job_dependency.job_status['result']['status'] in ['FAILED', 'DEPENDENCY_FAILED']:
			return True
		else:
			return False

	def is_job_ready_to_run(self):
		ready_to_run = self.is_dependency_finished()
		return ready_to_run

	def is_dependency_finished(self):
		if self.job_dependency.job_status['result']['status'] == 'ARCHIVING_FINISHED':
			return True
		else:
			return False

	def update_status(self):
		self.job_status = self.api.job_status(self.job_status['result']['id'])
		return self.job_status;
