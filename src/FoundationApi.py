#!/usr/bin/env python
import urllib, urllib2, base64
import simplejson as json

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
	baseurl = 'https://foundation.iplantc.org'
	
	def AuthInit(self, suburl, userid, password):
		req = urllib2.Request(self.baseurl + suburl)
		base64string = base64.encodestring('%s:%s' % (userid, password)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		return req
	
	def AuthInitDel(self, suburl, userid, token):
		req = RequestWithMethod(self.baseurl + suburl, 'DELETE')
		base64string = base64.encodestring('%s:%s' % (userid, token)).replace('\n', '')
		req.add_header("Authorization", "Basic %s" % base64string)
		return req
		
	def Validate(self, userid, password):
		req = self.AuthInit(suburl, userid, password)
		response = urllib2.urlopen(req)
		returnData = json.load(response)
		return returnData
		
	def Authenticate(self, userid, password):
		suburl = '/auth-v1/'
		req = self.AuthInit(suburl, userid, password)
		postdata = ''
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		returnData = json.load(response)
		self.token = returnData['result']['token']
		self.userid = returnData['result']['username']
		self.password = password
		self.authrenewed = returnData['result']['renewed']
		self.authcreated = returnData['result']['created']
		self.authexpires = returnData['result']['expires']
		self.authremaining = returnData['result']['remaining_uses']
		self.authcreator = returnData['result']['creator']
		return returnData
		
	def AuthRenew(self, token):
		suburl = '/auth-v1/renew'
		req = self.AuthInit(suburl, self.userid, self.password)
		values = {'token' : token}
		postdata = urllib.urlencode(values)
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		returnData = json.load(response)
		return returnData
		
	def AuthList(self):
		suburl = '/auth-v1/list'
		req = self.AuthInit(suburl, self.userid, self.token)
		response = urllib2.urlopen(req)
		returnData = json.load(response)
		return returnData
	
	def AuthDelete(self, token):
		suburl = '/auth-v1/'
		req = self.AuthInitDel(suburl, self.userid, token)
		postdata = ''
		req.add_data(postdata)
		response = urllib2.urlopen(req, postdata)
		returnData = json.load(response)
		return returnData
		
	def DeleteAllTokens(self):
		listData = self.AuthList()
		tokens = listData['result']
		for tokenItem in tokens:
			if tokenItem['token'] != self.token:
				self.AuthDelete(tokenItem['token'])
		
		
		