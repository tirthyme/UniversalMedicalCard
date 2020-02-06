from flask import Flask, render_template
from Utilities import Database


app = Flask(__name__)

@app.route('/')
def hello():
    db = Database.DB.db
    if(db):
        print ("Database Successful")
    return 'Hello World!'



    
