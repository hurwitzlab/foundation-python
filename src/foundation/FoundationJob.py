#!/usr/bin/env python
import FoundationApi

FAILED_STATUSES = ['KILLED', 'FAILED', 'STOPPED', 'ARCHIVING_FAILED']


class FoundationJob(object):
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

    def __init__(self, api, software_name, job_name, processor_count=1,
                 max_memory=1, requested_time='1:00:00',
                 callback_url='', archive='false', archive_path='',
                 inputs=[], outputs=[], parameters=[]):
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
        return self.job_status

    def update_status(self):
        try:
            job_status = self.api.job_status(self.job_status['result']['id'])
            if job_status:
                self.job_status = job_status
        except TypeError as e:
            print "TypeError({0}): {1}".format(e.errorno, e.strerror)
        return self.job_status


class TooManyFailures(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
