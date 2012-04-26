#!/usr/bin/python

import psycopg2
import psycopg2.extras
import cherrypy
from Cheetah.Template import Template
import datetime

conn = psycopg2.connect("dbname=expenses user=expenses password=expenses")
#cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def user_validation(username=None, password=None):
	c = cherrypy.request.cookie
	if not username and 'username' in c: username = c['username'].value
	if not password and 'password' in c: password = c['password'].value

	if not username: return
	if not password: return

	cur = conn.cursor()
	cur.execute('SELECT id,name,password FROM users WHERE name=%s;', (username, ))
	if cur.rowcount != 1: return
	i,u,p = cur.fetchone()
	cur.close()

	if p != password: return None

	return i
#enddef

class ExpensesServer(object):
	@cherrypy.expose
	def index(self, show_last=None, date=None, category=None, note=None, amount=None, date_until=None, *args, **kwargs):
		message = ''

		user_id = user_validation()
		if not user_id: raise cherrypy.HTTPRedirect('/login')

		if not show_last: show_last = 5

		if amount:
			try: amount = float(amount)
			except:
				amount = None
				message = 'not a number!'
			#endtry
		#endif

		if not date_until: date_until = None

		cur = conn.cursor()
		if date and category and note and amount:
			cur.execute('insert into expenses(date, category, note, amount, user_id, date_until) values (%s, %s, %s, %s, %s, %s);', (date, category, note, amount, user_id, date_until))
			conn.commit()

			date = None
			category = None
			note = None
			amount = None
			date_until = None

			message = 'inserted %s' % cur.lastrowid
		#endif

		cur.execute("select id,date,category,note,amount,date_until from expenses WHERE user_id=%s order by id desc limit %s;", (user_id, show_last))
		ii = cur.fetchall()
		cur.close()
		ii = reversed(ii)

		if not date: date = datetime.datetime.now().strftime('%Y-%m-%d')
		if not category: category = ''
		if not note: note = ''
		if not amount: amount = ''

		t = Template(file='index.tmpl')
		t.show_last = show_last
		t.message = message
		t.itemss = ii
		t.date = date
		t.category = category
		t.note = note
		t.amount = amount
		t.date_until = date_until
		return str(t)
	#enddef

	@cherrypy.expose
	def list(self):
		dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		dict_cur.execute('SELECT * FROM expenses;')
		a = dict_cur.fetchone()
		print a.keys()
		dict_cur.close()
		return ''
	#enddef

	@cherrypy.expose
	def login(self, username=None, password=None):
		message = ''

		user_id = user_validation(username, password)
		if user_id:
			c = cherrypy.response.cookie
			c['username'] = username
			c['password'] = password
			message = 'ok!'
		else:
			message = 'not ok!'
		#endif

		# TODO: hack to prevent cursor leak
		if message == 'ok!':
			raise cherrypy.HTTPRedirect('/')
		#endif

		t = Template(file='login.tmpl')
		t.message = message
		t.username = username
		t.password = password
		return str(t)
	#enddef

	@cherrypy.expose
	def logout(self):
		c = cherrypy.response.cookie
		c['username'] = ''
		c['username']['expires'] = 0
		c['password'] = ''
		c['password']['expires'] = 0
		raise cherrypy.HTTPRedirect('/')
	#enddef

	@cherrypy.expose
	def suggest(self, key, text, limit=5):
		user_id = user_validation()
		if not user_id: raise cherrypy.HTTPRedirect('/login')

		cur = conn.cursor()
		# TODO: injection!
		sql = 'select distinct('+key+') from expenses where user_id=%s and '+key+' like %s limit %s;'
		cur.execute(sql, (user_id, text+'%', limit))
		if cur.rowcount == 0: return 'EMPTY'
		ii = cur.fetchall()
		cur.close()
		ii = (i[0] for i in ii)

		t = Template(file='suggest.tmpl')
		t.name = key
		t.itemss = ii
		return str(t)
	#enddef

	@cherrypy.expose
	def report(self, days=None):
		user_id = user_validation()

		if not user_id: raise cherrypy.HTTPRedirect('/login')

		if not days: days = 30

		cur = conn.cursor()
		cur.execute('select sum(amount) from expenses where user_id=%s and current_date - date < %s;', (user_id, days))
		total = cur.fetchone()[0]

		sql = 'select category,sum(amount) as sum from expenses where user_id=%s and current_date - date < %s group by category order by sum desc;'
		cur.execute(sql, (user_id, days))
		ii = cur.fetchall()
		cur.close()

		t = Template(file='report.tmpl')
		t.days = days
		t.total = total
		t.itemss = ii
		return str(t)
	#enddef
#endclass

cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 8777
cherrypy.quickstart(ExpensesServer())

conn.close()
