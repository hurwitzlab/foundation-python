#!/usr/bin/env python
import FoundationJob

FAILED_STATUSES = ['KILLED', 'FAILED', 'STOPPED', 'ARCHIVING_FAILED',
                   'DEPENDENCY_FAILED']


class DependentJob(FoundationJob.FoundationJob):
    job_dependency = ''

    def __init__(self, api, software_name, job_name, job_dependency,
                 processor_count=1, max_memory=1, requested_time='1:00:00',
                 callback_url='', archive='false', archive_path='', inputs=[],
                 outputs=[], parameters=[]):
        super(DependentJob, self).__init__(api=api,
                                           software_name=software_name,
                                           job_name=job_name,
                                           processor_count=processor_count,
                                           max_memory=max_memory,
                                           requested_time=requested_time,
                                           callback_url=callback_url,
                                           archive=archive,
                                           archive_path=archive_path,
                                           inputs=inputs, outputs=outputs,
                                           parameters=parameters)
        self.job_dependency = job_dependency

    def job_dependencies_failed(self):
        status = self.job_dependency.job_status['result']['status']
        if status in FAILED_STATUSES:
            return True
        else:
            return False

    def is_job_ready_to_run(self):
        ready_to_run = self.is_dependency_finished()
        return ready_to_run

    def is_dependency_finished(self):
        status = self.job_dependency.job_status['result']['status']
        if status == 'ARCHIVING_FINISHED':
            return True
        else:
            return False

    def submit(self):
        self.job_dependency.update_status()
        print(str(self.job_dependency.job_status['result']['id']) +
              ' ' + str(self.is_job_ready_to_run()))
        result = ''
        if self.is_job_ready_to_run():
            result = super(DependentJob, self).submit()
        elif self.job_dependencies_failed():
            raise RuntimeError("Job dependency failed")
        return result
