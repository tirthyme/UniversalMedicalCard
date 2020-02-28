from flask import Flask, render_template, request, session, redirect, url_for, session, flash, send_from_directory, Blueprint
from flask_session import Session
from werkzeug.utils import secure_filename
from Utilities import Database
from flask_wtf.csrf import CSRFProtect
from admin import routes as admin_routes
from doctor import routes as doctor_routes
from hospital import routes as hospital_routes
from radiologist import routes as radiologist_routes
from admin.routes import get_connection
from pymysql import escape_string, MySQLError
from Utilities import Operations
import os
import datetime
AADHAR_UPLOAD_FOLDER = "static/userdata/aadhar"
PFP_UPLOAD_FOLDER = "static/userdata/images"
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
app.register_blueprint(doctor_routes.doctor_bp)
app.register_blueprint(hospital_routes.hospital_bp)
app.register_blueprint(radiologist_routes.radio_bp)

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
        phone = op.filter_data(data["phone"], "phone")
        aadhar = op.filter_data(data['aadhar'], "phone")
        gender = op.filter_data(data['gender'], "phone")
        pin = op.filter_data(data['pincode'], "phone")
        addr = op.filter_data(data['addr'], "phone")
        startdte = op.filter_data(data['startdte'], "phone")
        aadhar_file = request.files['aadhar-file']
        if aadhar_file and op.allowed_aadhar_file(aadhar_file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(aadhar_file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            aadhar_file.save(os.path.join(AADHAR_UPLOAD_FOLDER, filename))

        pfp_file = request.files['image-file']
        if pfp_file and op.allowed_pfp_file(pfp_file.filename):
            ts = datetime.datetime.now().timestamp() 
            pfp_filename = secure_filename(pfp_file.filename)
            pfp_filename = str(ts)+"."+pfp_filename
            pfp_filename = secure_filename(pfp_filename)
            pfp_file.save(os.path.join(PFP_UPLOAD_FOLDER, pfp_filename))
            
        dte = datetime.date.today()
        a = dte.strftime("%Y-%m-%d")
        q = "INSERT INTO user_master(uname, uphone, email, aadhar, aadhar_url, birth_date, isactive, isverified, isloggedin, date_joined, last_login, password, gender, usertype, addr, pin_code_id, pfp_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cur.execute(q,(name,phone,email,aadhar,filename,startdte,1,0,0,a,a,passw,gender,1,addr,pin,pfp_filename))
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
            elif cur["usertype"] == 1:
                session["role"] = "Patient"
                return "Patient Dashboard"
                #return redirect(url_for('admin_bp.admin'))
            elif cur["usertype"] == 2:
                session["role"] = "Doctor"
                q = "select doctor_id from doctor_master where u_id = %s"
                uid = cur["id"]
                db = get_connection()
                cur1 = db.cursor()
                cur1.execute(q,(uid))
                db.close()
                did = cur1.fetchone()
                session["did"] = did["doctor_id"]
                return redirect(url_for('doctor_bp.doctor_home'))
            elif cur["usertype"] == 3:
                session["role"] = "Hospital"
                q = "select hospital_id from hospital_master where u_id = %s"
                uid = cur["id"]
                db = get_connection()
                cur1 = db.cursor()
                cur1.execute(q,(uid))
                db.close()
                hid = cur1.fetchone()
                session["hid"] = hid["hospital_id"]
                return redirect(url_for('hospital_bp.hospital'))
            elif cur["usertype"] == 4:
                session["role"] = "Radiologist"
                q = "SELECT * FROM `radiologist_master` where u_id = %s"
                uid = cur["id"]
                db = get_connection()
                cur1 = db.cursor()
                cur1.execute(q,(uid))
                hid = cur1.fetchone()
                cur1.close()
                db.close()
                session["rid"] = hid["radiologist_id"]
                return redirect(url_for("radio_bp.radiologist"))
                #return redirect(url_for('hospital_bp.hospital'))
            elif cur["usertype"] == 5:
                session["role"] = "Pharma"
                return "Pharma"
                #return redirect(url_for('hospital_bp.hospital'))



@app.route('/doctor_register', methods=['GET','POST'])
def doc_register():
    if request.method == 'GET':
        return render_template("doctor_registration.html")
    elif request.method == 'POST':
        db = get_connection()
        data = request.form.to_dict()
        print(data)
        cur = db.cursor()
        name = op.filter_data(data['uname'], "email")
        email = op.filter_data(data['email'], "email")
        passw = op.filter_data(data['pass'], "email")
        phone = op.filter_data(data["phone"], "phone")
        aadhar = op.filter_data(data['aadhar'], "phone")
        gender = op.filter_data(data['gender'], "phone")
        pin = op.filter_data(data['pincode'], "phone")
        addr = op.filter_data(data['addr'], "phone")
        clinic_addr = op.filter_data(data['clinic_addr'], "phone")
        startdte = op.filter_data(data['startdte'], "phone")
        aadhar_file = request.files['aadhar-file']
        if aadhar_file and op.allowed_aadhar_file(aadhar_file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(aadhar_file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            aadhar_file.save(os.path.join(AADHAR_UPLOAD_FOLDER, filename))

        pfp_file = request.files['image-file']
        if pfp_file and op.allowed_pfp_file(pfp_file.filename):
            ts = datetime.datetime.now().timestamp() 
            pfp_filename = secure_filename(pfp_file.filename)
            pfp_filename = str(ts)+"."+pfp_filename
            pfp_filename = secure_filename(pfp_filename)
            pfp_file.save(os.path.join(PFP_UPLOAD_FOLDER, pfp_filename))
            
        dte = datetime.date.today()
        a = dte.strftime("%Y-%m-%d")
        q = "INSERT INTO user_master(uname, uphone, email, aadhar, aadhar_url, birth_date, isactive, isverified, isloggedin, date_joined, last_login, password, gender, usertype, addr, pin_code_id, pfp_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        q1 = "INSERT INTO doctor_master(u_id,clinic_addr) values (%s,%s)"
        try:
            cur.execute(q,(name,phone,email,aadhar,filename,startdte,1,0,0,a,a,passw,gender,2,addr,pin,pfp_filename))
            try:
                lastrow = cur.lastrowid
                cur.execute(q1,(lastrow,clinic_addr))
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
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


@app.route('/hospital_register',methods=['GET','POST'])
def hospital_register():
    if request.method == "GET":
        return render_template('hospital_registration.html')
    else:
        db = get_connection()
        data = request.form.to_dict()
        print(data)
        cur = db.cursor()
        name = op.filter_data(data['uname'], "email")
        email = op.filter_data(data['email'], "email")
        passw = op.filter_data(data['pass'], "email")
        phone = op.filter_data(data["phone"], "phone")
        aadhar = op.filter_data(data['aadhar'], "phone")
        gender = "Other"
        pin = op.filter_data(data['pincode'], "phone")
        addr = op.filter_data(data['addr'], "phone")
        startdte = op.filter_data(data['startdte'], "phone")
        aadhar_file = request.files['aadhar-file']
        if aadhar_file and op.allowed_aadhar_file(aadhar_file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(aadhar_file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            aadhar_file.save(os.path.join(AADHAR_UPLOAD_FOLDER, filename))

        pfp_file = request.files['image-file']
        if pfp_file and op.allowed_pfp_file(pfp_file.filename):
            ts = datetime.datetime.now().timestamp() 
            pfp_filename = secure_filename(pfp_file.filename)
            pfp_filename = str(ts)+"."+pfp_filename
            pfp_filename = secure_filename(pfp_filename)
            pfp_file.save(os.path.join(PFP_UPLOAD_FOLDER, pfp_filename))

        dte = datetime.date.today()
        a = dte.strftime("%Y-%m-%d")
        q = "INSERT INTO user_master(uname, uphone, email, aadhar, aadhar_url, birth_date, isactive, isverified, isloggedin, date_joined, last_login, password, gender, usertype, addr, pin_code_id, pfp_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        q1 = "INSERT INTO `hospital_master`(u_id, hospital_address) VALUES (%s,%s)"
        try:
            cur.execute(q,(name,phone,email,aadhar,filename,startdte,1,0,0,a,a,passw,gender,2,addr,pin,pfp_filename))
            try:
                lastrow = cur.lastrowid
                cur.execute(q1,(lastrow,addr))
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"    
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


@app.route("/radiologist_register", methods=["GET","POST"])
def radiologist_register():
    if request.method == "GET":
        return render_template("radiologist_registration.html")
    else:
        db = get_connection()
        data = request.form.to_dict()
        print(data)
        cur = db.cursor()
        name = op.filter_data(data['uname'], "email")
        email = op.filter_data(data['email'], "email")
        passw = op.filter_data(data['pass'], "email")
        phone = op.filter_data(data['phone'], "phone")
        aadhar = op.filter_data(data['aadhar'], "phone")
        gender = op.filter_data(data['gender'], "phone")
        pin = op.filter_data(data['pincode'], "phone")
        clinic_addr = op.filter_data(data['clinic_addr'], "phone")
        addr = op.filter_data(data['addr'], "phone")
        startdte = op.filter_data(data['startdte'], "phone")
        aadhar_file = request.files['aadhar-file']
        if aadhar_file and op.allowed_aadhar_file(aadhar_file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(aadhar_file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            aadhar_file.save(os.path.join(AADHAR_UPLOAD_FOLDER, filename))

        pfp_file = request.files['image-file']
        if pfp_file and op.allowed_pfp_file(pfp_file.filename):
            ts = datetime.datetime.now().timestamp() 
            pfp_filename = secure_filename(pfp_file.filename)
            pfp_filename = str(ts)+"."+pfp_filename
            pfp_filename = secure_filename(pfp_filename)
            pfp_file.save(os.path.join(PFP_UPLOAD_FOLDER, pfp_filename))

        license_file = request.files['license-file']
        if pfp_file and op.allowed_pfp_file(license_file.filename):
            ts = datetime.datetime.now().timestamp() 
            license_filename = secure_filename(license_file.filename)
            license_filename = str(ts)+"."+license_filename
            license_filename = secure_filename(license_filename)
            license_file.save(os.path.join(PFP_UPLOAD_FOLDER, license_filename))

        dte = datetime.date.today()
        a = dte.strftime("%Y-%m-%d")
        q = "INSERT INTO user_master(uname, uphone, email, aadhar, aadhar_url, birth_date, isactive, isverified, isloggedin, date_joined, last_login, password, gender, usertype, addr, pin_code_id, pfp_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        q1 = "INSERT INTO radiologist_master(u_id, clinic_addr, license_url) VALUES (%s,%s,%s)"
        try:
            cur.execute(q,(name,phone,email,aadhar,filename,startdte,1,0,0,a,a,passw,gender,3,addr,pin,pfp_filename))
            try:
                lastrow = cur.lastrowid
                cur.execute(q1,(lastrow,clinic_addr,license_filename))
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
        except MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("hello"))

