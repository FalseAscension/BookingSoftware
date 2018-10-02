from flask import Flask, Response, request, render_template, session
from passlib.hash import bcrypt
from sqlitedb import database
import json,os,time,datetime

# Initialise Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database file
dbfile = "booking.db"

# Load settings from the database
db = database(dbfile)
settings = db.getSettings()
db.close()

print(settings['admins'])

@app.route('/')
@app.route('/index.html')
def home():
    if 'nologin' in settings:
        session['UUID'] = "4de2f84f-8c08-484f-942b-4f9bd8ab5ee4"
    if 'UUID' in session:
        db = database(dbfile)
        user = db.getUserByUUID(session['UUID'])
        db.close()
        return render_template('index.html', user=user['realname'])
    else:
        return render_template('login.html')

@app.route('/api')
def api(req=None):
    return json.dumps({})

@app.route('/api/getRooms')
def getRooms():
    return Response(json.dumps(settings['rooms']), status=200, mimetype="application/json")

@app.route('/api/getTimes')
def getTimes():
    return Response(json.dumps(settings['times']), status=200, mimetype="application/json")

@app.route('/api/getBookings', methods=["GET"])
def getBookings():
    if 'date' in request.args:
        date = request.args['date']
    else:
        date = datetime.date.today().isoformat()
    db = database("booking.db")
    bookings = db.getBookings(request.args.get("date"))
    db.close()
    return Response(json.dumps(bookings), status=200, mimetype="application/json")

@app.route('/api/updateSettings')
def updateSettings():
    global settings
    if 'UUID' not in session or session['UUID'] not in settings['admins']:
        return Response('{"status":"denied", "reason":"Not logged in as admin."}', status=400, mimetype="application/json")
    db = database(dbfile)
    settings = db.getSettings()
    db.close()
    return Response('{"status":"ok"}', status=400, mimetype="application/json")

# API User authentication
@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    response,status  = doAuthenticate()
    return Response(json.dumps(response), status=status, mimetype="application/json")

def doAuthenticate():

    # User is already authenticated...
    if 'UUID' in session:
        return {    "authenticated":    True,
                    "redirect":         "/index.html" },200

    # Ensure data is of a valid type
    if request.content_type in ("application/json", "json"):
        req_data = request.get_json()
    #elif request.content_type == "text/plain":
        #req_data = request.args
    else:
        return {    "authenticated":    False,
                    "reason":           "Client Error: Data type must be application/json"    },400

    # Ensure we have the correct data.
    if 'email' in req_data and 'password' in req_data:
        email = req_data['email']
        password = req_data['password']
    else:                                       # Client did not provide email and password. 400 Bad Request.
        return {    "authenticated":    False,
                    "reason":           "Client Error: Must provide both email and password"    },400

    # Initialise the database object and fetch data from it.
    db = database(dbfile)
    user = db.getUserByEmail(email)
    db.close()

    # Only allow 5 tries.
    if user['incorrectTries'] == 5:        # User has run out of tries.
        if time.time() - user['incorrectTime'] > 30: # Allow again after 10 minutes.
            user['incorrectTries'] = 0;
            db = database(dbfile)
            db.updateUserTriesByUUID(user['UUID'], 0, user['incorrectTime'])
            db.close()
        else:
            return {    "authenticated":    False,
                    "reason":           f"0 attempts remaining. Try again in {int(user['incorrectTime'] + 30 - time.time())} seconds.",
                    "triesRemaining":   0  },200    # Deny authentication for reason 0 tries remaining.
    # Check the user exists
    if not user:
        return {    "authenticated":    False,
                    "reason":           "User does not exist"   },200

    # Verify password...
    if bcrypt.verify(password, user['password']):
        session['UUID'] = user['UUID']
        db = database(dbfile)
        db.updateUserTriesByUUID(user['UUID'], 0, time.time())
        db.close()
        return {    "authenticated":   True,    # Allow authenitcation and give location for AJAX redirect.
                    "redirect":        "/index.html"   },200

    # Password must be incorrect.
    print(user['incorrectTries'])
    tries = user['incorrectTries'] + 1                 # Append one to tries

    # Store incorrect tries & time of last attempt in database.
    db = database(dbfile)
    db.updateUserTriesByUUID(user['UUID'], tries, time.time())
    db.close()
    return {    "authenticated":        False,  # Deny authentication for reason incorrect password.
                "reason":               "Incorrect Password.",
                "triesRemaining":       5 - tries  },200

@app.route('/register')
@app.route('/register.html')
def register():
    return render_template('register.html')

if __name__ == "__main__":
    app.config.update(
        TEMPLATES_AUTO_RELOAD=True,
        TESTING=True
    );
    app.run()
