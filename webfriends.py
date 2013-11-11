import subprocess, re, time, os, sys, json

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
		 	1650 : 	"CompSci Rsch",
		 	8543 :  "IT",
		 	3969 :  "CompSci/Media",
		 	3725 :  "Elec/Sci"
		}

		if not degree_num:
			degree_name = ""
		elif degree_num in degrees:
			degree_name = degrees[degree_num]
		else:
			degree_name = "Eng/Sci ["+str(degree_num)+"]"

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
						user_name = user_data.group().strip() if user_data else ""

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

		lab_output.update({lab:newLab(	lab,
										labs[lab]['grid_pos'],
										labs[lab]['directions'],
										users,
										state,
										labs[lab]['size'],
										labs[lab]['doors'],
										online
									)})

	return lab_output