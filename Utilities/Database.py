import pymysql
class DB:
        def make_connection(self):
            try:
               db = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='UMC',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
            except Exception as error:
                print(error)
            return db