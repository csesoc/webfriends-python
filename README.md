# webfriends-python
------------
Track your friends in UNSW cse labs over the web.


## Instructions:

### Basic Install
1. Clone webfriends to your public_html (on your cse account) directory using `git clone https://github.com/csesoc/webfriends-python.git`
2. You need to install the dependencies into the webfrieds-python folder:
 - flask
 - itsdangerous
 - jinja2
 - markupsafe
 - werkzeug
 - jsonpickle
3. Open webfriends.py.cgi/ with a web browser. Make sure that you include the trailing slash, or you will get a 500 error.

### Temperature and SSH Data
To get the temperature and ssh data, I use a cron job to pull it off `~status`, since the cgi server doesn't have the permissions.
However you decide to gather the data, it needs to end up in the cache/temp and cache/server directory (named after the name of the server/lab).

My scripts are as follows:
    
```shell
#!/bin/sh

labs=( "mabu" "clavier" "organ" "guan" "erhu" "oud" "piano" "banjo" "sanhu" )

mkdir -p public_html/webfriends-python/cache/temp
for i in "${labs[@]}"
do
    tail -n 1 ~status/temperature/lab-$i > public_html/webfriends-python/cache/temp/$i
done
```

```shell
#!/bin/sh

servers=( 'wagner' 'weill' 'williams' )

mkdir -p public_html/webfriends-python/cache/server
for i in "${servers[@]}"
do
    ssh $i who > public_html/webfriends-python/cache/server/$i
done
```

Ask for more explanation if this doesnt make sense.


### Todo:
 - See issues

Webfriends is available under the Apache License 2.0.

### Something Broken?

When SS change things it can screw up webfriends. Open `err.log` and check the last traceback. Its probably that they have added or removed a computer in a lab, so you might need to edit `webfriends.json`. You can also run `lab <labname>` in a cse terminal to check whether a lab is actually offline, and/or whether webfriends has the incorrect number of computers in its json file.
