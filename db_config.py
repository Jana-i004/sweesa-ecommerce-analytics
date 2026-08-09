"""
db_config.py
إعدادات الاتصال المشتركة بقاعدة البيانات sweesa_ecommerce_db

عدّلي القيم أدناه حسب إعدادات جهازك (MySQL / phpMyAdmin المحلي).
"""

import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "PUT_YOUR_MYSQL_PASSWORD_HERE",
    "database": "sweesa_ecommerce_db",
    "charset": "utf8mb4",
}


def get_connection():
    """
    تحاول فتح اتصال بقاعدة البيانات باستخدام mysql.connector.
    عند فشل الاتصال تُطبع رسالة خطأ وتُرجع None.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

        if connection.is_connected():
            return connection

    except Error as e:
        print(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
        return None


def get_engine():
    """
    تُرجع SQLAlchemy engine لاستخدامه مع pandas.read_sql.
    """
    try:
        url = URL.create(
            drivername="mysql+mysqlconnector",
            username=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            query={"charset": DB_CONFIG["charset"]},
        )

        engine = create_engine(url)
        return engine

    except Exception as e:
        print(f"❌ فشل إنشاء اتصال SQLAlchemy: {e}")
        return None