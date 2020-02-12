from flask import Blueprint, render_template,session
from flask import current_app as app
from Utilities import Database

admin_bp = Blueprint('admin_bp',__name__,template_folder="templates",static_folder="static")

@admin_bp.route('/admin',methods=['GET'])
def admin():
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
    return render_template("admin_panel.html",context = context)

@admin_bp.route('/admin/viewusers', methods=['GET'])
def viewusers():
    context = {}
    context.update(set_user_data())
    db = get_connection()
    q = "select * from user_master"
    cur = db.cursor()
    cur.execute(q)
    print(cur.rowcount)
    context["user_data"] = cur.fetchall()
    return render_template("view_users.html",context = context)

def set_user_data():
    context = {}
    context["name"] = session["name"]
    context["role"] = session["role"]
    context["email"] = session["email"]
    return context

def get_connection():
    return Database.DB.make_connection(Database.DB())