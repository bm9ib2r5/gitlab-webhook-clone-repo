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
sourcedir="/tmp/www"

############# LOGGING
logging.basicConfig(filename='/tmp/gitlab-webhook-clone-repo.log',level=logging.DEBUG,format='[ %(thread)d ] %(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S ')

####################

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        message =  threading.currentThread().getName()
	message2 = " Just Gitlab webhook receiver. Nothing here"
        self.wfile.write(message)
        self.wfile.write(message2)
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
        REMOTE_URL=(text['repository']['git_ssh_url'])
	action=(text['object_kind'])
        commitAfter=(text['after'])
        if commitAfter == "0000000000000000000000000000000000000000":
            action='deleteBranch'
	logging.info(" ")
	logging.info("====== BRANCH: "+branch+" REPOSITORY: "+repository+" ACTION: "+action+"=====")
	print(" ")
	print('===' + ' BRANCH: '+branch+' REPOSITORY: '+repository+' ACTION: '+action)

	repodir=sourcedir+'/'+repository
	DIR_NAME=repodir+'/'+branch

	if action == "push":	
		if not os.path.exists(repodir):
			os.mkdir(repodir)
			logging.info('Creating: '+repodir)

		if not os.path.exists(DIR_NAME):
			gitclone='git clone '+REMOTE_URL+' '+DIR_NAME
			logging.info('Clonning repository: '+REMOTE_URL+' to '+DIR_NAME)
			print('Clonning repository: '+REMOTE_URL+' to '+DIR_NAME)
			print gitclone
			retvalue=os.system(gitclone)
			if retvalue != '0':
				logging.error("repository clone failed!")

		if os.path.exists(DIR_NAME):
			gitsetremote='git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' remote set-url origin '+REMOTE_URL
			gitfetch='git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune'
			gitcheckout='git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' checkout --quiet --force '+branch
			githardreset='git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' reset --quiet --hard origin/'+branch
			gitclean='git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' clean --quiet --force -d -x'
			#print gitsetremote
			#print gitfetch
			#print gitcheckout
			#print githardreset
			#print gitclean

			logging.info('Work directory: ' +DIR_NAME)
			logging.info('Set remote: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' remote set-url origin '+REMOTE_URL )
			print('Work directory: ' +DIR_NAME)
			print('Set remote: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' remote set-url origin '+REMOTE_URL )
			retvalue=os.system(gitsetremote)
			if retvalue != 0:
				logging.error("Set remote failed!")
                                print("Error: Set remote failed!")
			#print retvalue

			logging.info('Fetch: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune')
			print('Fetch: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' fetch --quiet --all --prune')
			retvalue=os.system(gitfetch)
			if retvalue != 0:
				logging.error("Git fetch failed!")
                                print("Error: Git fetch failed!")
			#print retvalue

			logging.info('Checkout: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' checkout --quiet --force '+branch)
			print('Checkout: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' checkout --quiet --force '+branch)
			retvalue=os.system(gitcheckout)
			if retvalue != 0:
				logging.error("Git checkout failed!")
                                print("Error: Git checkout failed!")
			#print retvalue

			logging.info('Hard reset: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' reset --quiet --hard origin/'+branch)
			print('Hard reset: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' reset --quiet --hard origin/'+branch)
			retvalue=os.system(githardreset)
			if retvalue != 0:
				logging.error("Git hard reset failed!")
                                print("Error: Git hard reset failed!")
			#print retvalue

			logging.info('Clean: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' clean --quiet --force -d -x')
			print('Clean: git --git-dir='+DIR_NAME+'/.git --work-tree='+DIR_NAME+' clean --quiet --force -d -x')
			retvalue=os.system(gitclean)
			if retvalue != 0:
				logging.error("Git clean failed!")
                                print("Error: Git clean failed!")
			#print retvalue
	if action == "deleteBranch":	
	    if os.path.exists(DIR_NAME):
                logging.info ('Deleting directory: '+DIR_NAME)
                print ('Deleting directory: '+DIR_NAME)

                try:
                    shutil.rmtree(DIR_NAME)
                except OSError, e:
                    print ("Error: %s - %s." % (e.filename,e.strerror))
                    logging.error("Error: branch failed!")

	else:
            print ('Action: '+action+' not supported')
            logging.info('Action: '+action+' not supported')

	logging.info(" ")
	print(" ")
		

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8888), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
