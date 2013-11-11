'''
   Copyright 2013 John Wiseheart

   Licensed under the Apache License, Version 2.0 (the 'License');
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an 'AS IS' BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

import subprocess
import re
import time
import os


class Lab(object):

    name = ''
    computers = []  # stores the grid coords
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

    user_id = ''
    name = ''
    zid = ''
    degree = ''
    since = time.struct_time
    since_string = ''

    def getData(self, user_id):
        user = {}
        if user_id != '':
            data = importFromFile(user_id, 'users', 60 * 60 * 24 * 30 * 3)

            user_name_reg = re.search(r'(?<=[^\bUser\b] Name : ).*', data)
            user['user_name'] = user_name_reg.group().strip()

            zid_reg = re.search(r'z[0-9]+', data)
            user['user_zid'] = zid_reg.group().strip() if zid_reg else ''

            degree_reg = re.search(r' [\d]{4}_Student', data)
            if degree_reg:
                degree_num = int(degree_reg.group().strip()[:-8])
                user['degree'] = self.getDegree(degree_num)
            else:
                user['degree'] = ''
        else:
            user['user_zid'] = ''
            user['user_name'] = ''
            user['degree'] = ''
        return user

    def getDegree(self, degree_num):

        degrees = {
            3529: 'Comm/CompSci',
            3645: 'CompEng',
            3647: 'Binf',
            3648: 'Seng',
            3651: 'Seng/Sci',
            3652: 'Seng/Arts',
            3653: 'Seng/Comm',
            3715: 'Eng/Comm',
            3722: 'CompEng/Arts',
            3726: 'CompEng/Sci',
            3728: 'CompEng/Biomed',
            3749: 'Seng/Biomed',
            3755: 'Binf/Sci',
            3756: 'Binf/Arts',
            3757: 'Binf/Biomed',
            3978: 'CompSci',
            3968: 'CompSci/Arts',
            3982: 'CompSci/BDM',
            3983: 'CompSci/Sci',
            1650: 'CompSci Rsch',
            8543: 'IT',
            3969: 'CompSci/Media',
            3725: 'Elec/Sci'
        }

        if not degree_num:
            degree_name = ''
        elif degree_num in degrees:
            degree_name = degrees[degree_num]
        else:
            degree_name = 'Eng/Sci [' + str(degree_num) + ']'

        return degree_name

    def __init__(self, user_id, since):
        self.user_id = user_id
        self.name = self.getData(user_id)['user_name']
        self.zid = self.getData(user_id)['user_zid']
        self.degree = self.getData(user_id)['degree']
        self.since = since
        self.since_string = time.strftime('%H:%M:%S %d/%m', since)


def newUser(user_id, since):

    user = User(user_id, since)
    return user


def newLab(name, computers, directions, users, state, size, doors, online):

    lab = Lab(name, computers, directions, users, state, size, doors, online)
    return lab


def importFromFile(cache_id, cache_type, refresh_time):  # cache to file # yolo

    if not os.path.exists('cache'):
        os.makedirs('cache')
    if not os.path.exists('cache/users'):
        os.makedirs('cache/users')
    if not os.path.exists('cache/labs'):
        os.makedirs('cache/labs')

    fileName = 'cache/' + cache_type + '/' + cache_id
    command = []

    if cache_type == 'labs':
        command = ['timeout', '3s', '/usr/local/bin/lab', cache_id]
    elif cache_type == 'users':
        command = ['pp', cache_id]

    useFile = False

    if os.path.isfile(fileName):
        if time.time() - os.path.getmtime(fileName) < refresh_time:
            with open(fileName) as fileData:
                data = fileData.read()
            useFile = True

    if not useFile:
        data = importData(command)
        with open(fileName, 'w') as fileData:
            fileData.write(data)

    return data


def importData(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def getState(line):
    state_reg = re.search(r'(?<=is )[\S]+', line)
    state_text = state_reg.group().strip().rstrip(',')
    state = False if state_text == 'CLOSED' else True
    return state


def getComp(line):
    data = {}

    comp_reg = re.search(r'.*(?=:[\bUp\b\bDown\b])', line)

    if comp_reg:
        data['comp_name'] = comp_reg.group().strip()[:-2]
        data['comp_num'] = int(data['comp_name'][-2:])
        user_reg = re.search(r'(?<=[\bAllocated\b\bTentative\b]: )[\S]+', line)
        data['user_name'] = user_reg.group().strip() if user_reg else ''

        since_reg = re.search(r'(?<=since ).*', line)
        if since_reg:
            since = since_reg.group().strip()
            since_plus_year = since + ' ' + time.strftime('%Y')
            data['since'] = time.strptime(since_plus_year, '%d/%m;%H:%M:%S %Y')
        else:
            data['since'] = time.strptime(time.strftime('%d/%m;0:0:0 %Y'), '%d/%m;%H:%M:%S %Y')

        data['user'] = newUser(data['user_name'], data['since'])

    return data


def isValidLab(lab_list):
    if len(lab_list.splitlines()) > 2:
        if lab_list.splitlines()[1][0:3] == 'Lab':
            return True
    return False


def getLabs(labs):
    lab_output = {}
    for lab in labs.keys():

        users = {}
        lab_list = importFromFile(lab, 'labs', 60)

        if isValidLab(lab_list):
            state = getState(lab_list.splitlines()[1])
            online = True

            for line in lab_list.splitlines():

                data = getComp(line)
                if 'user' in data:
                    users[data['comp_num']] = data['user']
        else:
            online = False
            state = False

        lab_output.update({lab: newLab(lab, labs[lab]['grid_pos'], labs[lab]['directions'],
                                       users, state, labs[lab]['size'],  labs[lab]['doors'],  online)})

    return lab_output
