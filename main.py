from appLogging import get_logger
import socket
import datetime as dt
import firebase_admin
from firebase_admin import db
import threading

from flask import Flask, jsonify, request, send_from_directory, render_template
from notify import Notify
from response import Response
from static import check_mac, set_slash

from relay import Relay
from properties import ip, port, end_time, start_time
import os

from tof import TOF

app = Flask(__name__)

logger = get_logger()
tof = TOF()
notify = Notify(tof)
relay = None
running = False

appKey = "garageDoor"
ref = db.reference(appKey)


def complete():
    global running
    running = False


def button_click():
    global relay, running
    print("button_click()")
    logger.debug(f"button_click()")
    status = 200
    hr = dt.datetime.now().hour
    if start_time <= hr < end_time:
        if not running:
            relay = Relay(12, complete)
            relay.on()
            running = True
    else:
        status = 503
    response = Response()
    response.status_code = status
    response.action = "relay"
    response.data = '{"data": "value"}'
    return jsonify(message="Success",
                   statusCode=status), status


@app.route("/_getStatus")
def get_status():
    print("get_status()")
    val = tof.range
    ret = "CLOSED"
    if 10 < val < 275:
        ret = "OPEN"
    return jsonify(value=ret)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/test')
def test():
    response = Response()
    response.status_code = 200
    response.action = "test"
    response.data = '{"data": "value"}'
    return response.__dict__()


@app.route('/token')
def add_token():
    token = request.args.get('token', default="", type=str)


@app.route('/relay')
def relay_action():
    global relay, running
    pin = request.args.get('pin_in', default=-1, type=int)
    mac = request.args.get('mac', default="", type=str)
    logger.debug(f"relay[{pin}] action[ON] time[1]")
    status = 200
    hr = dt.datetime.now().hour
    if start_time <= hr < end_time or check_mac(mac):
        if not running:
            relay = Relay(int(pin), complete)
            relay.on()
            running = True
    else:
        status = 503
    response = Response()
    response.status_code = status
    response.action = "relay"
    response.data = '{"data": "value"}'
    return jsonify(message="Success",
                   statusCode=status), status


@app.route('/door/<action>')
def door(action):
    global tof
    logger.info(f"door({action})")
    val = action
    if action == 'on':
        tof.start()
    elif action == 'off':
        tof.stop()
    elif action == 'get':
        val = tof.range
    elif action == 'status':
        val = tof.get_status()
    else:
        val = "Invalid action"
    return {"value": val}, 200


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


def trigger():
    ref.child('trigger').update(True)
    threading.Timer(5, trigger).start()


def listener(event):
    print('firebase listener...')
    if event.data:
        print('open garage door')
        ref.child('trigger').update(False)


if __name__ == '__main__':
    set_slash()
    host_name = socket.gethostbyname(socket.gethostname())
    logger.info("machine host_name[" + host_name + "]")
    print(host_name + "[" + host_name[0: 3] + "]")
    if host_name[0: 3] == "192" or host_name[0: 3] == "127":
        host_name = ip
    else:
        host_name = "localhost"
    logger.info(f"app host_name[{host_name}]")
    tof.start()
    notify.start()
    ref.child("trigger").listen(listener)
    threading.Timer(5, trigger).start()
    app.run(host=host_name, port=port)
