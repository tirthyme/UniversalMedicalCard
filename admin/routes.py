from flask import Blueprint, render_template,session, request, redirect, url_for, json, session, send_from_directory
from flask import current_app as app
from Utilities import Database, Operations
from prevailDisease import prevalilingDiseases


admin_bp = Blueprint('admin_bp',__name__,template_folder="templates",static_folder="static")


op = Operations.Operations()
def get_connection():
    return Database.DB.make_connection(Database.DB())
    

def set_user_data():
    context = {}
    context["name"] = session["name"]
    context["role"] = session["role"]
    context["email"] = session["email"]
    return context


@admin_bp.route('/admin',methods=['GET',"POST"])
def admin():
    if request.method == "POST":
        context = {}
        city = request.form.get("city")
        age = request.form.get("age")
        gen = request.form.get("gender")
        context.update(prevalilingDiseases(city,int(age),gen))
        return render_template("admin_panel.html",context = context)
    db = get_connection()
    print(session["email"])
    q = "select * from user_master where email = %s"
    cur = db.cursor()
    if cur.rowcount == 0: 
                return "Wrong Credentials try again" 
    cur.execute(q,session["email"])
    cur = cur.fetchone()
    context = {}
    context.update(set_user_data())
    context.update(prevalilingDiseases("All","All","All"))
    return render_template("admin_panel.html",context = context)


@admin_bp.route('/admin/viewusers', methods=['GET'])
def viewusers():
    context = {}
    db = get_connection()
    q = "select * from user_master"
    cur = db.cursor()
    cur.execute(q)
    print(cur.rowcount)
    context["user_data"] = cur.fetchall()
    return render_template("view_users.html",context = context)


@admin_bp.route('/admin/stateadd',methods=['GET','POST'])
def stateadd():
    if request.method == 'GET':
        return render_template('state_entry.html')
    else:
        db = get_connection()
        cur = db.cursor()
        state = request.form.get("state")
        q = "insert into state_master(state_name) values (%s)"
        state = op.filter_data(state, "string")
        try:
            cur.execute(q,(state))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.stateadd",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/symptomsadd',methods=['GET','POST'])
def symptomsadd():
    if request.method == 'GET':
        return render_template('symptoms_entry.html')
    else:
        db = get_connection()
        cur = db.cursor()
        symptom = request.form.get("symptom")
        sever = request.form.get("sever")
        q = "insert into symptom_master(symptom_name,severity) values (%s,%s)"
        symptom = op.filter_data(symptom, "string")
        sever = op.filter_data(sever, "string")
        try:
            cur.execute(q,(symptom,int(sever)))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.symptomsadd",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/diseaseadd',methods=['GET','POST'])
def diseaseadd():
    if request.method == 'GET':
        db = get_connection()
        cur = db.cursor()
        q = "select * from symptom_master"
        cur.execute(q)
        data = cur.fetchall()
        context = {}
        context['symptoms'] = data
        q = "select * from anatomical_disease_category_master"
        cur.execute(q)
        data = cur.fetchall()
        context['anatomicald'] = data
        q = "select * from global_disease_category_master"
        cur.execute(q)
        data = cur.fetchall()
        context['globald'] = data
        return render_template('disease_entry.html', context = context)
    else:
        db = get_connection()
        cur = db.cursor()
        disease = request.form.get("disease")
        sever = request.form.get("sever")
        globald = request.form.get('global')
        symptoms = request.form.getlist('symptoms')
        anatomical = request.form.get('anatomical')
        q = "insert into disease_master(disease_name, severity, anatomical_cat_id, global_d_id) values (%s,%s,%s,%s)"
        disease = op.filter_data(disease, "string")
        globald = op.filter_data(globald, "string")
        anatomical = op.filter_data(anatomical, "string")
        sever = op.filter_data(sever, "string")
        try:
            cur.execute(q,(disease,int(sever),anatomical,globald))
            try:
                did = cur.lastrowid
                for sid in symptoms:
                    q1 = "insert into disease_symptom_mapper(disease_id,symptom_id) values(%s,%s)"
                    cur1 = db.cursor()
                    cur1.execute(q1,(did,sid))
            except Database.pymysql.MySQLError as e:
                print(e)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
            cur.close()
            cur1.close()
            db.commit()
            db.close()
            return redirect(url_for("admin_bp.diseaseadd",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/anatomicalcategoryadd',methods=['GET','POST'])
def anatcatadd():
    if request.method == 'GET':
        return render_template('anatomical_category_entry.html')
    else:
        db = get_connection()
        cur = db.cursor()
        anatcat = request.form.get("anatcat")
        q = "insert into anatomical_disease_category_master(anatomical_cat_name) values (%s)"
        anatcat = op.filter_data(anatcat, "string")
        try:
            cur.execute(q,(anatcat))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.anatcatadd",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/globalcategoryadd',methods=['GET','POST'])
def globcatadd():
    if request.method == 'GET':
        return render_template('global_d_category_entry.html')
    else:
        db = get_connection()
        cur = db.cursor()
        globcat = request.form.get("globcat")
        q = "insert into global_disease_category_master(global_d_name) values (%s)"
        globcat = op.filter_data(globcat, "string")
        try:
            cur.execute(q,(globcat))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.globcatadd",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/verifyuser',methods=['GET','POST'])
def verifyuser():
    if request.method == 'GET':
        email = request.args.get("email")
        if(email == ""):
            return "NOT VALID"
        q = "SELECT user_master.id, user_master.pfp_url, user_master.uname,user_master.email,user_master.uphone,user_master.aadhar,user_master.aadhar_url,user_master.date_joined, user_master.gender, user_master.isverified, user_master.addr, pin_code_master.pin_code, city_master.city_name, state_master.state_name FROM user_master inner JOIN pin_code_master inner JOIN city_master inner JOIN state_master where email = %s and user_master.pin_code_id = pin_code_master.pin_code_id and pin_code_master.state_id = state_master.state_id and pin_code_master.city_id = city_master.city_id"
        db = get_connection()
        cur = db.cursor()
        cur.execute(q, email)
        if cur.rowcount == 0:
            return "Invalid Input"
        data = cur.fetchone() 
        return render_template("verify_user.html", context = data)
    elif request.method == 'POST':
        query = request.form.get('issue')
        uid = request.form.get("btn")
        aadhar = request.form.get("aadhar")
        if query != "":
            q = "insert into verification_query_master(query, user_id, solved) values (%s,%s,%s)"
            db = get_connection()
            cur= db.cursor()
            try:
                cur.execute(q, (query, uid, 0))
                db.commit()
                cur.close()
                db.close()
                return "query done"
            except Database.pymysql.MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"
        else:
            q = "update user_master set isverified = 1 where id = %s"
            q1 = "insert into medical_card_mapper(medical_card_no,user_id) values(%s,%s)"
            db = get_connection()
            cur= db.cursor()
            try:
                cur.execute(q, uid)
                cur.execute(q1,(aadhar,uid))
                db.commit()
                cur.close()
                db.close()
                return "verified"
            except Database.pymysql.MySQLError as error:
                print(error)
                db.rollback()
                cur.close()
                db.close()
                return "ERROR"

AADHAR_UPLOAD_FOLDER = "static/userdata/aadhar"
@admin_bp.route('/admin/uploads/<filename>')
def uploaded_file_aadhar(filename):
        return send_from_directory(AADHAR_UPLOAD_FOLDER, filename)

IMAGE_UPLOAD_FOLDER = "static/userdata/images"
@admin_bp.route('/admin/uploads/<filename>')
def uploaded_file_pfp(filename):
        return send_from_directory(IMAGE_UPLOAD_FOLDER, filename)

@admin_bp.route('/admin/addmedicalbranch',methods=['GET','POST'])
def medicalbranchadd():
    if request.method == 'GET':
        return render_template('add_medical_branch.html')
    else:
        db = get_connection()
        cur = db.cursor()
        edlevelcat = request.form.get("anatcat")
        q = "insert into medical_ed_level_category(med_ed_cat_name) values (%s)"
        edlevelcat = op.filter_data(edlevelcat, "string")
        try:
            cur.execute(q,(edlevelcat))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.addmedicalbranch",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/addmedicalspecialization',methods=['GET','POST'])
def addmedicalspecialization():
    if request.method == 'GET':
        return render_template('add_medical_specialization.html')
    else:
        db = get_connection()
        cur = db.cursor()
        edspec = request.form.get("anatcat")
        q = "insert into medical_specialization_master(med_spec_name) values (%s)"
        edspec = op.filter_data(edspec, "string")
        try:
            cur.execute(q,(edspec))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.addmedicalspecialization",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"


@admin_bp.route('/admin/addeducationlevel',methods=['GET','POST'])
def addeducationlevel():
    if request.method == 'GET':
        return render_template('add_education_level.html')
    else:
        db = get_connection()
        cur = db.cursor()
        edspec = request.form.get("anatcat")
        q = "insert into medical_ed_level_category(med_ed_cat_name) values (%s)"
        edspec = op.filter_data(edspec, "string")
        try:
            cur.execute(q,(edspec))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.addeducationlevel",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"

@admin_bp.route('/admin/addmedicaltests', methods=["GET","POST"])
def addmedicaltests():
    if request.method == 'GET':
        return render_template('add_medical_tests.html')
    else:
        db = get_connection()
        cur = db.cursor()
        edspec = request.form.get("anatcat")
        q = "insert into medical_tests_master(med_test_name) values (%s)"
        edspec = op.filter_data(edspec, "string")
        try:
            cur.execute(q,(edspec))
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for("admin_bp.addmedicaltests",inserted="true"))
        except Database.pymysql.MySQLError as error:
            print(error)
            db.rollback()
            cur.close()
            db.close()
            return "ERROR"