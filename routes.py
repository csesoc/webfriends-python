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

import webfriends, json, jsonpickle
from flask import Flask, render_template, request


app = Flask(__name__)      
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
if __name__ == '__main__':
    app.run(debug=False)

@app.route('/')
def home():
    debug = request.args.get('debug')

    with open('webfriends.json') as json_data:
        labs = json.load(json_data)

    server_data = webfriends.get_servers(["wagner","weill","williams"])

    lab_data = webfriends.get_labs(labs)
    return render_template('index.html',
        labs = lab_data,
        json = jsonpickle.encode(lab_data),
        servers = server_data,
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
 
