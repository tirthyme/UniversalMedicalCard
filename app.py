from flask import Flask, render_template, request, session, redirect, url_for
from Utilities import Database
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config.update(
    SECRET_KEY = 'you-will-never-guess'
)

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
    return render_template("userregistration.html")
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template("page-login.html")
    elif request.method == "POST":
            db = Database.DB.make_connection(Database.DB())
            cur = db.cursor()
            q = "select * from user_master where email = %s and password = %s"
            print((request.form.get('email') + " 00 " + (request.form.get('password'))))
            cur.execute(q,(request.form.get('email'), (request.form.get('password'))))
            if cur.rowcount == 0: 
                context = {}
                context["error"] = "Wrong Credentials try again"
                return render_template('page-login.html',context = context)
            cur = cur.fetchone()
            print(cur)
            return redirect(url_for('admin'))

@app.route('/admin',methods=['GET'])
def admin():
    return render_template('utilities/admin_panel.html')