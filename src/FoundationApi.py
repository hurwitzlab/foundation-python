#!/usr/bin/env python
import urllib, urllib2, base64
import simplejson as json
import requests

#from poster.encode import multipart_encode
#from poster.streaminghttp import register_openers

class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={},\
        origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,\
                 origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)

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
	baseurl = 'https://foundation.iplantcollaborative.org'

	def get_content_type(filename):
	    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
	
	
	def auth_init(self, suburl, userid, password):
		req = urllib2.Request(self.baseurl + suburl)
		base64string = base64.encodestring('%s:%s' % (userid, password)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		return req

	def auth_init_user(self, suburl, userid, password):
		req = urllib2.Request(self.baseurl + suburl + userid + path)
		base64string = base64.encodestring('%s:%s' % (userid, password)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		return req	
	
	def auth_init_del(self, suburl, userid, token):
		req = RequestWithMethod(self.baseurl + suburl, 'DELETE')
		base64string = base64.encodestring('%s:%s' % (userid, token)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		return req
		
	def validate(self, userid, password):
		suburl = '/auth-v1/'
		req = self.auth_init(suburl, userid, password)
		response = urllib2.urlopen(req)
		return_data = json.load(response)
		return return_data
		
	def authenticate(self, userid, password):
		suburl = '/auth-v1/'
		req = self.auth_init(suburl, userid, password)
		postdata = ''
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		return_data = json.load(response)
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
		suburl = '/auth-v1/renew'
		req = self.auth_init(suburl, self.userid, self.password)
		values = {'token' : token}
		postdata = urllib.urlencode(values)
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		return_data = json.load(response)
		return return_data
		
	def auth_list(self):
		suburl = '/auth-v1/list'
		req = self.auth_init(suburl, self.userid, self.token)
		response = urllib2.urlopen(req)
		return_data = json.load(response)
		return return_data
	
	def auth_delete(self, token):
		suburl = '/auth-v1/'
		req = self.auth_init_del(suburl, self.userid, token)
		postdata = ''
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		return_data = json.load(response)
		return return_data
		
	def delete_all_tokens(self):
		list_data = self.auth_list()
		tokens = list_data['result']
		for token_item in tokens:
			if token_item['token'] != self.token:
				self.auth_delete(token_item['token'])
				
	def list_apps(self):
		suburl = '/apps-v1/apps/list'
		req = self.auth_init(suburl, self.userid, self.token)
		response = urllib2.urlopen(req)
		return_data = json.load(response)
		return return_data
					
	def past_jobs(self):
		suburl = '/apps-v1/jobs/list'
		req = urllib2.Request(self.baseurl + suburl)
		base64string = base64.encodestring('%s:%s' % (self.userid, self.token)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		response = urllib2.urlopen(req)
		return_data = json.load(response)
		return return_data
		
	def run_job(self):
		suburl = '/apps-v1/job'
		base64string = base64.encodestring('%s:%s' % (self.userid, self.token)).replace('\n', '')
		headers = {'Authorization': "Basic %s" % base64string}
		values = {'softwareName': 'head-stampede-5.97u2', 'jobName': 'Head test', 
					'inputFile': '/iplant/home/dboss/all.fastaq', 'requestedTime': '1:00:00',
					'numberOfLines': '5'}
		postdata = urllib.urlencode(values)
		#req = urllib2.Request(self.baseurl + suburl, headers=headers)
		results = requests.post(self.baseurl + suburl, data=values, headers=headers)
		return results.json()
		#return return_data
		
	def list_files(self, path):
		suburl = '/io-v1/io/list'
		url = self.baseurl + suburl + path
		req = urllib2.Request(url)
		print(url)
		base64string = base64.encodestring('%s:%s' % (self.userid, self.token)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		response = urllib2.urlopen(req)
		return_data = json.load(response)
		return return_data