from flask import Flask, request, jsonify
import json
import base64
from firebase import firebase

fb = firebase.FirebaseApplication('https://pi8iftm-default-rtdb.firebaseio.com/', None)

app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])

def index():
    global fb
    
    if(request.method == 'POST'):
        return jsonify({'response': ''})
    return "<h1>PI8-Backend</h1>"  
        
if(__name__ == "__main__"):
    
    # teste relays
    for i in range(1,9,1):
        fb.put('/relay',i,True)
    
    app.run(host = 'localhost',port=5000,debug=True)

        

    

