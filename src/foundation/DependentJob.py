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
        self.job_status = {'result': {'status': 'DEPENDENCY_WAITING'}}

    def update_status(self):
        if self.job_status['result']['status'] == 'DEPENDENCY_WAITING':
            return 'DEPENDENCY_WAITING'
        elif self.job_status['result']['status'] == 'DEPENDENCY_FAILED':
            return 'DEPENDENCY_FAILED'
        else:
            return super(DependentJob, self).update_status()

    def job_dependencies_failed(self):
        status = self.job_dependency.job_status['result']['status']
        if status in FAILED_STATUSES:
            self.job_status = {'result': {'status': 'DEPENDENCY_FAILED'}}
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
    failures = 0
    _failures_before_quit = 3

    def __init__(self, interval=10, failures=3):
        self._queue = Queue.Queue()
        self._poll_interval = interval
        self._failures_before_quit = failures

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
                result = job.submit()
                if result:
                    if verbose:
                        print 'Dependent job submitted'
                else:
                    # There was no result returned becuase the job dependencies
                    # were not fullfilled so we return the job to the queue
                    self.put_job(job)
                self.task_done()
                time.sleep(self._poll_interval)
            except Queue.Empty:
                if verbose:
                    print 'Queue is empty'
                    break
            except RuntimeError:
                # The job our current job was dependent on has failed
                # We tell the queue the task is done and we don't return it
                # to the queue
                self.task_done()
                self.failures += 1
                if self.failures >= self._failures_before_quit:
                    break
                if verbose:
                    print '**** Job dependency failed!'
                continue
            except KeyboardInterrupt:
                print "**** Interupted!"
