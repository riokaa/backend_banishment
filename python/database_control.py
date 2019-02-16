import MySQLdb
from log import Log
from settings import *

class DBControl(object):
    def __init__(self):
        pass

    def _connect(self):
        # 链接数据库
        self.db = MySQLdb.connect(host=DB_ADRESS, db=DB_NAME, user=DB_USERNAME, password=DB_PASSWORD, charset='utf8')
        #self.db = MySQLdb.connect(host=DB_ADRESS, db=DB_NAME, user='temp', password='123456', charset='utf8')
        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()

    def search(self, sql):
        # select操作使用
        results = []
        self._connect()
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            Log.i('数据库执行SQL: ' + sql)
        except:
            Log.e('数据库执行异常,执行语句: ' + sql)
        finally:
            self.db.close()
            return results

    def execute(self, sql):
        # insert/update/delete操作使用
        self._connect()
        try:
            self.cursor.execute(sql)
            self.db.commit()
            Log.i('数据库执行SQL: ' + sql)
        except:
            self.db.rollback()
            Log.e('数据库执行异常,执行语句: ' + sql)
        finally:
            self.db.close()

if __name__ == '__main__':
    db = DBControl()
