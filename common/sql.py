import pymysql
from config import DB_CONF


class DbOperation:

    @staticmethod
    def connect_db(db_conf):
        """
        返回一个数据库连接对象
        :param db_conf:
        :return:
        """
        return pymysql.Connect(**db_conf)

    @staticmethod
    def close_db(db_connect):
        """
        关闭数据库连接
        :param db_connect:
        :return:
        """
        db_connect.close()

    @staticmethod
    def execute_select_one(cur, sql):
        """
        执行查询语句，返回第一条结果或者None
        :param cur:
        :param sql:
        :return:
        """
        try:
            cur.execute(sql)
            return cur.fetchone()
        except:
            return None

    @staticmethod
    def execute_select_all(cur, sql):
        """
        返回所有查询结果， 或者None
        :param cur:
        :param sql:
        :return:
        """
        try:
            cur.execute(sql)
            return cur.fetchall()
        except:
            return None


# 创建一个数据连接， 全局可用
db = DbOperation.connect_db(DB_CONF)


