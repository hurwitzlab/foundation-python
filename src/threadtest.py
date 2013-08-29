#!/usr/bin/env python
from foundation import FoundationApi, FoundationJob, DependentJob, queuedpool
import time
import threading


def do_work(job):
    job.job_dependency.update_status()
    print(str(job.job_dependency.job_status['result']['id']) +
          ' ' + str(job.is_job_ready_to_run()))
    result = ''
    if job.is_job_ready_to_run():
        result = job.submit()
    elif job.job_dependencies_failed():
        raise RuntimeError("Job dependency failed")
    return result


def print_result(request, result):
    print "**** Result from request #%s: %r" % (request.requestID, result)


def handle_exception(request, exc_info):
    if not isinstance(exc_info, tuple):
        # Something is seriously wrong...
        print request
        print exc_info
        raise SystemExit
    print "**** Exception occured in request #%s: %s" % \
        (request.requestID, exc_info)


def main():
    api = FoundationApi.FoundationApi()
    # Put in your iPlant userid and password
    with open('password') as f:
        credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        api.authenticate(username, password)
    # Change the file path to a file that you have access to
    inputs = {'inputFile': '/dboss/current-prot-universe.fa'}
    parameters = {'numberOfLines': '5'}
    jobs = []
    submitted_jobs = []
    count = 0
    while (count < 2):
        test_job = FoundationJob.FoundationJob(api, 'head-stampede-5.97u2',
                                               'Head test', archive='true',
                                               inputs=inputs,
                                               parameters=parameters)
        jobs.append(test_job)
        count += 1
    for job in jobs:
        job.submit()
        time.sleep(2)
        job.update_status()
        submitted_jobs.append(job)
    dependent_jobs = []
    for job in jobs:
        dependent_job = DependentJob.DependentJob(api, 'head-stampede-5.97u2',
                                                  'Head dep', archive='true',
                                                  inputs=inputs,
                                                  parameters=parameters,
                                                  job_dependency=job)
        dependent_jobs.append(dependent_job)
    work_requests = queuedpool.makeRequests(DependentJob.DependentJob.submit,
                                            dependent_jobs,
                                            print_result, handle_exception)
    print "Creating thread pool with 2 worker threads."
    pool = queuedpool.ThreadPool(2)
    for work_request in work_requests:
        pool.putRequest(work_request)
        print "Work request #%s added." % work_request.requestID

    i = 0
    while True:
        try:
            time.sleep(0.5)
            pool.poll()
            print "Main thread working...",
            print "(active worker threads: %i)" % (threading.activeCount()-1, )
            i += 1
        except KeyboardInterrupt:
            print "**** Interrupted!"
            break
        except queuedpool.NoResultsPending:
            print "**** No pending results."
            break
    if pool.dismissedWorkers:
        print "Joining all dismissed worker threads..."
        pool.joinAllDismissedWorkers()


if __name__ == "__main__":
    main()
