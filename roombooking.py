from flask import Flask, Response, request, render_template, session
from passlib.hash import bcrypt
from sqlitedb import database
import json,os

# Initialise Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    if 'UUID' in session:
        return render_template('index.html', user="Test User")
    else:
        return render_template('login.html')

@app.route('/api')
def api(req=None):
    return json.dumps({})

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
       
    # Only allow 5 tries.
    ## TODO storing this in session is not secure. Use database instead.
    if 'triesRemaining' not in session:       # Keep track of how many tries user has remaining.
        session['triesRemaining'] = 5
    elif session['triesRemaining'] == 0:        # User has run out of tries.
        return {    "authenticated":    False,
                    "reason":           "0 tries remaining.",
                    "triesRemaining":   0  },200    # Deny authentication for reason 0 tries remaining.

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
    db = database("booking.db")                 
    user = db.getUserByEmail(email)             
    db.close()                                  
    
    # Check the user exists
    if not user:
        return {    "authenticated":    False,
                    "reason":           "User does not exist"   },200

    # Verify password...
    if bcrypt.verify(password, user['password']):
        session['UUID'] = user['UUID'] 
        return {    "authenticated":   True,    # Allow authenitcation and give location for AJAX redirect.
                    "redirect":        "/index.html"   },200

    # Password must be incorrect.
    session['triesRemaining'] -= 1              # Decrement remaining tries.
    return {    "authenticated":        False,  # Deny authentication for reason incorrect password.
                "reason":               "Incorrect Password.",
                "triesRemaining":       session['triesRemaining']  },200

if __name__ == "__main__":
    app.run()
