#!/usr/bin/python2.7

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
    temperature = 0.0

    def __init__(self, name, computers, directions, users, state, size, doors, online):

        self.name = name
        self.computers = computers
        self.directions = directions
        self.state = state
        self.users = users
        self.size = size
        self.doors = doors
        self.online = online
        self.temperature = self._get_temperature(name)

    def __str__(self):
        return self.name

    def _get_temperature(self,name):
        path = 'cache/temp/' + name
        if os.path.isfile(path):
            with open(path) as temp_data:
                temp_reg = re.search(r' [0-9.]+', temp_data.read())
                temp = float(temp_reg.group().strip()) if temp_reg else 0.0
            return round(temp, 1)


class User(object):

    user_id = ''
    name = ''
    zid = ''
    degree = ''
    since = time.struct_time
    since_string = ''

    def __init__(self, user_id, since):

        self.user_id = user_id
        self.name = self._getData(user_id)['user_name']
        self.zid = self._getData(user_id)['user_zid']
        self.degree = self._getData(user_id)['degree']
        self.since = since
        self.since_string = time.strftime('%H:%M:%S %d/%m', since)

    def _getData(self, user_id):

        user = {}
        if user_id != '':
            data = import_from_file(user_id, 'users', 60 * 60 * 24 * 30 * 3)

            user_name_reg = re.search(r'(?<=[^\bUser\b] Name : ).*', data)
            user['user_name'] = user_name_reg.group().strip()

            zid_reg = re.search(r'z[0-9]+', data)
            user['user_zid'] = zid_reg.group().strip() if zid_reg else ''

            degree_reg = re.search(r' [\d]{4}_Student', data)
            if degree_reg:
                degree_num = int(degree_reg.group().strip()[:-8])
                user['degree'] = self._get_degree(degree_num)
            else:
                user['degree'] = ''
        else:
            user['user_zid'] = ''
            user['user_name'] = ''
            user['degree'] = ''
        return user

    def _get_degree(self, degree_num):

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


def new_user(user_id, since):

    user = User(user_id, since)
    return user


def new_lab(name, computers, directions, users, state, size, doors, online):

    lab = Lab(name, computers, directions, users, state, size, doors, online)
    return lab


def import_from_file(cache_id, cache_type, refresh_time=60):  # cache to file # yolo

    if not os.path.exists('cache'):
        os.makedirs('cache')
    if not os.path.exists('cache/users'):
        os.makedirs('cache/users')
    if not os.path.exists('cache/labs'):
        os.makedirs('cache/labs')

    fileName = 'cache/' + cache_type + '/' + cache_id

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
        data = import_data(command)
        with open(fileName, 'w') as fileData:
            fileData.write(data)

    return data


def import_data(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def get_state(line):
    state_reg = re.search(r'(?<=is )[\S]+', line)
    state_text = state_reg.group().strip().rstrip(',')
    state = False if state_text == 'CLOSED' else True
    return state


def get_since(line):
    since_reg = re.search(r'(?<=since ).*', line)
    if since_reg:
        since = since_reg.group().strip()
        since_plus_year = since + ' ' + time.strftime('%Y')
        since_out = time.strptime(since_plus_year, '%d/%m;%H:%M:%S %Y')
    else:
        since_out = time.strptime(time.strftime('%d/%m;0:0:0 %Y'), '%d/%m;%H:%M:%S %Y')

    return since_out


def get_username(line):
    user_reg = re.search(r'(?<=[\bAllocated\b\bTentative\b]: )[\S]+', line)
    user_name = user_reg.group().strip() if user_reg else ''

    return user_name


def get_computer(line):
    data = {}
    comp_reg = re.search(r'.*(?=:[\bUp\b\bDown\b])', line)
    if comp_reg:
        data['comp_name'] = comp_reg.group().strip()[:-2]
        data['comp_num'] = int(data['comp_name'][-2:])
        data['user_name'] = get_username(line)
        data['since'] = get_since(line)
        data['user'] = new_user(data['user_name'], data['since'])

    return data


def is_valid_lab(lab_list):
    if len(lab_list.splitlines()) > 2:
        if lab_list.splitlines()[1].startswith('Lab'):
            return True

    return False

def get_servers(servers):
    server_output = {}
    for server in servers:
        with open('cache/server/' + server) as server_data:
            server_output.update({server: server_data.read()})

    return server_output

def get_labs(labs):
    lab_output = {}
    for lab in labs:

        users = {}
        lab_list = import_from_file(lab, 'labs')

        if is_valid_lab(lab_list):
            state = get_state(lab_list.splitlines()[1])
            online = True

            for line in lab_list.splitlines():

                data = get_computer(line)
                if 'user' in data:
                    users[data['comp_num']] = data['user']
        else:
            online = False
            state = False

        lab_output.update({lab: new_lab(lab, labs[lab]['grid_pos'], labs[lab]['directions'],
                                        users, state, labs[lab]['size'],  labs[lab]['doors'],  online)})

    return lab_output
