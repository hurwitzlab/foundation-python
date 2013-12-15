#!/usr/bin/env python
import json
import requests
from requests.adapters import HTTPAdapter
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
    session = ''
    BASEURL = 'https://foundation.iplantcollaborative.org'
    AUTH = '/auth-v1/'
    AUTH_RENEW = '/auth-v1/renew'
    AUTH_LIST = '/auth-v1/list'
    APPS = '/apps-v1/apps/'
    APPS_LIST = '/apps-v1/apps/list'
    JOBS_LIST = '/apps-v1/jobs/list'
    JOBS_LIST_STATUS = '/apps-v1/jobs/list/status/'
    APPS_LIST_NAME = '/apps-v1/apps/name/'
    IO = '/io-v1/io/'
    IO_LIST = '/io-v1/io/list'
    JOB = '/apps-v1/job/'
    IPLANT_CREDENTIALS = ['/etc/iplant.foundationapi.json',
                          'iplant.foundationapi.json']
    IMICROBE_CREDENTIALS = ['/etc/imicrobe.foundationapi.json',
                            'imicrobe.foundationapi.json']

    def __init__(self):
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        self.session = s

    def validate(self, userid, password):
        try:
            response = requests.get(self.BASEURL + self.AUTH, auth=(userid,
                                    password))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def authenticate(self, userid, password, lifetime=172800):
        try:
            payload = {'lifetime': lifetime}
            response = requests.post(self.BASEURL + self.AUTH, auth=(userid,
                                     password), data=payload)
            print response
            return_data = response.json()
            self.token = return_data['result']['token']
            self.userid = return_data['result']['username']
            self.password = password
            #self.authrenewed = return_data['result']['renewed']
            renewed = int(return_data['result']['renewed'])
            self.authrenewed = datetime.datetime.fromtimestamp(renewed)
            created = int(return_data['result']['created'])
            self.authcreated = datetime.datetime.fromtimestamp(created)
            expires = int(return_data['result']['expires'])
            self.authexpires = datetime.datetime.fromtimestamp(expires)
            self.authremaining = return_data['result']['remaining_uses']
            self.authcreator = return_data['result']['creator']
            return return_data
        except requests.exceptions.RequestException as e:
            print e

    def authenticate_imicrobe(self):
        for item in self.IMICROBE_CREDENTIALS:
            if os.path.isfile(item):
                imicrobe_login = open(item)
                imicrobe_data = json.load(imicrobe_login)
                break
        return_data = self.authenticate(imicrobe_data['user'],
                                        imicrobe_data['password'])
        print return_data

    def proxy_authenticate(self, userid):
        values = {'username': userid}
        try:
            response = requests.post(self.BASEURL + self.AUTH, data=values,
                                     auth=(self.userid, self.password))
            return_data = response.json()
            self.token = return_data['result']['token']
            self.userid = return_data['result']['username']
            return return_data
        except requests.exceptions.RequestException as e:
            print e

    def _get_iplant_credentials(self):
        for item in self.IPLANT_CREDENTIALS:
            if os.path.isfile(item):
                iplant_login = open(item)
                iplant_data = json.load(iplant_login)
                break
        return iplant_data

    def super_authenticate(self, userid):
        iplant_data = self._get_iplant_credentials()
        return_data = self.authenticate(iplant_data['user'],
                                        iplant_data['password'])
        return_data = self.proxy_authenticate(userid)
        print return_data

    def reauth(self):
        try:
            return_data = self.authenticate(self.userid, self.password)
            return return_data
        except requests.exceptions.RequestException as e:
            print e
        except TypeError as e:
            print e
            print self
            print self.list_jobs('RUNNING')

    def auth_renew(self, token=''):
        if token == '':
            token = self.token
        values = {'token': token}
        try:
            response = requests.post(self.BASEURL + self.AUTH_RENEW,
                                     auth=(self.userid, self.password),
                                     data=values)
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def auth_list(self):
        try:
            response = requests.get(self.BASEURL + self.AUTH_LIST,
                                    auth=(self.userid, self.token))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def auth_delete(self, token):
        try:
            response = requests.delete(self.BASEURL + self.AUTH,
                                       auth=(self.userid, self.token))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def delete_all_tokens(self):
        list_data = self.auth_list()
        tokens = list_data['result']
        for token_item in tokens:
            if token_item['token'] != self.token:
                self.auth_delete(token_item['token'])

    def list_apps(self):
        try:
            response = requests.get(self.BASEURL + self.APPS_LIST,
                                    auth=(self.userid, self.token))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def list_app_ids(self):
        applist = self.list_apps()
        appids = []
        for app in applist['result']:
            if 'id' in app:
                appids.append(app['id'])
        return appids

    def find_app_by_name(self, name):
        try:
            response = requests.get(self.BASEURL + self.APPS_LIST_NAME + name,
                                    auth=(self.userid, self.token))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

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
        try:
            response = requests.get(self.BASEURL + self.JOBS_LIST,
                                    auth=(self.userid, self.token))
            return response.json()
        except requests.exceptions.RequestException as e:
            print e

    def run_job(self, foundation_job):
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
        try:
            results = requests.post(self.BASEURL + self.JOB, data=values,
                                    auth=(self.userid, self.token))
            results_json = results.json()
            foundation_job.job_status = results_json
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def job_status(self, id):
        try:
            results = self.session.get(self.BASEURL + self.JOB + str(id),
                                       auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def job_output_list(self, id, path):
        try:
            results = self.session.get(self.BASEURL + self.JOB + str(id) +
                                       '/output/list/' + path,
                                       auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def job_output(self, id, path):
        try:
            results = self.session.get(self.BASEURL + self.JOB + str(id) +
                                       '/output/' + path,
                                       auth=(self.userid, self.token))
            return results.text
        except requests.exceptions.RequestException as e:
            print e

    def kill_job(self, id):
        try:
            results = self.session.delete(self.BASEURL + self.JOB + id,
                                          auth=(self.userid, self.password))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

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
        try:
            results = requests.get(self.BASEURL + self.JOBS_LIST_STATUS +
                                   status, auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def app_permissions(self, id):
        try:
            results = requests.get(self.BASEURL + self.APPS + id + '/share',
                                   auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def make_directory(self, path):
        values = {'dirName': path, 'action': 'mkdir'}
        try:
            results = requests.put(self.BASEURL + self.IO + self.userid +
                                   '/analyses', data=values,
                                   auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e

    def upload_file(self, path, infile):
        values = {'fileToUpload': infile,
                  'fileType': 'fileType=FASTA-0'}
        print self.IO + self.userid + '/analyses/' + path
        try:
            results = requests.post(self.BASEURL + self.IO + self.userid +
                                    '/scratch/' + path, data=values,
                                    auth=(self.userid, self.token))
            return results.json()
        except requests.exceptions.RequestException as e:
            print e
