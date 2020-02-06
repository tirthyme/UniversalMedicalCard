import pymysql

class DB:
    db = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='UMC',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def getConnection():
        return connection
       