import json, time
from ubiquiti.unifi import API as Unifi_API
from flask import Flask, request, render_template
from flask_apscheduler import APScheduler

config = json.load(open('config.json','r'))


UniFi_api = Unifi_API(username=config["username"], password=config["password"], baseurl=config["baseurl"], site=config["site"], verify_ssl=config["verify_ssl"])


app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from datetime import datetime

def checkStatus():
    UniFi_api.login()

def getStatus():
    if not UniFi_api.connected:
        status = "Disconnected"
    elif UniFi_api.connected:
        status = "Connected"
    return {"status": status}


def monthlypasswordchange():
    password = UniFi_api.set_guest_password()
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(f"Changing password to {password} at {dt_string}.")
    #TODO
    #Add email so that we know it's been done.

@app.route("/password/show")
def show_Password():
    status = getStatus()
    if status["status"] == "Disconnected":
        return render_template('password.html', data={"password": "error"})
    else:
        return render_template('password.html', data=UniFi_api.get_guest_password())


@app.route('/password', methods=['GET'])
def get_password():
    status = getStatus()
    if status["status"] == "Disconnected":
        return {"error": "Could not recieve password, not logged in to UniFi"}, 404

    return UniFi_api.get_guest_password()

@app.route('/password', methods=['PUT'])
def set_password():
    #Check status
    status = getStatus()
    if status["status"] == "Disconnected":
        return {"error": "Could not recieve password, not logged in to UniFi"}, 404
    
    password = request.args.get('password')

    return UniFi_api.set_guest_password(password)

if __name__ == '__main__':
    #app.apscheduler.add_job(func=monthlypasswordchange, trigger="cron", day="1", id="monthlypasswordchange")
    app.apscheduler.add_job(func=checkStatus, trigger="cron", day="*/1", id="checkStatus")
    checkStatus()
    app.run(debug=False,host="0.0.0.0", port=5000)
    
