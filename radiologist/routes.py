from flask import Flask, render_template, request, session, redirect, url_for, session, flash, send_from_directory, Blueprint
from flask import current_app as app
from Utilities import Database, Operations
from admin.routes import op
import datetime
from pymysql import MySQLError
from app import secure_filename
import os

def get_connection():
    return Database.DB.make_connection(Database.DB())
    


radio_bp = Blueprint('radio_bp',__name__,template_folder="templates",static_folder="static")

@radio_bp.route("/radiologist/", methods=["GET","POST"])
def radiologist():
    return render_template("dashboard.html")

@radio_bp.route("/radiologist/medical_diagnosis", methods=["GET","POST"])
def medical_diagnosis():
    if request.args.get("id") == None:
        return redirect(url_for("radio_bp.radiologist"))
    else:
        uid = request.args.get("id")
        q = "SELECT diag_id, create_date FROM medical_record_diagnostics_master JOIN medical_record_master on medical_record_master.record_id = medical_record_diagnostics_master.record_id AND medical_record_master.u_id = %s"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(uid))
        context = {}
        if cur.rowcount != 0:
            context["diagnosis"] = cur.fetchall()
        else:
            context["diagnosis"] = "None"
        cur.close()
        db.close()
        return render_template("view_diags.html",context = context)
MEDICAL_TEST_UPLOAD_FOLDER = "static/userdata/user_reports"
@radio_bp.route("/radiologist/medical_tests", methods=["GET","POST"])
def medical_tests():
    if request.args.get("id") == None:
        if request.method == "POST":
            if request.form.get("action") == "addmedicaltestfile":
                pfp_file = request.files['image-file']
                did = request.form.get("diag_id")
                mid = request.form.get("map_id")
                phone = request.form.get("phone")
                rid = session["rid"]
                q1 = "SELECT map_id FROM `report_medical_test_mapper` JOIN user_master JOIN medical_record_master JOIN medical_record_diagnostics_master on user_master.aadhar = medical_record_master.u_id AND medical_record_diagnostics_master.record_id = medical_record_master.record_id WHERE medical_record_diagnostics_master.diag_id = %s and report_medical_test_mapper.map_id = %s and user_master.uphone = %s"
                db = get_connection()
                cur = db.cursor()
                cur.execute(q1,(did,mid,phone))
                if cur.rowcount != 1:
                    return redirect(url_for("radio_bp.medical_tests",duplicate="true", id=did))
                if pfp_file and op.allowed_pfp_file(pfp_file.filename):
                    ts = datetime.datetime.now().timestamp() 
                    pfp_filename = secure_filename(pfp_file.filename)
                    pfp_filename = str(ts)+"."+pfp_filename
                    pfp_filename = secure_filename(pfp_filename)
                    pfp_file.save(os.path.join(MEDICAL_TEST_UPLOAD_FOLDER, pfp_filename))
                    q = "UPDATE report_medical_test_mapper SET file_url = %s, uploaded_by = %s where map_id = %s"
                    try:
                        cur.execute(q,(pfp_filename,rid,mid))
                        db.commit()
                        cur.close()
                        db.close()
                    except MySQLError as error:
                        print(error)
                        db.rollback()
                        cur.close()
                        db.close()
                        return "ERROR"
        return redirect(url_for("radio_bp.medical_tests",id = did))
    else:
        diag_id = request.args.get("id")
        q = "SELECT med_test_id,map_id,med_test_name,diag_id,diag_date, file_url FROM `medical_record_diagnostics_master` JOIN report_medical_test_mapper JOIN medical_tests_master on medical_record_diagnostics_master.diag_id = report_medical_test_mapper.diagnostics_id AND medical_tests_master.med_test_id = report_medical_test_mapper.test_id WHERE diag_id = %s"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q,(diag_id))
        context = {}
        context["medical_tests"] = cur.fetchall()
        return render_template("view_medical_tests.html", context = context)

        