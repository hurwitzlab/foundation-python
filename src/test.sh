#!/bin/bash

runtag=$3
failfile="$runtag.failed"

user=$1
pass=$2

if [ $# -lt 3 ] ; then
      echo "usage: test.sh <username> <password> <runtag>"
      exit 0
fi
# command line python call to submit jobs
python FoundationJobSubmit.py --username=$user --password=$pass --inputFile=input --paramFile=param --app=head-stampede-5.97u2 --runTag=$runtag --archive=true --dependency=true 

# command line python call to get status of all the jobs for pipeline instance
python PipelinesUtil.py --username=$user --password=$pass --status=true --runTag=$runtag

# command line python call to poll over job specified in dependency file
python PipelinesUtil.py --username=$user --password=$pass --poll=true --runTag=$runtag


if [ -f "$failfile" ]
then
	echo "Pipeline $runtag failed."
	exit
fi

# command line python call to poll over job specified in dependency file
#python PipelinesUtil.py --username=$user --password=$pass --output=true --runTag=$runtag

# here we can submit the next job, as there is no failed file which implies dependency is fullfilled.



