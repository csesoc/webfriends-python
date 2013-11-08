#!/usr/bin/python2.7

'''
   Copyright 2013 John Wiseheart

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import subprocess, re, time, os, sys, json, smtplib
from flask import Flask, render_template, request
from werkzeug.contrib.cache import SimpleCache

app = Flask(__name__)      
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
if __name__ == '__main__':
	app.run(debug=False)
	
cache = SimpleCache()

class Lab(object):
	name = ""
	computers = [] #stores the grid coords
	directions = []
	state = False
	users = []
	size = tuple()
	doors = {}
	online = True

	def __init__(self, name, computers, directions, users, state, size, doors, online):
		self.name = name
		self.computers = computers
		self.directions = directions
		self.state = state
		self.users = users
		self.size = size
		self.doors = doors
		self.online = online

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

class User(object):
	user_id = ""
	name = ""
	zid = ""
	degree = ""
	since = time.struct_time
	since_string = ""
	
	def getData(self, user_id):
		user = {}
		if user_id != "":
			user_data = cache.get('user-'+user_id)
			if user_data is None:
				user_data = importData(["pp",user_id])
				cache.set('user-'+user_id, user_data, timeout=60 * 60 *24 * 30 * 3)
			user_name_data = re.search(r'(?<=[^\bUser\b] Name : ).*', user_data)
			user_name = user_name_data.group().strip()

			zid_data = re.search(r'z[0-9]+', user_data)
			if zid_data:
				user_zid = zid_data.group().strip()
			else: 
				user_zid = ""

			degree_data = re.search(r' [\d]{4}_Student', user_data)
			if degree_data:
				degree = getDegree(degree_data.group().strip()[:-8])
			else:
				degree = ""
		else:
			user_zid = ""
			user_name = ""
			degree = ""
		user['user_zid'] = user_zid
		user['user_name'] = user_name
		user['degree'] = degree
		return user

	def __init__(self, user_id, since):
		self.user_id = user_id
		self.name = self.getData(user_id)['user_name']
		self.zid = self.getData(user_id)['user_zid']
		self.degree = self.getData(user_id)['degree']
		self.since = since
		self.since_string = time.strftime("%H:%M:%S %d/%m", since)

	def __str__(self):
		if self.user_id:
			out = "user_id: "+self.user_id+" name: "+self.name
		else:
			out = ""
		return out
	
def newUser(user_id, since):
	user = User(user_id, since)
	return user

def newLab(name, computers, directions, users, state, size, doors, online):
	lab = Lab(name, computers, directions, users, state, size, doors, online)
	return lab

def getDegree(degree_num):
	degree_name = ""
	degree_num = int(degree_num)
	if degree_num == 3529:
		degree_name = "Comm/CompSci"
	elif degree_num == 3645:
		degree_name = "CompEng"
	elif degree_num == 3647:
		degree_name = "Binf"
	elif degree_num == 3648:
		degree_name = "Seng"
	elif degree_num == 3651:
		degree_name = "Seng/Sci"
	elif degree_num == 3652:
		degree_name = "Seng/Arts"
	elif degree_num == 3653:
		degree_name = "Seng/Comm"
	elif degree_num == 3715:
		degree_name = "Eng/Comm"
	elif degree_num == 3722:
		degree_name = "CompEng/Arts"
	elif degree_num == 3726:
		degree_name = "CompEng/Sci"
	elif degree_num == 3728:
		degree_name = "CompEng/Biomed"
	elif degree_num == 3749:
		degree_name = "Seng/Biomed"
	elif degree_num == 3755:
		degree_name = "Binf/Sci"
	elif degree_num == 3756:
		degree_name = "Binf/Arts"
	elif degree_num == 3757:
		degree_name = "Binf/Biomed"
	elif degree_num == 3978:
		degree_name = "CompSci"
	elif degree_num == 3968:
		degree_name = "CompSci/Arts"
	elif degree_num == 3982:
		degree_name = "CompSci/BDM"
	elif degree_num == 3983:
		degree_name = "CompSci/Sci"
	elif degree_num == 1650:
		degree_name = "CompSci(PG)"   
	else:
		degree_name = "Eng/Sci"
	return degree_name

def importLabData(lab, refresh_time):
	
	lab_data = cache.get('lab-'+lab)
	if lab_data is None:

		# timeout prevents offline labs from hanging the site
		process = subprocess.Popen(['timeout','3s','/usr/local/bin/lab',lab], stdout=subprocess.PIPE)

		lab_data, err = process.communicate()
		cache.set('lab-'+lab, lab_data, timeout=refresh_time*60)
	return lab_data

def importData(command):
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, err = process.communicate()
	return out

def getLabs(labs):
	lab_output = {}
	for lab in labs.keys():

		users = {}
		lab_list = importLabData(lab,60)

		if len(lab_list.splitlines()) > 2:
			if lab_list.splitlines()[1][0:3] == 'Lab':
				state_data = re.search(r'(?<=is )[\S]+', lab_list.splitlines()[1])
				state_text = state_data.group().strip().rstrip(',')
				state = False if state_text == "CLOSED" else True
				online = True

				for line in lab_list.splitlines():

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

						users[comp_no] = newUser(user_name, since)
		else:
			online = False

		lab_output.update({lab:newLab(lab,labs[lab]['grid_pos'],labs[lab]['directions'],users,state,labs[lab]['size'],labs[lab]['doors'],online)})

	return lab_output

def getJson(lab_data):
	json = "{"
	for i in lab_data:
		if lab_data[i].online:
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

	json_data = open('webfriends.json')
	labs = json.load(json_data)
	json_data.close()

	lab_data = getLabs(labs)
	return render_template('index.html',
		labs = lab_data,
		debug = debug)


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('err.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('webfriends startup')
 
