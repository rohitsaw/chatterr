import os

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit,join_room, leave_room
from flask_session import Session
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

roomlist=["Group1", "Group2", "Group3"]

@app.route("/")
def index():
    if 'name' in session:
        return redirect(url_for('chat'))
    else:
        return render_template("type-name.html")

@app.route("/chat", methods=["POST","GET"])
def chat():
    if request.method=='POST':
        name=request.form.get("name")
        session['name']=name
        #roomlist=['hello', 'rohit']
        return render_template("COJ.html", name=session['name'], roomlist=roomlist)
    else:
        return render_template("COJ.html", name=session['name'], roomlist=roomlist)

@socketio.on("connect", namespace='/chat')
def connect():
    emit("connectmsg",{"msg","socket connected"})

@socketio.on("joinroom", namespace="/chat")
def joinroom(data):
    print("joinedroom event received")
    session['room']=data["room"]
    emit("redirect", {"url": {{url_for('myfunction')}} })

@socketio.on("createroom", namespace="/chat")
def createroom(data):
    print("createroom event received")
    room=data["room"]
    if room in roomlist:
        emit("roomnotavailable",{"room":room})
    else:
        roomlist.append(room)
        session['room']=room
        emit("redirect", {"url":{{url_for('myfunction')}} })

@app.route("/group")
def myfunction():
    return render_template("index.html",user=session['name'], room=session['room'])

@socketio.on("connect", namespace="/group")
def on_connect():
    room=session['room']
    join_room(room)
    emit("userjoined", {"user":session['name'], "room":session["room"]})

# @app.route("/chooseroom", methods=["POST"])
# def chooseroom():
#     return render_template("roomlist.html",roomlist=roomlist)
#
# @app.route("/sessionroom", methods=["POST"])
# @socketio.on("connect", namespace="/sessionroom")
# def sessionroom():
#     room=request.form.get("name")
#     session['room']=room
#     roomlist.append(room)
#     join_room(room)
#     return render_template("index.html",room=session['room'], user=session['name'])

# @app.route("/room")
# def room(data):
#     # room=request.form.get("cname")
#     room=request.json['share']
#     if room in roomlist:
#         return "qwertghjkmnbvcx"
#     else:
#         roomlist.append(room)
#         # join_room(room)
#         # emit('status', {'success':"true", 'name':session['name'],"room":room}, room=room)
#         return "hasdfghnm"


@socketio.on("msg", namespace="/group")
def msg_handle(data):
    emit("msgsend",{"msg":data["msg"], "name":session['name']}, broadcast=True, room=room)
