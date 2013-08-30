#!/usr/bin/env python
from foundation import FoundationApi, FoundationJob, DependentJob
import time


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
    dependent_job_queue = DependentJob.DependencyQueue(interval=2)
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
        dependent_job_queue.put_job(dependent_job)
    #work_requests = queuedpool.makeRequests(DependentJob.DependentJob.submit,
    #                                        dependent_jobs,
    #                                        print_result, handle_exception)
    dependent_job_queue.run_queue(True)

if __name__ == "__main__":
    main()
