#!/usr/bin/env python
import time
import datetime
## This pipeline runs the following steps 
## 
##  1- preprocess the fasta file(s) to create job array input file 
##  2- set up the blast output dirs
##  3- run blast against the set of databases and parse (in blastdbs file)
##  4- cleanup interim files and concatenate the results 

date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
fadir = '/rsgrps1/mbsulli/bioinfo/data/processed2/' + date + '/fasta/trimmed'
finaldir = '/rsgrps1/mbsulli/bioinfo/blastdata2/' + date
SCRIPTS= findir + '/scripts'
JOBS=100