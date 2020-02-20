from flask import render_template
from flask import current_app as app
from Utilities import Database
from pymysql import escape_string


class Operations():
    def filter_data(self,data,type):
        data = str.strip(data)
        data = escape_string(data)
        return data

    def duplicate_check(self, data, type):
        db = Database.DB.make_connection(Database.DB())
        cur = db.cursor()
        if type == "email":
            q = f"select count(id) from user_master where email = {data} LIMIT 1"
            cur.execute(q)
            if cur.rowcount == 0:
                return False
            return True
        elif type == "phone":
            q = f"select count(id) from user_master where uphone = {data} LIMIT 1"
            cur.execute(q)
            if cur.rowcount == 0:
                return False
            return True
        elif type == "aadhar":
            q = f"select count(id) from user_master where aadhar = {data} LIMIT 1"
            cur.execute(q)
            if cur.rowcount == 0:
                return False
            return True

    def allowed_aadhar_file(self, filename):
        ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def allowed_pfp_file(self, filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS