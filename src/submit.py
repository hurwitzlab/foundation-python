#!/usr/bin/env python
import argparse
import getpass
import urllib
import urllib2
import base64
import simplejson as json

parser = argparse.ArgumentParser(description='Submit and monitor cd-hit job.')
parser.add_argument('-u', dest='userid', type=str, required=True,
                   help='Your iPlant userid')
parser.add_argument('inputSeqs', type=str,
                   help='name of input sequence file on iPlant iRODS datastore')

args = parser.parse_args()
userid = args.userid
#password = getpass.getpass()
password = 'Bc455XHraRJw'
authurl = "https://foundation.iplantc.org/auth-v1"
#url = "https://foundation.iplantc.org/apps-v1/apps/form/cd-hit-4.6.1"
url = "https://foundation.iplantc.org/apps-v1/job/"
#authurl = "https://foundation.iplantc.org/"
#password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
#password_mgr.add_password(None, authurl, userid, password)
#handler = urllib2.HTTPBasicAuthHandler(password_mgr)
#handler = urllib2.HTTPBasicAuthHandler()
#handler.add_password(None, "https://foundation.iplantc.org/", 
#			userid,
#			password)
#opener = urllib2.build_opener(handler)
#urllib2.install_opener(opener)
req = urllib2.Request(url)
values = {'jobName' : 'foundationTest', 'softwareName' : 'cd-hit-4.6.1', 
          'requestedTime' : '01:00:00', 'maxMemory' : '45000',
          'callbackUrl' : '', 'archive' : '1',
          'archivePath' : '', 'inputSeqs' : args.inputSeqs,
          'memoryLimit' : '45000', 'globalSeqId' : '1',
          'outputName' : 'outfile.fa', 'alignCover' : '0.8', 'wordLength' : '4',
          'descLength' : '0' , 'bandwidth' : '0.6', 'algorithim' : '1',
          'threads' : '24', 'idThreshold' : '0.6'}
data = urllib.urlencode(values)
base64string = base64.encodestring('%s:%s' % (userid, password)).replace('\n', '')
req.add_header("Authorization", "Basic %s" % base64string)
req.add_data(data)
print 'This will be a', req.get_method(), 'request.'
opener = urllib2.build_opener()
results = opener.open(req)
print(results.read())
#returnData = json.load(results)
#result = returnData.get('')
#for item in result:
#	print item['name']