#!/usr/bin/python

import cherrypy
from Cheetah.Template import Template

class ExpensesServer(object):
	@cherrypy.expose
	def index(self, version=None, host=None, domain=None, *args, **kwargs):
		t = Template(file='index.tmpl')
		return str(t)
	#enddef
#endclass

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 8765
cherrypy.quickstart(ExpensesServer())
