from flask import Flask, render_template, redirect
import random
import string

app = Flask(__name__)

def genID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))

@app.route("/")
def index():
    return render_template("index.html", partyID=genID())

@app.route("/base")
def base():
    return render_template("base.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/party")
def party():
    return render_template("party.html")

@app.route("/party/<partyID>")
def genParty(partyID):
   if (len(partyID)==8):
      return render_template("party.html", partyID=partyID)
   else:
      return '<h1>404</h1>', 404

@app.route("/<partyID>")
def redirParty(partyID):
   if (len(partyID)==8):
      partyURL = "/party/" + partyID
      return redirect(partyURL, code=303)
   else:
      return '<h1>404</h1>', 404

if __name__ == "__main__":
   app.debug = True
   app.run(host="0.0.0.0", port=8000)
