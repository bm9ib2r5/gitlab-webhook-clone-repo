#!/usr/bin/python
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import commands
import json
import logging
import logging.handlers
import os
import re
import shutil
import subprocess
import sys
import threading

############# CONFIG
deployrootdir="/export/www/x2"
gitserver="git@10.11.11.84:devs/"
deployhost="user@localhost"
repositories = ['poligon.pl', 'test.pl']
############# LOGGING
logging.basicConfig(filename='/tmp/gitlab-webhook-clone-repo.log',level=logging.DEBUG,format='[ %(thread)d ] %(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S ')

####################

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        message =  threading.currentThread().getName()
	infomsg = " Just Gitlab webhook receiver. Nothing here"
        self.wfile.write(message+infomsg)
        self.wfile.write('\n')
        return
    def do_POST(self):
        """
            receives post, handles it
        """
        message = 'OK'
        self.rfile._sock.settimeout(5)
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.send_header("Content-length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)

        text = json.loads(data_string)
        out = (text['ref'])
        outb = out.split('/')

	branch = outb[2]
	repository=(text['repository']['name'])
	action=(text['object_kind'])
	#logging.info(" ")
	#logging.info("====== BRANCH: "+branch+" REPOSITORY: "+repository+" ACTION: "+action+"=====")
	print(" ")
	print('===' + ' BRANCH: '+branch+' REPOSITORY: '+repository+' ACTION: '+action)

	deploydir=deployrootdir+'/'+repository
	if repository in repositories:
		print('Repository'+repository+' supported')
		if action == "push":
			checkdestdir=''.join(['ssh ',deployhost,' " [ -d ', deploydir, ' ]"'])
			retvalue=os.system(checkdestdir)
			if retvalue != 0:
				print('Creating: '+deploydir)
				createdestdir=''.join(['ssh ',deployhost, 'mkdir', deploydir])
				retvalue=os.system(createdestdir)
				if retvalue != 0:
					print('Error creating: '+deploydir)

			DIR_NAME=deploydir+'/'+branch
			REMOTE_URL=gitserver+repository+'.git'
		
			checkbranchdir=''.join(['ssh ', deployhost, ' " [ -d ', DIR_NAME, ' ]"'])
			retvalue=os.system(checkbranchdir)
			if retvalue != 0:
				gitclone=''.join(['ssh ' ,deployhost, ' git clone ',REMOTE_URL,' ',DIR_NAME])
				#logging.info('Clonning repository: '+REMOTE_URL+' to '+DIR_NAME)
				print('Clonning repository: '+REMOTE_URL+' to '+DIR_NAME)
				print gitclone
				retvalue=os.system(gitclone)
				if retvalue != '0':
					#logging.error("repository clone failed!")
					print("repository clone failed!")

			else: 
				gitsetremote=''.join(['ssh ',deployhost,' git --git-dir=', DIR_NAME,'/.git --work-tree=',DIR_NAME, ' remote set-url origin ', REMOTE_URL])
				gitfetch=''.join(['ssh ',deployhost,' git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune'])
				gitcheckout=''.join(['ssh ',deployhost,' git --git-dir=',DIR_NAME,'/.git --work-tree=',DIR_NAME,' checkout --quiet --force ',branch])
				githardreset=''.join(['ssh ',deployhost,' git --git-dir=',DIR_NAME,'/.git --work-tree=',DIR_NAME,' reset --quiet --hard origin/',branch])
				gitclean=''.join(['ssh ',deployhost,' git --git-dir=',DIR_NAME,'/.git --work-tree=',DIR_NAME,' clean --quiet --force -d -x'])
				print gitsetremote
				#print gitfetch
				#print gitcheckout
				#print githardreset
				#print gitclean

				#logging.info('Work directory: ' +DIR_NAME)
				#logging.info('Set remote: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' remote set-url origin '+REMOTE_URL )
				print('Work directory: ' +DIR_NAME)
				print('Set remote: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' remote set-url origin '+REMOTE_URL )
				retvalue=os.system(gitsetremote)
				if retvalue != 0:
					logging.error("Set remote failed!")
					print("Set remote failed!")
				#print retvalue

				#logging.info('Fetch: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune')
				print('Fetch: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune')
				retvalue=os.system(gitfetch)
				if retvalue != 0:
				#	logging.error("Git fetch failed!")
					print("Git fetch failed!")
				#print retvalue

				#logging.info('Checkout: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' checkout --quiet --force '+branch)
				print('Checkout: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' checkout --quiet --force '+branch)
				retvalue=os.system(gitcheckout)
				if retvalue != 0:
					logging.error("Git checkout failed!")
					print("Git checkout failed!")
				#print retvalue

				#logging.info('Hard reset: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' reset --quiet --hard origin/'+branch)
				print('Hard reset: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' reset --quiet --hard origin/'+branch)
				retvalue=os.system(githardreset)
				if retvalue != 0:
					logging.error("Git hard reset failed!")
					print("Git hard reset failed!")
				#print retvalue

				#logging.info('Clean: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' clean --quiet --force -d -x')
				print('Clean: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' clean --quiet --force -d -x')
				retvalue=os.system(gitclean)
				if retvalue != 0:
					logging.error("Git clean failed!")
					print("Git clean failed!")
				#print retvalue
		else:
			print "Action not supported"
			#logging.info("Action not supported")

		#logging.info(" ")
		print(" ")
	else: 
		print('Repository '+repository+' not supported')
		

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8888), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
