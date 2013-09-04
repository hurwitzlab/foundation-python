#!/usr/bin/env python
import time
import datetime
from foundation import FoundationApi
## This pipeline runs the following steps
##
##  1- preprocess the fasta file(s) to create job array input file
##  2- set up the blast output dirs
##  3- run blast against the set of databases and parse (in blastdbs file)
##  4- cleanup interim files and concatenate the results

date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
fadir = '/rsgrps1/mbsulli/bioinfo/data/processed2/' + date + '/fasta/trimmed'
finaldir = '/rsgrps1/mbsulli/bioinfo/blastdata2/' + date
TEST_LIST = '/dboss/'
SCRIPTS = finaldir + '/scripts'
JOBS = 100
api = FoundationApi.FoundationApi()
# Put in your iPlant userid and password
with open('password') as f:
    credentials = [x.strip().split(':') for x in f.readlines()]
for username, password in credentials:
    api.authenticate(username, password)
file_list = api.list_files(TEST_LIST)
print "**** Files"
print file_list
dir_list = api.list_dirs(TEST_LIST)
print "**** Dirs"
print dir_list
