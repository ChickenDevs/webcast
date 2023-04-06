#!/usr/bin/python3

from flask import Flask, abort, Response, request
app = Flask(__name__)

import os
import json
import pam

from functools import wraps
def auth(f):
    @wraps(f)
    def pred(*args, **kwargs):
        if request.authorization:
            if pam.authenticate(request.authorization.username, request.authorization.password):
                return f(*args, **kwargs)
        return abort(401)
    return pred

def pi_stopped(f):
    @wraps(f)
    def pred(*args, **kwargs):
        if request.method == "POST":
            if len(os.popen('ps -e | grep ffmpeg').read()) > 0:
                return abort(404)
        return f(*args, **kwargs)
    return pred

@app.route('/auth')
@auth
def authenticate():
    print("/auth called")
    return {}

import psutil
import time
@app.route('/pi/stats')
@auth
def pi_stats():
    print("/pi/stats called")
    net = psutil.net_io_counters()
    return {'timestamp': time.time(), 'cpu': psutil.cpu_percent(), 'memory': psutil.virtual_memory().percent, 'net_sent': net.bytes_sent, 'net_recv': net.bytes_recv}


@app.route('/webcast/pause/status')
@auth
def webcast_pause_status():
    with open('/etc/webcast/webcast.conf') as f:
        conf = json.load(f)
    return {'paused': conf.get('shouldbepaused', False)}


@app.route('/webcast/pause')
@auth
def webcast_pause():
    with open('/etc/webcast/webcast.conf') as f:
        conf = json.load(f)
    conf['shouldbepaused'] = True
    with open('/etc/webcast/webcast.conf', 'w') as f:
        json.dump(conf, f)
    os.system('sudo systemctl start webcast.service')
    return {'paused': True}


@app.route('/webcast/resume')
@auth
def webcast_resume():
    with open('/etc/webcast/webcast.conf') as f:
        conf = json.load(f)
    conf['shouldbepaused'] = False
    with open('/etc/webcast/webcast.conf', 'w') as f:
        json.dump(conf, f)
    os.system('sudo systemctl start webcast.service')
    return {'paused': False}


@app.route('/webcast/stop')
@auth
def webcast_stop():
    print("/webcast/stop called")
    os.system('sudo systemctl stop webcast.timer')
    os.system('sudo systemctl stop webcast.service')
    os.system('sudo pkill ffmpeg')
    output = os.popen('sudo systemctl status webcast.service').read()
    return {'response': output}

@app.route('/webcast/start')
@auth
def webcast_start():
    print("/webcast/start called")
    os.system('sudo systemctl start webcast.timer')
    os.system('sudo systemctl start webcast.service')
    output = os.popen('sudo systemctl status webcast.service').read()
    return {'response': output}


@app.route('/webcast/restart')
@auth
def webcast_restart():
    print("/webcast/restart called")
    os.system('sudo pkill ffmpeg')
    os.system('sudo systemctl restart webcast.service')
    output = os.popen('sudo systemctl status webcast.service').read()
    return {'response': output}

@app.route('/webcast/status')
@auth
def webcast_status():
    print("/webcast/status called")
    output = os.popen('sudo systemctl status webcast.service').read()
    return {'response': output}


@app.route('/webcast/settings', methods=['GET', 'POST'])
@auth
@pi_stopped
def webcast_settings():
    print("/webcast/settings called")
    print("Method:", request.method)
    with open('/etc/webcast/webcast.conf') as f:
        conf = json.load(f)

    if request.method == 'GET':
        return conf
    elif request.method == 'POST':
        req_json = request.get_json()

        for key, val in req_json.items():
            if key in conf.keys():
                conf[key] = val
            else:
                return abort(400)
        with open('/etc/webcast/webcast.conf', 'w') as f:
            json.dump(conf, f)
        return conf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
