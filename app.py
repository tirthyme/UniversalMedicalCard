from flask import Flask, render_template, request, session, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.utils import secure_filename
from Utilities import Database
from flask_wtf.csrf import CSRFProtect
from admin import routes as admin_routes
from admin.routes import get_connection
from pymysql import escape_string, MySQLError
from Utilities import Operations
import os
import datetime

AADHAR_UPLOAD_FOLDER = "static/userdata/aadhar"
PFP_UPLOAD_FOLDER = "static/userdata/aadhar"
app = Flask(__name__)
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config.update(
    SECRET_KEY = 'you-will-never-guess'
)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['MAX_CONTENT_LENGTH'] = 1024*400
Session(app)
op = Operations.Operations()
app.register_blueprint(admin_routes.admin_bp)

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
    db.close()
    return render_template('index.html',context = context)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template("userregistration1.html")
    elif request.method == 'POST':
        db = get_connection()
        data = request.form.to_dict()
        print(data)
        cur = db.cursor()
        name = op.filter_data(data['uname'], "email")
        email = op.filter_data(data['email'], "email")
        passw = op.filter_data(data['pass'], "email")
        phone = op.filter_data(data['email'], "phone")
        aadhar = op.filter_data(data['aadhar'], "phone")
        gender = op.filter_data(data['gender'], "phone")
        pin = op.filter_data(data['pincode'], "phone")
        addr = op.filter_data(data['addr'], "phone")
        file = request.files['aadhar-file']
        if file and op.allowed_file(file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            file.save(os.path.join(AADHAR_UPLOAD_FOLDER, filename))
        dte = datetime.date.today()
        a = dte.strftime("%Y-%m-%d")
        q = "INSERT INTO user_master(uname, uphone, email, aadhar, aadhar_url, isactive, isverified, isloggedin, date_joined, last_login, password, gender, usertype, addr, pin_code_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cur.execute(q,(name,phone,email,aadhar,filename,1,0,0,a,a,passw,gender,1,addr,pin))
            #print(cur.rowcount, "Record inserted successfully into Laptop table")
            db.commit()
            cur.close()
            db.close()
            return "Registration Successful"
        except MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"
    else:
        return "WRONG METHOD"
        

    
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
            db.close()
            print(cur)
            session["logged"] = True
            session["email"] = cur["email"]
            session["name"] = cur["uname"]
            if cur["usertype"] == 0:
                session["role"] = "Superuser"
                return redirect(url_for('admin_bp.admin'))
