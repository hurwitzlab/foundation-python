#!/usr/bin/env python
import FoundationJob
import Queue
import time

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
        #print(str(self.job_dependency.job_status['result']['id']) +
        #      ' ' + str(self.is_job_ready_to_run()))
        result = ''
        if self.is_job_ready_to_run():
            result = super(DependentJob, self).submit()
        elif self.job_dependencies_failed():
            raise RuntimeError("Job dependency failed")
        return result


class DependencyQueue():
    _queue = Queue.Queue()
    _poll_interval = 10

    def __init__(self, interval=10):
        self._queue = Queue.Queue()
        self._poll_interval = interval

    def put_job(self, job):
        self._queue.put(job)

    def get_job(self):
        return self._queue.get(True, 2)

    def task_done(self):
        self._queue.task_done()

    def run_queue(self, verbose=False):
        while True:
            try:
                job = self.get_job()
                self.task_done()
                result = job.submit()
                if result and verbose:
                    print 'Dependent job submitted'
                else:
                    self.put_job(job)
                time.sleep(self._poll_interval)
            except Queue.Empty:
                if verbose:
                    print 'Queue is empty'
                    break
            except RuntimeError:
                if verbose:
                    print '**** Job dependency failed!'
                continue
            except KeyboardInterrupt:
                print "**** Interupted!"
