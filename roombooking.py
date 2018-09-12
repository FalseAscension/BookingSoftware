from flask import Flask, Response, request, render_template, session
from passlib.hash import bcrypt
from sqlitedb import database
import json,os

# Initialise Flask App
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('index.html', user="Test User")

@app.route('/api')
def api(req=None):
    return json.dumps({})

status = 200 # doAuthenticate can easily change the status with this...
# API User authentication
@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    status = 200    # Default to satus 200 OK
    return Response(json.dumps(doAuthenticate()), status=status, mimetype="application/json")

def doAuthenticate():
    
    # User is already authenticated...
    if 'UUID' in session:
        return {    "authenticated":    True,
                    "redirect":         "/index.html" }
    
    # We only want to accept JSON data
    if not request.content_type == "application/json":
        status = 400
        return {    "authenticated":    False,
                    "reason":           "Client Error: Data type must be application/json"    }
    
    # Only allow 5 tries.
    if 'triesRemaining' not in session:       # Keep track of how many tries user has remaining.
        session['triesRemaining'] = 5
    elif session['triesRemaining'] == 0:        # User has run out of tries.
        return {    "authenticated":    False,
                    "reason":           "0 tries remaining.",
                    "triesRemaining":   0  }    # Deny authentication for reason 0 tries remaining.
    
    req_data = request.get_json()
    # Ensure we have the correct data.
    if 'email' in req_data and 'password' in req_data:
        email = req_data['email']
        password = req_data['password']
    else:                                       # Client did not provide email and password. 400 Bad Request.
        status = 400
        return {    "authenticated":    False,
                    "reason":           "Client Error: Must provide both email and password"    }
    
    # Initialise the database object and fetch data from it.
    db = database("booking.db")                 
    user = db.getUserByEmail(email)             
    db.close()                                  
    
    # Verify password...
    if bcrypt.verify(password, user['password']):
        session['UUID'] = user['UUID'] 
        return {    "authenticated":   True,    # Allow authenitcation and give location for AJAX redirect.
                    "redirect":        "/index.html"   }

    # Password must be incorrect.
    session['triesRemaining'] -= 1              # Decrement remaining tries.
    return {    "authenticated":        False,  # Deny authentication for reason incorrect password.
                "reason":               "Incorrect Password.",
                "triesRemaining":       session['triesRemaining']  }   

if __name__ == "__main__":
    app.run()
