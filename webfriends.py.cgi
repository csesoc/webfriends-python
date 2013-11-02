#!/usr/bin/python2.7
import cgitb
cgitb.enable()
from wsgiref.handlers import CGIHandler
from webfriends import app

CGIHandler().run(app)