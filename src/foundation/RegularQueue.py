#!/usr/bin/env python
import Queue
import time
from datetime import datetime
from datetime import timedelta

FAILED_STATUSES = ['KILLED', 'FAILED', 'STOPPED', 'ARCHIVING_FAILED']


class TooManyFailures(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RegularQueue():
    _queue = Queue.Queue()
    _monitor_queue = Queue.Queue()
    _poll_interval = 10
    failures = 0
    _failures_before_quit = 3
    verbose = False
    finished_jobs = []
    failed_jobs = []
    fapi = ''

    def __init__(self, fapi, interval=10, failures=3, verbose=False):
        self._queue = Queue.Queue()
        self._monitor_queue = Queue.Queue()
        self._poll_interval = interval
        self._failures_before_quit = failures
        self.verbose = verbose
        self.fapi = fapi

    def put_job(self, job):
        self._queue.put(job)

    def get_job(self):
        return self._queue.get(True, 2)

    def monitor_job(self, job):
        self._monitor_queue.put(job)

    def get_monitor_job(self):
        return self._monitor_queue.get(True, 2)

    def task_done(self):
        self._queue.task_done()

    def monitor_task_done(self):
        self._monitor_queue.task_done()

    def increment_failures(self, job):
        self.failed_jobs.append(job)
        self.failures += 1
        if self.verbose:
            jobid = job.job_status['result']['id']
            status = job.job_status['result']['status']
            print 'Job ' + str(jobid) + ' has status ' + status
        if self.failures >= self._failures_before_quit:
            if self.verbose:
                print '**** Too many job failures!'
            raise TooManyFailures(self.failures)

    def run_queue(self):
        while True:
            try:
                job = self.get_job()
                result = job.submit()
                if result:
                    self.monitor_job(job)
                    if self.verbose:
                        jobid = job.job_status['result']['id']
                        print 'Job ' + str(jobid) + ' submitted'
                else:
                    # There was no result returned
                    # so we return the job to the queue
                    self.put_job(job)
                self.task_done()
                time.sleep(self._poll_interval)
            except Queue.Empty:
                if self.verbose:
                    print 'All jobs have been submitted.'
                break
            except RuntimeError:
                # The job our current job was dependent on has failed
                # We tell the queue the task is done and we don't return it
                # to the queue
                self.task_done()
                self.increment_failures(job)
                continue
            except KeyboardInterrupt:
                print "**** Interupted!"
        while True:
            try:
                d1 = self.fapi.authexpires
                d2 = datetime.now()
                if (d1 - d2) < timedelta(hours=2):
                    print 'Attempting to super authenticate'
                    self.fapi.super_authenticate('imicrobe')
                    if self.verbose:
                        print 'Authentication token renewed'
                print 'get_monitor_job'
                job = self.get_monitor_job()
                print 'update_status()'
                job.update_status()
                result = job.job_status['result']
                print result
                if result is None:
                    self.monitor_job(job)
                elif result['status'] == 'ARCHIVING_FINISHED':
                    self.finished_jobs.append(job)
                elif result['status'] in FAILED_STATUSES:
                    self.increment_failures(job)
                else:
                    jobid = str(result['id'])
                    status = result['status']
                    if self.verbose:
                        print 'Job ' + jobid + ' has status ' + status
                    self.monitor_job(job)
                self.monitor_task_done()
                time.sleep(self._poll_interval)
            except Queue.Empty:
                if self.verbose:
                    print 'All jobs have finished.'
                break
