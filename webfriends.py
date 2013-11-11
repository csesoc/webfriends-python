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

import subprocess, re, time, os, sys, json
from flask import Flask, render_template, request

app = Flask(__name__)      
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
if __name__ == '__main__':
	app.run(debug=False)

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
			user_data = importFromFile(user_id,"users", 60*60*24*30*3)

			user_name_data = re.search(r'(?<=[^\bUser\b] Name : ).*', user_data)
			user_name = user_name_data.group().strip()

			zid_data = re.search(r'z[0-9]+', user_data)
			if zid_data:
				user_zid = zid_data.group().strip()
			else: 
				user_zid = ""

			degree_data = re.search(r' [\d]{4}_Student', user_data)
			if degree_data:
				degree = self.getDegree(int(degree_data.group().strip()[:-8]))
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

	def getDegree(self,degree_num):
		degrees = {
			3529 : 	"Comm/CompSci",
			3645 : 	"CompEng",
			3647 : 	"Binf",
			3648 : 	"Seng",
			3651 : 	"Seng/Sci",
			3652 : 	"Seng/Arts",
			3653 : 	"Seng/Comm",
			3715 : 	"Eng/Comm",
			3722 : 	"CompEng/Arts",
			3726 : 	"CompEng/Sci",
			3728 : 	"CompEng/Biomed",
			3749 : 	"Seng/Biomed",
			3755 : 	"Binf/Sci",
			3756 : 	"Binf/Arts",
			3757 : 	"Binf/Biomed",
			3978 : 	"CompSci",
			3968 : 	"CompSci/Arts",
			3982 : 	"CompSci/BDM",
			3983 : 	"CompSci/Sci",
		 	1650 : 	"CompSci(PG)"  
		}

		if not degree_num:
			degree_name = ""
		elif degree_num in degrees:
			degree_name = degrees[degree_num]
		else:
			degree_name = "Eng/Sci"

		return degree_name

	def __init__(self, user_id, since):
		self.user_id = user_id
		self.name = self.getData(user_id)['user_name']
		self.zid = self.getData(user_id)['user_zid']
		self.degree = self.getData(user_id)['degree']
		self.since = since
		self.since_string = time.strftime("%H:%M:%S %d/%m", since)
	
def newUser(user_id, since):
	user = User(user_id, since)
	return user

def newLab(name, computers, directions, users, state, size, doors, online):
	lab = Lab(name, computers, directions, users, state, size, doors, online)
	return lab

def importFromFile(cache_id,cache_type, refresh_time): #cache to file #yolo

	if not os.path.exists('cache'):
		os.makedirs('cache')
	if not os.path.exists('cache/users'):
		os.makedirs('cache/users')
	if not os.path.exists('cache/labs'):
		os.makedirs('cache/labs')

	fileName = "cache/"+cache_type+"/"+cache_id
	command = []

	if cache_type == 'labs':
		command = ['timeout','3s','/usr/local/bin/lab',cache_id]
	elif cache_type == 'users':
		command = ["pp",cache_id]

	if os.path.isfile(fileName):
		if time.time() - os.path.getmtime(fileName) < refresh_time:
			fileData = open(fileName)
			data = fileData.read()
			fileData.close()
		else:
			data = importData(command)
			fileData = open(fileName, "w")
			fileData.write(data)
			fileData.close()
	else:
		data = importData(command)
		fileData = open(fileName, "a")
		fileData.write(data)
		fileData.close()

	return data

def importData(command):
	process = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, err = process.communicate()
	return out

def getLabs(labs):
	lab_output = {}
	for lab in labs.keys():

		users = {}
		lab_list = importFromFile(lab,"labs", 60)

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
			state = False

		lab_output.update({lab:newLab(lab,labs[lab]['grid_pos'],labs[lab]['directions'],users,state,labs[lab]['size'],labs[lab]['doors'],online)})

	return lab_output

@app.route('/')
def home():
	debug = request.args.get('debug')

	json_data = open('webfriends.json')
	labs = json.load(json_data)
	json_data.close()

	lab_data = getLabs(labs)
	return render_template('index.html',
		labs = lab_data,
		debug = debug)

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html',
    	env = e)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',
    	env = e),404

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('err.log', 'a', 1 * 256 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('[%(lineno)d] %(asctime)s %(levelname)s: %(message)s',"%Y-%m-%d %H:%M:%S"))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
 
