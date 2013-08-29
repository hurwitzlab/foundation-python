#!/usr/bin/env python
from foundation import FoundationApi, FoundationJob, DependentJob, queuedpool
import time
import Queue

def main():
    api = FoundationApi.FoundationApi()
    # Put in your iPlant userid and password
    with open('password') as f:
        credentials = [x.strip().split(':') for x in f.readlines()]
    for username, password in credentials:
        api.authenticate(username, password)
    # Change the file path to a file that you have access to
    inputs = {'inputFile': '/dboss/current-prot-universe.fa'}
    #inputs = {'query1': '/dboss/current-prot-universe.fa'}
    parameters = {'numberOfLines': '5'}
    #parameters = {'printLongestLine': 'true'}
    jobs = []
    submitted_jobs = []
    count = 0
    while (count < 2):
        test_job = FoundationJob.FoundationJob(api, 'head-stampede-5.97u2',
                                               'Head test', archive='true',
                                               inputs=inputs,
                                               parameters=parameters)
        #test_job = FoundationJob.FoundationJob(api, 'wc-1.00u1',
        #                                       'wc test',
        #                                       inputs=inputs,
        #                                       parameters=parameters)
        jobs.append(test_job)
        count += 1
    for job in jobs:
        print job.submit()
        time.sleep(2)
        print job.update_status()
        submitted_jobs.append(job)
    dependent_job_queue = Queue.Queue()
    for job in jobs:
        dependent_job = DependentJob.DependentJob(api, 'head-stampede-5.97u2',
                                                  'Head dep', archive='true',
                                                  inputs=inputs,
                                                  parameters=parameters,
                                                  job_dependency=job)
        #dependent_job = DependentJob.DependentJob(api, 'wc-1.00u1',
        #                                          'Head dep', archive='false',
        #                                          inputs=inputs,
        #                                          job_dependency=job)
        dependent_job_queue.put(dependent_job)
    #work_requests = queuedpool.makeRequests(DependentJob.DependentJob.submit,
    #                                        dependent_jobs,
    #                                        print_result, handle_exception)
    failed_jobs = []
    while True:
        try:
            job = dependent_job_queue.get(True, 2)
            dependent_job_queue.task_done()
            result = job.submit()
            if result:
                print 'Dependent job submitted'
            else:
                dependent_job_queue.put(job)
            time.sleep(2)
        except Queue.Empty:
            print 'Queue is empty'
            break
        except RuntimeError:
            print '**** Job dependency failed!'
            failed_jobs.append(job.job_dependency)
            failed_jobs.append(job)
            continue
        except KeyboardInterrupt:
            print "**** Interupted!"

if __name__ == "__main__":
    main()
