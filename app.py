from flask import Flask, render_template, redirect,request, jsonify, Response, sessions,session, url_for
from flask.ext.socketio import SocketIO, join_room, leave_room, emit
import random
import string
import party as p
import uuid as u
import logging
from logging.handlers import RotatingFileHandler
app = Flask(__name__)
#app.config['SECRET_KEY'] = 'secret'
with open('secret.txt','r') as f:
    app.secret_key =f.read()
socketio = SocketIO(app)

@app.route("/api/parties/<party_id>",
           methods=["GET", "POST", "PATCH", "DELETE"])
def apiParty(party_id):
    party_id=party_id.upper()
    newParty = p.Party(party_id)
    if request.method == "GET":
        return jsonify({"songs": newParty.getOrdered()})
    elif request.method == "POST":
        print "POST"
        rec = request.get_json()
        newParty.addSong(rec["videoID"], rec["title"], rec["artist"])
        return jsonify({"success": True})
    elif request.method == "PATCH":
        rec = request.get_json()
        if rec["upvote"]:
            newParty.upVote(rec["videoID"])
        else:
            newParty.downVote(rec["videoID"])
        return jsonify({"success": True})
    elif request.method == "DELETE":
        rec = request.get_json()
        print rec["videoID"]
        newParty.removeSong(rec["videoID"])


def genID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))


@app.route("/")
def index():
    if 'id' not in session.keys():
        session['id']=str(u.uuid4())
    x=genID()
    while p.partyExists(x):
        x=genID()
    return render_template("index.html", partyID=x)


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
  return render_template("contact.html")

@app.route("/party")
def party():
    return render_template("party.html")


@app.route("/party/<partyID>")
def genParty(partyID):
    partyID=partyID.upper()
    if (len(partyID) == 8):
        if 'id' not in session.keys():
            session['id']=str(u.uuid4())
        return render_template("party.html", partyID=partyID)
    else:
        return '<h1>404</h1>', 404


@app.route("/<partyID>")
def redirParty(partyID):
    partyID=partyID.upper()
    if (len(partyID) == 8):
        if 'id' not in session.keys():
            session['id']=str(u.uuid4())
        partyURL = "/party/" + partyID
        return redirect(partyURL, code=303)
    else:
        return '<h1>404</h1>', 404

@socketio.on('connect', namespace='/party')
def test_connect():
    print "connected"
    if 'id' not in session.keys():
        session['id']=str(u.uuid4())
    print "connect:",session['id']
    emit('connect', {'data': session['id']})

@socketio.on('getID', namespace='/party')
def getID(data):
	if 'id' not in session.keys():
		session['id']=str(u.uuid4())
	print "getID: ", session['id']
	emit('getID', {'id': session['id']})


@socketio.on('disconnect', namespace='/party')
def test_disconnect():
    print "client disconnected"

@socketio.on('makeParty', namespace='/party')
def makeParty(data):
    print session.keys()
    print 'id' not in session.keys()
    if 'id' not in session.keys():
        session['id']=str(u.uuid4())
    print "makeParty:", session['id']
    room = data['room'].upper()
    ip = session['id']
    newParty = p.Party(room, ip)
    print "user: " + ip + "created party: " + room
    url = 'http://vynl.party/party/' + room
    emit('makeParty', {'id': session['id']})

@socketio.on('join', namespace='/party')
def on_join(data):
    #vote = data['vote']
    if 'id' not in session.keys():
        session['id']=str(u.uuid4())
    print "onjoin:", session['id']
    room = data['room'].upper()
    ipAddress =session['id']
    join_room(room)
    newParty = p.Party(room)
    dj = newParty.getDJ()
    song= newParty.getPlaying()
    if song:
        song=song[0]
    print "playing" , song
    print "joined room: " + room
    emit('join', {"songs": newParty.getOrdered(ipAddress),
                  "dj": dj ,"song":song})


@socketio.on('leave', namespace='/party')
def on_leave(data):
    room = data['room'].upper()
    leave_room(room)
    print "broski left room: " + room


@socketio.on('addSong', namespace='/party')
def addSong(data):
    #app.logger.error(data)
    partyID = data['room'].upper()
    song = data['song']
    ipAddress = session['id']
    newParty = p.Party(partyID)
    print "adding song: ", song, " to room: " + partyID
    newParty.addSong(song["songID"], song["albumarturl"], song["songname"], song["songartist"])
    #print newParty.getOrdered(newParty.getDJ())
    emit('notifySongUpdate', {"data": True}, room=partyID)


@socketio.on('getSongs', namespace='/party')
def getSong(data):
    print "updating songs"
    partyID = data['room'].upper()
    ipAddress = session['id']
    newParty = p.Party(partyID)
    thang=newParty.getOrdered(ipAddress)
    song= newParty.getPlaying()
    if song:
        song=song[0]
    print "ordered list:", thang
    emit('updateSongs', {"songs":thang ,"song":song})


@socketio.on('voteSong', namespace="/party")
def voteSong(data):
    partyID = data['room'].upper()
    song = data['song']
    vote=data['vote']
    ipAddress = session['id']
    newParty = p.Party(partyID)
    print "user: ", ipAddress, " vote: ", vote, " for song: ", song, " to room: " + partyID
    if vote == 1:
        newParty.upVote(song["songID"], ipAddress)
    elif vote == -1:
        newParty.downVote(song["songID"], ipAddress)
    emit('notifySongUpdate', {"data": True}, room=partyID)


@socketio.on('deleteSong', namespace="/party")
def deleteSong(data):
    partyID = data['room'].upper()
    song = data['song']
    ipAddress = session['id']
    newParty = p.Party(partyID)
    dj = newParty.getDJ()
    if dj == ipAddress:
        print "user: ", ipAddress, " deleting song: ", song["songID"], " to room: ", partyID
        newParty.removeSong(song["songID"])
        emit('notifySongUpdate', {"data": True}, room=partyID)
        emit('success', {'data': "Deleted Song"})
    else:
        print "user: ", ipAddress, " is not a dj: ", dj
        emit('error', {'data': "You are not the dj. You cannot Delete songs"});


@socketio.on('getPlaying', namespace="/party")
def playingSong(data):
    partyID = data['room'].upper()
    newParty = p.Party(partyID)
    song= newParty.getPlaying()
    if song:
        song=song[0]
    print "playing song: ", song, " in room: ", partyID
    emit('playingSong', {"song": song}, room=partyID)

@socketio.on('playSong', namespace="/party")
def playSong(data):
    partyID = data['room'].upper()
    song = data['song']
    newParty = p.Party(partyID)
    #print song
    newParty.playSong(song["songID"])
    #print newParty.getOrdered()
    print "played song: ", song, " in room: ", partyID
    emit('notifySongUpdate', {"data": True}, room=partyID)


if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.debug=True
    socketio.run(app, host='0.0.0.0', port=8000)
