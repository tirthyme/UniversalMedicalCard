from flask import Flask, render_template, request, session, redirect, url_for, session, flash, send_from_directory, Blueprint
from flask import current_app as app
from Utilities import Database, Operations
from admin.routes import op
from app import secure_filename
import datetime,os
from pymysql import escape_string, MySQLError

doctor_bp = Blueprint('doctor_bp',__name__,template_folder="templates",static_folder="static")

def get_connection():
    return Database.DB.make_connection(Database.DB())

def isRequestMethodGet():
    if request.method == "GET":
        return True
    else:
        return False

@doctor_bp.route("/doctor/")
def doctor_home():
    return render_template('doctor_dashboard.html')

DOCTOR_CERTI_UPLOAD_FOLDER = "static/userdata/doctor_certificates"

@doctor_bp.route("/doctor/addmedicalexpertise", methods=["GET","POST"])
def addmedicalexpertise():
    if isRequestMethodGet():
        context = {}
        q = "select * from medical_ed_level_category"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q)
        context["education_level"] = cur.fetchall()
        q1 = "select * from medical_education_specialization"
        cur.execute(q1)
        context["education_specialization"] = cur.fetchall()
        q2 = "select * from medical_specialization_master"
        cur.execute(q2)
        context["medical_specialization"] = cur.fetchall()
        return render_template('add_medical_expertise.html', context = context)
    else:
        medbranch = request.form.get("medbranch")
        edlevel = request.form.get("edlevel")
        specialization = request.form.get("specialization")
        certi_file = request.files['certi']
        if certi_file and op.allowed_aadhar_file(certi_file.filename):
            ts = datetime.datetime.now().timestamp() 
            filename = secure_filename(certi_file.filename)
            filename = str(ts)+"."+filename
            filename = secure_filename(filename)
            certi_file.save(os.path.join(DOCTOR_CERTI_UPLOAD_FOLDER, filename))
        did = session["did"] 
        q = "insert into doctor_expertise_mapper(d_id,med_ed_cat_id,med_ed_spec_id,med_spec_id) values (%s,%s,%s,%s)"
        db = get_connection()
        cur = db.cursor()
        try:
                cur.execute(q,(did,edlevel,medbranch,specialization))
                cur.close()
                db.commit()
                db.close()
        except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
        return redirect(url_for('doctor_bp.addmedicalexpertise'))

@doctor_bp.route("/doctor/search_patient", methods=["GET","POST"])
def searchpatient():
    if isRequestMethodGet():
        return render_template('search_patient.html')
    else:
        key = request.form.get("key")
        q = "select uname, pfp_url, email, aadhar from user_master where aadhar = %s or email = %s or uphone = %s"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(key,key,key))
        context={}
        if cur.rowcount == 0:
            context["profile"] = "None"
        else:
            context["profile"] = cur.fetchone()
        return render_template('search_patient.html', context=context)


@doctor_bp.route("/doctor/viewhospitalrequests", methods=["GET","POST"])
def viewhospitalrequests():
    if isRequestMethodGet():
        did = session["did"]
        q = """SELECT hospital_doctor_mapper.hos_doc_id,user_master.email, user_master.uname,user_master.pfp_url, hospital_master.hospital_id ,hospital_master.hospital_address, hospital_doctor_mapper.request_date, hospital_doctor_mapper.accepted FROM `hospital_doctor_mapper`
        JOIN hospital_master join user_master on hospital_master.hospital_id = hospital_doctor_mapper.hospital_id and hospital_master.u_id = user_master.id 
        WHERE hospital_doctor_mapper.doctor_id = %s"""
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(did))
        context = {}
        if(cur.rowcount != 0):
            context["hospital_requests"] = cur.fetchall()
        else:
            context["hospital_requests"] = "None"
        db.close()
        cur.close()
        return render_template("view_hospital_requests.html",context = context)
    else:
        btn = request.form.get("btn")
        hdid = request.form.get("hid")
        if(btn == "accepted"):
            q = "UPDATE hospital_doctor_mapper SET accepted = %s WHERE hos_doc_id = %s"
            db = get_connection()
            cur = db.cursor()
            try:
                cur.execute(q,(1,hdid))
                cur.close()
                db.commit()
                db.close()
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
        else:
            hdid = request.form.get("hid")
            q = "update hospital_doctor_mapper set accepted = 0 where hos_doc_id = %s"
            db = get_connection()
            cur = db.cursor()
            try:
                cur.execute(q,(hdid))
                cur.close()
                db.commit()
                db.close()
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
    return redirect(url_for("doctor_bp.viewhospitalrequests"))

@doctor_bp.route("/doctor/patient_profile", methods=["GET","POST"])
def patient_profile():
    if request.args.get("id") == None:
        return render_template('search_patient.html')
    else:
        key = request.args.get("id")
        q = "SELECT user_master.id, user_master.pfp_url, user_master.uname,user_master.email,user_master.uphone,user_master.aadhar,user_master.aadhar_url,user_master.date_joined, user_master.gender, user_master.isverified, user_master.addr, pin_code_master.pin_code, city_master.city_name, state_master.state_name FROM user_master inner JOIN pin_code_master inner JOIN city_master inner JOIN state_master where aadhar = %s and user_master.pin_code_id = pin_code_master.pin_code_id and pin_code_master.state_id = state_master.state_id and pin_code_master.city_id = city_master.city_id"
        db = get_connection()
        cur= db.cursor()
        cur.execute(q,(key))
        context = {}
        if cur.rowcount == 0:
            context["profile"] = "None"
            return render_template('search_patient.html', context=context)
        else:
            context["profile"] = cur.fetchone()
            uid = context["profile"]["aadhar"]
            q = "select * from medical_record_master where u_id = %s"
            cur.execute(q,(uid))
            context["past_med_records"] = cur.fetchall()
            return render_template("view_patient_profile.html", context = context)


@doctor_bp.route("/doctor/addmedicalrecord",methods=["GET","POST"])
def addmedicalrecord():
    if isRequestMethodGet():
        return redirect(url_for("doctor_bp.searchpatient"))
    else:
        if request.form.get("action") == "addmedicalrecord":
            context = {}
            pid = request.form.get("patient_id")
            context["patient_id"] = pid
            context["patient_name"] = request.form.get("patient_name")
            q = """SELECT hospital_doctor_mapper.hos_doc_id, user_master.uname, hospital_master.hospital_id FROM `hospital_doctor_mapper` JOIN hospital_master join user_master on hospital_master.hospital_id = hospital_doctor_mapper.hospital_id and hospital_master.u_id = user_master.id WHERE hospital_doctor_mapper.doctor_id = %s and hospital_doctor_mapper.accepted = 1"""
            did = session["did"]
            db = get_connection()
            cur = db.cursor()
            cur.execute(q, (did))
            if cur.rowcount != 0:
                context["hospitals"] = cur.fetchall()
                context["hospital_no"] = cur.rowcount
            else:
                return "No Hospitals Joined, Join a hospital to add patient record"
            q = "select * from symptom_master"
            cur.execute(q)
            context["symptoms"] = cur.fetchall()
            q = "select * from disease_master"
            cur.execute(q)
            context["diseases"] = cur.fetchall()
            return render_template("add_medical_record.html", context = context)
        elif request.form.get("action") == "medicalrecordinsert":
            pid = request.form.get("patient_id")
            hid = request.form.get("hospital_id")
            did = session["did"]
            symptoms = request.form.getlist('symptom')
            diseases = request.form.getlist('disease')
            symptoms = ','.join(symptoms)
            diseases = ','.join(diseases)
            diagnosis = request.form.get('diagnosis')
            pincode = request.form.get('pincode')
            a = datetime.date.today().strftime("%Y-%m-%d")
            q = """ 
            INSERT INTO medical_record_master(u_id, d_id, create_date, hospital_id, primary_diagnosis, symptoms, diseases, last_checked, pin_code_id) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
             """
            db = get_connection()
            cur = db.cursor()
            try:
                cur.execute(q, (pid,did,a,hid,diagnosis,symptoms,diseases,a,pincode))
                cur.close()
                db.commit()
                db.close()
                return redirect(url_for("doctor_bp.patient_profile",key=pid))
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"

@doctor_bp.route("/doctor/viewmedicalrecord", methods=["GET","POST"])
def viewmedicalrecord():
    context = {}
    key = request.args.get("id")

    patient_data = "SELECT pin_code_master.pin_code, record_id, pin_code_master.area_name, city_master.city_name, state_master.state_name, user_master.pfp_url, aadhar, primary_diagnosis, medical_file_url, gender, medical_file_url, user_master.aadhar, user_master.uname as 'patient_name', medical_record_master.create_date FROM `medical_record_master` JOIN user_master JOIN pin_code_master JOIN city_master JOIN state_master ON medical_record_master.pin_code_id = pin_code_master.pin_code_id and pin_code_master.state_id = state_master.state_id and pin_code_master.city_id = city_master.city_id WHERE medical_record_master.record_id = %s ;" % (key)
    doctor_data = "SELECT doctor_master.doctor_id, doctor_master.clinic_addr, user_master.uname, user_master.uphone, user_master.email FROM `medical_record_master` JOIN doctor_master JOIN user_master on medical_record_master.d_id = doctor_master.doctor_id and user_master.id = doctor_master.u_id WHERE medical_record_master.record_id = %s ;" % (key)
    hospital_data = "SELECT hospital_master.hospital_id, hospital_master.hospital_address, user_master.uname as 'hospital_name', user_master.uphone as 'hospital_phone', email FROM `medical_record_master` JOIN hospital_master JOIN user_master on medical_record_master.hospital_id = hospital_master.hospital_id and user_master.id = hospital_master.u_id WHERE medical_record_master.record_id = %s ;" % (key)
    medical_tests = "select * from medical_tests_master"
    medical_diagnostic_records = "select * from medical_record_diagnostics_master where record_id = %s" % (key)
    db = get_connection()
    cur = db.cursor()
    cur.execute(patient_data)
    context["patient_data"] = cur.fetchone()
    cur.execute(doctor_data)
    context["doctor_data"] = cur.fetchone()
    cur.execute(hospital_data)
    context["hospital_data"] = cur.fetchone()
    cur.execute(medical_tests)
    context["medical_tests"] = cur.fetchall()
    cur.execute(medical_diagnostic_records)
    context["medical_diagnostic_records"] = cur.fetchall()
    return render_template("view_medical_record.html", context = context)

PRESCRIPTION_INSERT_FOLDER = "static/userdata/user_reports"

@doctor_bp.route("/doctor/addmedicaldiagnosis", methods=["GET","POST"])
def addmedicaldiagnosis():
    if isRequestMethodGet():
        return redirect(url_for("doctor_bp.searchpatient"))
    else:
        if(request.form.get("record_id")) == None:
            return redirect(url_for("doctor_bp.searchpatient"))
        else:
            rid = request.form.get("record_id")
            if request.form.get("action") == "medicaldiagnosisinsert":
                prescription = request.files['prescription']
                if prescription and op.allowed_aadhar_file(prescription.filename):
                    ts = datetime.datetime.now().timestamp() 
                    filename = secure_filename(prescription.filename)
                    filename = str(ts)+"."+filename
                    filename = secure_filename(filename)
                    prescription.save(os.path.join(PRESCRIPTION_INSERT_FOLDER, filename))
                else:
                    filename = "None"
                symptoms = request.form.getlist('symptom')
                diseases = request.form.getlist('disease')
                medical_tests = request.form.getlist('medical_tests')
                symptoms = ','.join(symptoms)
                diseases = ','.join(diseases)
                diagnosis = request.form.get('diagnosis')
                a = datetime.date.today().strftime("%Y-%m-%d")
                q = "INSERT INTO medical_record_diagnostics_master(record_id, diagnosis, symptoms, diseases, diag_date) VALUES (%s,%s,%s,%s,%s)"
                q1 = "INSERT INTO report_medical_test_mapper(diagnostics_id, test_id, create_date, file_url) VALUES (%s,%s,%s,%s)"
                try:
                    db = get_connection()
                    cur = db.cursor()
                    cur.execute(q, (rid,diagnosis,symptoms, diseases, a))
                    diag_id = cur.lastrowid
                    for data in medical_tests:
                        cur.execute(q1,(diag_id,data,a,"NONE"))
                    cur.close()
                    db.commit()
                    db.close()
                    return redirect(url_for("doctor_bp.viewmedicalrecord",id=rid))
                except MySQLError as error:
                    print(error)
                    db.rollback()
                    cur.close()
                    db.close()
                    return "ERROR"
            else:                
                context = {}
                rid = request.form.get("record_id")
                context["record_id"] = rid
                q = "select * from symptom_master"
                db = get_connection()
                cur = db.cursor()
                cur.execute(q)
                context["symptoms"] = cur.fetchall()
                q = "select * from disease_master"
                cur.execute(q)
                context["diseases"] = cur.fetchall()
                q = "select * from medical_tests_master"
                cur.execute(q)
                context["medical_tests"] = cur.fetchall()
                cur.close()
                db.close()
                return render_template("add_medical_diagnosis.html", context = context)

@doctor_bp.route("/doctor/viewdiagnosis", methods=["GET","POST"])
def viewdiagnostics():
    diag_id = request.args.get("diag_id")
    context = {}
    q = "select * from medical_record_diagnostics_master where diag_id = %s"
    db = get_connection()
    cur = db.cursor()
    cur.execute(q,(diag_id))
    context["diagnosis"] =  cur.fetchone()
    q = "select disease_name from disease_master where disease_id in (%s)" % context["diagnosis"]["diseases"]
    cur.execute(q)
    context["diseases"] =  cur.fetchall()
    q = "select symptom_name from symptom_master where symptom_id in (%s)" % context["diagnosis"]["symptoms"]
    cur.execute(q)
    context["symptoms"] =  cur.fetchall()
    strs = ""
    for data in context["symptoms"]:
        strs = strs + data["symptom_name"] +","
    context["symptoms"] = strs
    strs = ""
    for data in context["diseases"]:
        strs = strs+data["disease_name"] +","
    context["diseases"] = strs
    q = "SELECT medical_tests_master.med_test_name, medical_tests_master.med_test_id FROM `report_medical_test_mapper` JOIN medical_record_diagnostics_master JOIN medical_tests_master on report_medical_test_mapper.diagnostics_id = medical_record_diagnostics_master.diag_id and medical_tests_master.med_test_id = report_medical_test_mapper.test_id WHERE diagnostics_id = %s"
    cur.execute(q,(diag_id))
    context["medical_tests"] =  cur.fetchall()
    return render_template("view_medical_diagnosis.html",context=context)