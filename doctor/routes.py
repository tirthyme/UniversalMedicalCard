from flask import Blueprint, render_template,session, request, redirect, url_for, json, session, send_from_directory
from flask import current_app as app
from Utilities import Database, Operations
from admin.routes import op


doctor_bp = Blueprint('doctor_bp',__name__,template_folder="templates",static_folder="static")

def get_connection():
    return Database.DB.make_connection(Database.DB())


@doctor_bp.route("/doctor")
def doctor_home():
    return "Doc home"