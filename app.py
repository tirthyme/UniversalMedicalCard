from flask import Flask, render_template
from Utilities import Database


app = Flask(__name__)

@app.route('/')
def hello(): 
    db = Database.DB.make_connection(Database.DB())
    if(db):
        print ("Database Successful")
    cur = db.cursor()
    cur.execute("select COUNT(uname),count(id) from user_master")
    print(cur.description)
    context = cur.fetchall() 
    print(type(context))
    print(context)
    cur.close()
    return render_template('index.html',context = context)

@app.route('/register')
def register():
    return render_template("index.html")
    