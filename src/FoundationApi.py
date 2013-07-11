#!/usr/bin/env python
import base64
import simplejson as json
import requests

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
	APPS_LIST = '/apps-v1/apps/list'
	JOBS_LIST = '/apps-v1/jobs/list'
	IO_LIST = '/io-v1/io/list'
	JOB = '/apps-v1/job'
			
	def validate(self, userid, password):
		response = requests.get(self.BASEURL + self.AUTH, auth=(userid, password))
		return response.json()
		
	def authenticate(self, userid, password):
		response = requests.post(self.BASEURL + self.AUTH, auth=(userid, password))
		return_data = response.json()
		self.token = return_data['result']['token']
		self.userid = return_data['result']['username']
		self.password = password
		self.authrenewed = return_data['result']['renewed']
		self.authcreated = return_data['result']['created']
		self.authexpires = return_data['result']['expires']
		self.authremaining = return_data['result']['remaining_uses']
		self.authcreator = return_data['result']['creator']
		return return_data
		
	def auth_renew(self, token):
		values = {'token' : token}
		response = requests.post(self.BASEURL + self.AUTH_RENEW, auth=(self.userid, self.password),
					data=values)
		return response.json()
		
	def auth_list(self):
		response = requests.get(self.BASEURL + self.AUTH_LIST, auth=(self.userid, self.token))
		return response.json()
	
	def auth_delete(self, token):
		response = requests.delete(self.BASEURL + self.AUTH, auth=(self.userid, self.token))
		return response.json()
		
	def delete_all_tokens(self):
		list_data = self.auth_list()
		tokens = list_data['result']
		for token_item in tokens:
			if token_item['token'] != self.token:
				self.auth_delete(token_item['token'])
				
	def list_apps(self):
		response = requests.get(self.BASEURL + self.APPS_LIST, auth=(self.userid, self.token))
		return response.json()
					
	def past_jobs(self):
		response = requests.get(self.BASEURL + self.JOBS_LIST, auth=(self.userid, self.token))
		return response.json()
		
	def run_job(self):
		values = {'softwareName': 'head-stampede-5.97u2', 'jobName': 'Head test', 
					'inputFile': '/iplant/home/dboss/all.fastaq', 'requestedTime': '1:00:00',
					'numberOfLines': '5'}
		results = requests.post(self.BASEURL + self.JOB, data=values, auth=(self.userid, self.token))
		return results.json()
		
	def list_files(self, path):
		url = self.BASEURL + self.IO_LIST + path
		response = requests.get(url, auth=(self.userid, self.token))
		return response.json()