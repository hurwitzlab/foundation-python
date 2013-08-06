#!/usr/bin/env python
from foundation import FoundationApi , FoundationJob
from optparse import OptionParser
import fileinput

def main():

	parser=OptionParser()
	parser.add_option("-u", "--username", dest="username",
                  help="Username", type="string")
	parser.add_option("-p", "--password", dest="password",
                  help="Password", type="string")
	parser.add_option("-i", "--inputFile", dest="inputFile",
                  help="Input File with input fields and values", metavar="FILE")
	parser.add_option("-P", "--paramFile", dest="paramFile",
                  help="Parameters File with param fields and values", metavar="FILE")

	parser.add_option("-o", "--outputFile", dest="outputFile",
                  help="Output File with fields and values", metavar="FILE")

	parser.add_option("-a", "--app", dest="app",
                  help="Application Name to be run", type="string")

	parser.add_option("-r", "--runTag", dest="runTag",
                  help="Runtag for the application instance", type="string")

	parser.add_option("-d", "--dependency", dest="dependency",
                  help="Whether submitted job is required for next job to start", type="string")

	parser.add_option("-A", "--archive", dest="archive",
                  help="Whether to archive output true/false", type="string")

	parser.add_option("-x", "--archivepath", dest="archivepath",
                  help="Where to archive job files", type="string")

	(options, args)=parser.parse_args()

	if options.username == None :
		raise TypeError('username missing from command-line.')

	if options.password == None :
                raise TypeError('password missing from command-line.')

	if options.app == None :
                raise TypeError('Application name missing from command-line.')
	
	if options.runTag == None :
                raise TypeError('runTag missing from command-line.')

	api=FoundationApi.FoundationApi()
	# Put in your iPlant userid and password
	api.authenticate(options.username, options.password)

	job_status = ''

	inputs={}
	parameters={}
	outputs={}
	archivepath= ''

	# read input file and generate input dictionary
	for line in fileinput.input([options.inputFile]):
		fieldi,temp,vali = line.partition('=')
		inputs[fieldi] = vali

	# read param file and generate parameters dictionary
	for line in fileinput.input([options.paramFile]):
        	fieldp,temp,valp = line.partition('=')
        	parameters[fieldp] = valp

	# read output file and generate output dictionary
	if options.outputFile != None :
		for line in fileinput.input([options.outputFile]):
        		fieldo,temp,valo = line.partition('=')
        		outputs[fieldo] = valo

	if options.archivepath != None :
		archivepath = options.archivepath


	job = FoundationJob.FoundationJob(api, options.app, options.runTag, 
				archive=options.archive, inputs=inputs, parameters=parameters, outputs=outputs, archive_path=archivepath)

	job.submit()

	job_status=job.api.run_job(job)

	fo = open(options.runTag + '.all', "a")
	fo.write( str(job.job_status['result']['id']) + "\n")

	if options.dependency == 'true':
		# need to store job id for polling only if there is dependency on this job
		fo = open(options.runTag + '.dependency', "w")
		fo.write( str(job.job_status['result']['id']) + "\n")

	# write this job id to a dependency file and the subsequent job will look for this id in finished job file or failure job file and proceed 
	# accordingly.
	# We need to maintain 4 different jobfiles for a pipeline instance i.e for a runtag
	# 1) All jobs submitted for that runtag - runtag.all
	# 2) jobs pending as dependency - runtag.dependency
 
if __name__ == "__main__":
	main()

