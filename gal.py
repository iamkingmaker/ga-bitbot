
"""
gal v0.01 

ga-bitbot system launcher

Copyright 2011 Brian Monkaba

This file is part of ga-bitbot.

    ga-bitbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ga-bitbot is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ga-bitbot.  If not, see <http://www.gnu.org/licenses/>.
"""

# genetic algo client launcher
__appversion__ = "0.01a"
print "ga-bitbot system launcher v%s"%__appversion__

WATCHDOG_TIMEOUT = 180 #seconds

import atexit
import sys
from subprocess import check_output as call, Popen, PIPE
import shlex
from os import environ
import os
from time import *

#open a null file to redirect output from the subprocesses 
fnull = open(os.devnull,'w')

print "Launching the xmlrpc server..."
Popen(shlex.split('python gene_server.py'),stdin=fnull, stdout=fnull, stderr=fnull)
sleep(3) #give the server time to start




# connect to the xml server
#
import gene_server_config
import xmlrpclib
import json
__server__ = gene_server_config.__server__
__port__ = str(gene_server_config.__port__)
server = xmlrpclib.Server('http://' + __server__ + ":" + __port__)  
print "Connected to",__server__,":",__port__

# create and register callback function to
# shutdown the system on exit.
# - after the xmlrpc server shuts down the clients
# will silently crash due to failed connections (not pretty but it works)
def shutdown():
	sys.stderr = fnull
	server.shutdown()

atexit.register(shutdown)



monitor = {}

print "Launching GA Clients..."


#collect system process PIDS for monitoring. 
#(not the same as system OS PIDs -- They are more like GUIDs as this is a multiclient distributed system) 
epl = json.loads(server.pid_list()) #get the existing pid list


launch = ['pypy gts.py 1 n','pypy gts.py 2 n','pypy gts.py 3 n','pypy gts.py 4 n','pypy gts.py 1 y','pypy gts.py 2 y','pypy gts.py 3 y','pypy gts.py 4 y']

for cmd_line in launch:
	Popen(shlex.split(cmd_line),stdin=fnull, stdout=fnull, stderr=fnull)
	sleep(2)
	cpl = json.loads(server.pid_list())	#get the current pid list
	npl = list(set(epl) ^ set(cpl)) 	#find the new pid(s)
	epl = cpl				#update the existing pid list
	monitor.update({npl[0]:cmd_line})	#store the pid/cmd_line combination
	print "Process Launched (PID:",npl[0],"CMD:",cmd_line,")"

print "\nMonitoring Processes..."
while 1:
	#process monitor loop
	for pid in monitor.keys():
		sleep(5)
		if server.pid_check(pid,WATCHDOG_TIMEOUT) == "NOK":
			#watchdog timed out
			print "WATCHDOG: PID",pid,"EXPIRED"
			#remove the expired PID
			server.pid_remove(pid)
			epl = json.loads(server.pid_list()) 	#get the current pid list
			cmd_line = monitor[pid]
			monitor.pop(pid)
			#launch new process
			Popen(shlex.split(cmd_line),stdin=fnull, stdout=fnull, stderr=fnull)
			sleep(2)
			#store new PID
			cpl = json.loads(server.pid_list())	#get the current pid list
			npl = list(set(epl) ^ set(cpl)) 	#find the new pid(s)
			epl = cpl				#update the existing pid list
			monitor.update({npl[0]:cmd_line})	#store the pid/cmd_line combination
			print "Process Launched (PID:",npl[0],"CMD:",cmd_line,")"



fnull.close()






"""
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 1 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 1 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 2 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 2 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 3 y"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 4 n"'))
Popen(shlex.split('gnome-terminal -x bash -c "pypy gts.py 4 y"'))
"""

