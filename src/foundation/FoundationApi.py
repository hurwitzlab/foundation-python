#!/usr/bin/env python
import json
import requests
import datetime
import os


class FoundationApi:
    """Foundation Api class"""
    userid = ''
    password = ''
    token = ''
    authrenewed = ''
    authcreated = ''
    authexpires = ''
    authremaining = ''
    authcreator = ''
    BASEURL = 'https://foundation.iplantcollaborative.org'
    AUTH = '/auth-v1/'
    AUTH_RENEW = '/auth-v1/renew'
    AUTH_LIST = '/auth-v1/list'
    APPS = '/apps-v1/apps/'
    APPS_LIST = '/apps-v1/apps/list'
    JOBS_LIST = '/apps-v1/jobs/list'
    JOBS_LIST_STATUS = '/apps-v1/jobs/list/status/'
    APPS_LIST_NAME = '/apps-v1/apps/name/'
    IO_LIST = '/io-v1/io/list'
    JOB = '/apps-v1/job/'
    IPLANT_CREDENTIALS = ['/etc/iplant.foundationapi.json',
                          'iplant.foundationapi.json']

    def validate(self, userid, password):
        response = requests.get(self.BASEURL + self.AUTH, auth=(userid,
                                password))
        return response.json()

    def authenticate(self, userid, password):
        response = requests.post(self.BASEURL + self.AUTH, auth=(userid,
                                 password))
        return_data = response.json()
        self.token = return_data['result']['token']
        self.userid = return_data['result']['username']
        self.password = password
        #self.authrenewed = return_data['result']['renewed']
        self.authrenewed = datetime.datetime.fromtimestamp(int(return_data['result']['renewed']))
        self.authcreated = datetime.datetime.fromtimestamp(int(return_data['result']['created']))
        self.authexpires = datetime.datetime.fromtimestamp(int(return_data['result']['expires']))
        self.authremaining = return_data['result']['remaining_uses']
        self.authcreator = return_data['result']['creator']
        return return_data

    def proxy_authenticate(self, userid):
        values = {'username': userid}
        response = requests.post(self.BASEURL + self.AUTH, data=values,
                                 auth=(self.userid, self.password))
        return_data = response.json()
        self.token = return_data['result']['token']
        self.userid = return_data['result']['username']
        return return_data

    def super_authenticate(self, userid):
        for item in self.IPLANT_CREDENTIALS:
            if os.path.isfile(item):
                iplant_login = open(item)
                iplant_data = json.load(iplant_login)
                break
        return_data = self.authenticate(iplant_data['user'],
                                        iplant_data['password'])
        return_data = self.proxy_authenticate(userid)
        print return_data 

    def reauth(self):
        return_data = self.authenticate(self.userid, self.password)
        return return_data

    def auth_renew(self, token=''):
        if token == '':
            token = self.token
        values = {'token': token}
        response = requests.post(self.BASEURL + self.AUTH_RENEW,
                                 auth=(self.userid, self.password),
                                 data=values)
        return response.json()

    def auth_list(self):
        response = requests.get(self.BASEURL + self.AUTH_LIST,
                                auth=(self.userid, self.token))
        return response.json()

    def auth_delete(self, token):
        response = requests.delete(self.BASEURL + self.AUTH,
                                   auth=(self.userid, self.token))
        return response.json()

    def delete_all_tokens(self):
        list_data = self.auth_list()
        tokens = list_data['result']
        for token_item in tokens:
            if token_item['token'] != self.token:
                self.auth_delete(token_item['token'])

    def list_apps(self):
        response = requests.get(self.BASEURL + self.APPS_LIST,
                                auth=(self.userid, self.token))
        return response.json()

    def list_app_ids(self):
        applist = self.list_apps()
        appids = []
        for app in applist['result']:
            if 'id' in app:
                appids.append(app['id'])
        return appids

    def find_app_by_name(self, name):
        response = requests.get(self.BASEURL + self.APPS_LIST_NAME + name,
                                auth=(self.userid, self.token))
        return response.json()

    def print_app_parameters(self, name):
        applist = self.find_app_by_name(name)
        for app in applist['result']:
            if 'id' in app:
                print('App ID: ' + app['id'])
                print('\tInputs:')
                for input in app['inputs']:
                    print('\t\tID:' + input['id'])
                print('\tOutputs:')
                for output in app['outputs']:
                    print('\t\tID:' + output['id'])
                print('\tParameters:')
                for param in app['parameters']:
                    print('\t\tID:' + param['id'])

    def app_parameters(self, name):
        applist = self.find_app_by_name(name)
        for app in applist['result']:
            if 'id' in app:
                print json.dumps(app, indent=4, separators=(',', ': '))

    def past_jobs(self):
        response = requests.get(self.BASEURL + self.JOBS_LIST,
                                auth=(self.userid, self.token))
        return response.json()

    def run_job(self, foundation_job):
        #values = {'softwareName': 'head-stampede-5.97u2',
                   # 'jobName': 'Head test',
                   #'inputFile': '/dboss/current-prot-universe.fa',
                   # 'requestedTime': '1:00:00',
                   # 'numberOfLines': '5'}
        values = {'softwareName': foundation_job.software_name,
                  'jobName': foundation_job.job_name,
                  'processorCount': foundation_job.processor_count,
                  'maxMemory': foundation_job.max_memory,
                  'requestedTime': foundation_job.requested_time,
                  'callbackURL': foundation_job.callback_url,
                  'archive': foundation_job.archive,
                  'archivePath': foundation_job.archive_path}
        values.update(foundation_job.inputs)
        values.update(foundation_job.outputs)
        values.update(foundation_job.parameters)
        results = requests.post(self.BASEURL + self.JOB, data=values,
                                auth=(self.userid, self.token))
        results_json = results.json()
        foundation_job.job_status = results_json
        return results.json()

    def job_status(self, id):
        results = requests.get(self.BASEURL + self.JOB + str(id),
                               auth=(self.userid, self.token))
        return results.json()

    def kill_job(self, id):
        results = requests.delete(self.BASEURL + self.JOB + id,
                                  auth=(self.userid, self.password))
        return results.json()

    def kill_queued(self):
        results = []
        jobs_to_kill = self.list_jobs('QUEUED')
        for job in jobs_to_kill['result']:
            result = self.kill_job(str(job['id']))
            results.append(result)
        return results

    def _list_files(self, path):
        url = self.BASEURL + self.IO_LIST + path
        results = requests.get(url, auth=(self.userid, self.token))
        files_json = results.json()
        results = files_json['result']
        return results

    def list_files(self, path):
        results = self._list_files(path)
        files = []
        for result in results:
            if result['type'] == 'file':
                files.append(result['path'])
        return files

    def list_dirs(self, path):
        results = self._list_files(path)
        dirs = []
        for result in results:
            if result['type'] == 'dir':
                dirs.append(result['path'])
        return dirs

    def list_jobs(self, status):
        results = requests.get(self.BASEURL + self.JOBS_LIST_STATUS +
                               status, auth=(self.userid, self.token))
        return results.json()

    def app_permissions(self, id):
        results = requests.get(self.BASEURL + self.APPS + id + '/share',
                               auth=(self.userid, self.token))
        return results.json()
