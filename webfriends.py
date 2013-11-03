#!/usr/bin/python2.7
import cgitb, subprocess, re, time, os, sys, json, smtplib
from flask import Flask, render_template, request
from werkzeug.contrib.cache import SimpleCache

cgitb.enable()

cache = SimpleCache()

app = Flask(__name__)      
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)

class Lab(object):
	name = ""
	computers = []
	directions = []
	state = ""
	users = []
	size = tuple()
	doors = {}
	total_user_number = 0

	def getUserNumber(self):
		number = 0
		for user in self.users:
			if self.users[user].zid:
				number+=int(self.users[user].zid[1:])
		return number

	def __init__(self, name, computers, directions, users, state, size, doors):
		self.name = name
		self.computers = computers
		self.directions = directions
		self.state = state
		self.users = users
		self.size = size
		self.doors = doors
		self.total_user_number = self.getUserNumber()

	def __str__(self):
		state = "open" if self.state else "closed"
		out = "Lab " + self.name + " is " + state + ".\n"
		out+= "It contains: \n"
		for i in self.users:
			if self.users[i].user_id != "":
				out+="\t"+self.users[i].name+"\n"
		return out

	def to_json(self):
		json = "{"
		json+= '"name": "'+self.name+'", '
		json+= '"state": "'+str(self.state)+'", '
		json+= '"users": ['
		for i in self.users:
			json+= "{"
			json+= '"user_id": "'+self.users[i].user_id+'", '
			json+= '"user_name": "'+self.users[i].name+'", '
			json+= '"user_zid": "'+self.users[i].zid+'", '
			json+= '"time_since_logged": "'+self.users[i].since_string+'"'
			json+= "},"
		json = json[:-1]
		json+= "]}"
		return json

class Computer(object):
	user_id = ""
	name = ""
	zid = ""
	since = time.struct_time
	since_string = ""
	
	def getData(self, user_id):
		user = {}
		if user_id != "":
			user_data = cache.get('user-'+user_id)
			if user_data is None:
				user_data = importData("pp",user_id)
				cache.set('user-'+user_id, user_data, timeout=60 * 60 *24 * 30 * 3)
			user_name_data = re.search(r'(?<=[^\bUser\b] Name : ).*', user_data)
			zid_data = re.search(r'z[0-9]+', user_data)
			user_zid = zid_data.group().strip()
			user_name = user_name_data.group().strip()
		else:
			user_zid = ""
			user_name = ""
		user['user_zid'] = user_zid
		user['user_name'] = user_name
		return user

	def __init__(self, user_id, since):
		self.user_id = user_id
		self.name = self.getData(user_id)['user_name']
		self.zid = self.getData(user_id)['user_zid']
		self.since = since
		self.since_string = time.strftime("%H:%M:%S %d/%m", since)

	def __str__(self):
		if self.user_id:
			out = "user_id: "+self.user_id+" name: "+self.name
		else:
			out = ""
		return out
	
def newComputer(user_id, since):
	computer = Computer(user_id, since)
	return computer

def newLab(name, computers, directions, users, state, size, doors):
	lab = Lab(name, computers, directions, users, state, size, doors)
	return lab

def importLabData(lab, refresh_time):
	
	lab_data = cache.get('lab-'+lab)
	if lab_data is None:
		lab_data = importData('/usr/local/bin/lab',lab)
		cache.set('lab-'+lab, lab_data, timeout=refresh_time)
	return lab_data


def importData(command, arguments):
	process = subprocess.Popen([command, arguments], stdout=subprocess.PIPE)
	out, err = process.communicate()
	return out

def getLabs(labs):
	lab_output = {}
	for lab in labs.keys():

		users = {}
		lab_list = importLabData(lab,60)
		for line in lab_list.splitlines():

			if line[0:3] == 'Lab':
				state_data = re.search(r'(?<=is )[\S]+', line)
				state_text = state_data.group().strip().rstrip(',')
				state = False if state_text == "CLOSED" else True
			else:

				comp_data = re.search(r'.*(?=:[\bUp\b\bDown\b])', line)

				if comp_data:
					comp_name = comp_data.group().strip()[:-2]
					comp_no = int(comp_name[-2:])
					user_data = re.search(r'(?<=[\bAllocated\b\bTentative\b]: )[\S]+', line)
					if user_data:
						user_name = user_data.group().strip()
					else:
						user_name = ""

					since_data = re.search(r'(?<=since ).*', line)
					if since_data:
						since_plus_year = since_data.group().strip()+" "+time.strftime("%Y")
						since = time.strptime(since_plus_year,"%d/%m;%H:%M:%S %Y")
					else:
						since = time.strptime(time.strftime("%d/%m;0:0:0 %Y"),"%d/%m;%H:%M:%S %Y")

					users[comp_no] = newComputer(user_name, since)

		lab_output.update({lab:newLab(lab,labs[lab]['grid_pos'],labs[lab]['directions'],users,state,labs[lab]['size'],labs[lab]['doors'])})

	return lab_output

def getStats(lab_data):
	stats = {}
	stats['high_lab_name'] = ""
	stats['high_lab_num'] = 0
	stats['low_lab_name'] = ""
	stats['low_lab_num'] = sys.maxint

	for lab in labs:
		if lab.total_user_number < stats['low_lab_num']:
			stats['low_lab_num'] = lab.total_user_number
			stats['low_lab_name']  = lab.name
		if lab.total_user_number > stats['high_lab_num']:
			stats['high_lab_num'] = lab.total_user_number
			stats['high_lab_name'] = lab.name

	return stats

def getJson(lab_data):
	json = "{"
	for i in lab_data:
		json+='"'+i+'": '
		json+=lab_data[i].to_json()
		json+=", "
	json = json[:-1]	
	json += "}"
	return json


@app.route('/')
def home():
	debug = request.args.get('debug')
	out = ""

	labs	=	{	"banjo": 	{
									"directions": 	['W','W','W','W','N','N','N','N','E','E','E','E','E','E','E','W','W','W'],
									"grid_pos": 	[(6, 1),(6, 2),(6, 3),(6, 4),(5, 5),(4, 5),(3, 5),(2, 5),(1, 4),(1, 3),(1, 2),(1, 1),(3, 1),(3, 2),(3, 3),(4, 3),(4, 2),(4, 1)],
									"size":			(8,7),
									"doors":		{
														'N':	[(6,0)]
													}
								},
					"oud": 		{
									"directions":	['SE','NE','SE','NE','SE','SW','NW','SW','NW','SW','SE','NE','SE','NE','SE','SW','NW','SW','NW'],
									"grid_pos":		[(5, 2),(5, 3),(5, 4),(5, 5),(5, 6),(3, 6),(3, 5),(3, 4),(3, 3),(3, 2),(2, 2),(2, 3),(2, 4),(2, 5),(2, 6),(0, 6),(0,5 ),(0, 4),(0, 3),(0, 2)],
									"size":			(6,7),
									"doors":		{
														'N':	[(4,0)]
													}
								},
					"guan": 	{
									"directions": 	['SW','NW','SW','NW','SW','NE','SE','NE','SE','SW','NW','SW','NW','N','NE','SE','SE','NE','SE','SE'],
									"grid_pos":		[(0,4),(0,3),(0,2),(0,1),(0,0),(2,0),(2,1),(2,2),(2,3),(3,3),(3,2),(3,1),(3,0),(4,0),(5,0),(5,1),(5,2),(5,3),(5,4),(3,6)],
									"size":			(6,7),
									"doors":		{
														'S':	[(1,6)]
													}
								},
					"erhu": 	{
									"directions":	['S','S','S','W','SW','NW','N','N','NE','E','E'],
									"grid_pos":		[(3,4),(2,4),(1,4),(0,2),(0,1),(0,0),(2,0),(3,0),(4,0),(4,1),(4,2)],
									"size":			(5,5),
									"doors":		{
														'S':	[(0,4)],
														'W':	[(4,3)]
													}
								},
					"sanhu": 	{
									"directions":	[],
									"grid_pos":		[(0,2),(0,1),(0,0),(2,0),(2,1),(2,2),(2,3),(2,4),(3,4),(3,3),(3,2),(3,1),(3,0),(5,0),(5,1),(5,2),(5,3),(5,4),(6,4),(6,3),(6,2),(6,1),(6,0),(8,0),(8,1),(8,2),(8,3),(8,4),(8,5)],
									"size":			(9,7),
									"doors":		{
														'E':	[(0,3),(0,6)]
													}
								},
					"piano": 	{
									"directions":	['NE','NW','NE','NW','NE','NW','NE','NW','NE','SE','SW','SE','SW','SE','SW','SE','SW','SE'],
									"grid_pos":		[(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),(11,2),(10,2),(9,2),(8,2),(7,2),(6,2),(5,2),(4,2),(3,2)],
									"size":			(12,3),
									"doors":		{
														'S':	[(0,2)]
													}
													
								},
					"organ": 	{
									"directions":	['NW','NE','NW','NE','NW','NE','NW','NE','NW','NE','SE','SW','SE','SW','SE','SW','SE','SW','SE','SW'],
									"grid_pos":		[(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(9,2),(8,2),(7,2),(6,2),(5,2),(4,2),(3,2),(2,2),(1,2),(0,2)],
									"size":			(10,3),
									"doors":		{
														'E':	[(0,1)]
													}
													
								},
					"clavier": 	{
									"directions":	['NW','NE','NW','NE','NW','NE','NW','NE','NW','NE','SE','SW','SE','SW','SE','SW','SE','SW','SE','SW'],
									"grid_pos":		[(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(9,2),(8,2),(7,2),(6,2),(5,2),(4,2),(3,2),(2,2),(1,2),(0,2)],
									"size":			(10,3),
									"doors":		{
														'E':	[(0,1)]
													}
													
								}
				}

	lab_data = getLabs(labs)
	return render_template('index.html',
		labs = lab_data,
		json = getJson(lab_data),
		debug = debug)

@app.route('/feedback')
def feedback():
	output = ""
	if request.args.get('body'):

		if request.args.get('subject'):
			subject = request.args.get('subject')
		else:
			subject = ""

		message = request.args.get('body')

		if request.args.get('email'):
			email = request.args.get('email')
		else:
			email = ""


		sender = 'jwis261@cse.unsw.edu.au'
		receivers = ['jwis261@cse.unsw.edu.au']

		message = """MIME-Version: 1.0
Content-type: text/html
Subject: webfriends suggestion: """+subject+"""


Feedback from webfriends form:<br /><br />

"""+message+"""<br /><br />

from email: """+email

		try:
		   smtpObj = smtplib.SMTP('smtp.cse.unsw.edu.au')
		   smtpObj.sendmail(sender, receivers, message)
		   smtpObj.quit()         
		   output+= "Successfully sent email"
		except smtplib.SMTPException:
		   output+= "Error: unable to send email. SMTPException"
	else:
		output+= "Please enter a message."
	return render_template('feedback.html',
		output = output)


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('err.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('webfriends startup')
 