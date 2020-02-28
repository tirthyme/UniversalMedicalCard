from flask import Flask, render_template, request, session, redirect, url_for, session, flash, send_from_directory, Blueprint
from flask import current_app as app
from Utilities import Database, Operations
from admin.routes import op
import datetime
from pymysql import MySQLError


hospital_bp = Blueprint('hospital_bp',__name__,template_folder="templates",static_folder="static")

def get_connection():
    return Database.DB.make_connection(Database.DB())


@hospital_bp.route('/hospital/')
def hospital():
    return render_template('hospital_dashboard.html')


@hospital_bp.route('/hospital/add_doctor', methods=['GET','POST'])
def add_doctor():
    if(request.method == 'GET'):
        return render_template('add_doctor.html')
    else:
        if(request.form.get("btn") == "doc_request"):
            h_id = session["hid"]
            did = request.form.get("doc_id")
            dte = datetime.date.today()
            a = dte.strftime("%Y-%m-%d")
            q = "insert into hospital_doctor_mapper(hospital_id, doctor_id, request_date, accepted) values (%s,%s,%s,%s)"
            db = get_connection()
            cur = db.cursor()
            try:
                cur.execute(q,(h_id,did,a,-1))
                cur.close()
                db.commit()
                db.close()
                return "Requested"
            except MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
        key = request.form.get('doc_id')
        q = "SELECT * FROM `doctor_master` join user_master join city_master join state_master join pin_code_master ON user_master.id = doctor_master.u_id and user_master.pin_code_id = pin_code_master.pin_code_id and pin_code_master.state_id = state_master.state_id and pin_code_master.city_id = city_master.city_id where user_master.email=%s or user_master.uphone=%s"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(key,key))
        context = {}
        if cur.rowcount != 0:
            context["profile"] = cur.fetchone()
            print(context["profile"])
            did = context["profile"]["doctor_id"]
            q1 = """SELECT CONCAT(medical_ed_level_category.med_ed_cat_name, ", ", medical_education_specialization.med_ed_spec_name, ", ", medical_specialization_master.med_spec_name) as docprof
            FROM doctor_expertise_mapper join medical_specialization_master join medical_ed_level_category join medical_education_specialization 
            where doctor_expertise_mapper.d_id = %s and doctor_expertise_mapper.med_ed_cat_id = medical_ed_level_category.med_ed_cat_id and doctor_expertise_mapper.med_ed_spec_id = medical_education_specialization.med_ed_spec_id and doctor_expertise_mapper.med_spec_id = medical_specialization_master.med_spec_id"""
            cur = db.cursor()
            cur.execute(q1,(did))
            if cur.rowcount != 0:
                context["doctor_profession"] = cur.fetchall()
            else:
                context["doctor_profession"] = {}
            return render_template('add_doctor.html',context=context)
        else:
            context["doctor_data"] = "None"
        return render_template('add_doctor.html',context=context)


@hospital_bp.route('/hospital/doctor_profile/<key>')
def doctor_profile(key):
    if(request.method == 'GET'):
        q = "SELECT * FROM `doctor_master` join user_master join city_master join state_master join pin_code_master where doctor_master.doctor_id = %s AND user_master.id = doctor_master.u_id and user_master.pin_code_id = pin_code_master.pin_code_id and pin_code_master.state_id = state_master.state_id and pin_code_master.city_id = city_master.city_id"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(key))
        context = {}
        if cur.rowcount != 0:
            context["doctor_data"] = cur.fetchone()
            did = context["doctor_data"]["doctor_id"]
            print(did)
            q1 = """SELECT CONCAT(medical_ed_level_category.med_ed_cat_name, ", ", medical_education_specialization.med_ed_spec_name, ", ", medical_specialization_master.med_spec_name) as docprof
            FROM doctor_expertise_mapper join medical_specialization_master join medical_ed_level_category join medical_education_specialization 
            where doctor_expertise_mapper.d_id = %s and doctor_expertise_mapper.med_ed_cat_id = medical_ed_level_category.med_ed_cat_id and doctor_expertise_mapper.med_ed_spec_id = medical_education_specialization.med_ed_spec_id and doctor_expertise_mapper.med_spec_id = medical_specialization_master.med_spec_id"""
            cur = db.cursor()
            cur.execute(q1,(did))
            context["doctor_profession"] = cur.fetchall()
            return render_template('doctor_profile.html',context=context)
        else:
            context["doctor_data"] = "None"
        return render_template('add_doctor.html')
        

@hospital_bp.route("/hospital/viewpastrequests")
def viewpastrequests():
    hid = session["hid"]
    q = """SELECT doctor_master.doctor_id,user_master.uname,user_master.pfp_url, user_master.email, user_master.aadhar,hospital_doctor_mapper.accepted  FROM `hospital_doctor_mapper` join doctor_master join user_master JOIN pin_code_master 
    JOIN city_master join state_master where hospital_id = %s and hospital_doctor_mapper.doctor_id = doctor_master.doctor_id 
    and user_master.id = doctor_master.u_id and user_master.pin_code_id = pin_code_master.pin_code_id 
    and pin_code_master.city_id = city_master.city_id and city_master.state_id = state_master.state_id
    """
    db = get_connection()
    cur = db.cursor()
    cur.execute(q,(hid))
    context = {}
    if cur.rowcount != 0:
        data = cur.fetchall()
        context["doctor_data"] = data
    else:
        context["doctor_data"] = "None"
    cur.close()
    db.close()
    return render_template("view_past_requests.html",context = context)