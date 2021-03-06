import os

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit,join_room, leave_room
from flask_session import Session
import requests
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

roomlist=["Group1", "Group2", "Group3"]
msg={}

@app.route("/")
def index():
    if 'name' in session:
        if 'room' in session:
            return render_template("index.html",user=session['name'], group=session['room'], pmsg=msg[session["room"]])
        return render_template("COJ.html", name=session['name'], roomlist=roomlist)
    else:
        return render_template("type-name.html")

@app.route("/chat", methods=["POST","GET"])
def chat():
    if request.method=='POST':
        name=request.form.get("name")
        session['name']=name
        return render_template("COJ.html", name=session['name'], roomlist=roomlist)
    else:
        return render_template("type-name.html")

@app.route("/createroom", methods=["POST"])
def createroom():
    if 'name' in session:
        room=request.form.get("name")
        if room in roomlist:
            return render_template("error.html")
        roomlist.append(room)
        session['room']=room
        if msg.get(room) is None:
            msg[room]=[]
        return redirect(url_for("index"))
    else:
        return render_template("type-name.html")


@app.route("/joinroom", methods=["POST"])
def joinroom():
    if 'name' in session:
        room=request.form.get("name")
        session['room']=room
        if msg.get(room) is None:
            msg[room]=[]
        return redirect(url_for("index"))
    else:
        return render_template("type-name.html")


@socketio.on("connect")
def on_connect():
    room=session['room']
    join_room(room)
    emit('userjoined',{"user":session['name']}, broadcast=True, room=room)


@socketio.on("msg")
def msg_handle(data):
    now = time.time()
    timestamp = time.strftime('%H:%M:%S', time.gmtime(now))
    room=session['room']
    msgitem=data["msg"]
    msgitem = f'{session["name"]} : {msgitem} \n {str(timestamp)}'
    print(msgitem)
    if len(msg[room])<=99:
        msg[room].append(msgitem)
    else:
        del msg[room][0]
        msg[room].append(msgitem)
    emit("msgsend",{"msg":data["msg"], "name":session['name'], "timestamp":timestamp}, broadcast=True, room=room)

@socketio.on('disconnect')
def test_disconnect():
    name=session['name']
    room=session["room"]
    emit("userleave", {"user":name}, broadcast=True, room=room)

@app.route("/sendrequest",methods=["POST"])
def sendrequest():
    message=str(request.form.get("message"))
    print(message)
    if message in msg[session["room"]]:
        msg[session["room"]].remove(message)
        return "message deleted successfully"
    return "something went wrong"
