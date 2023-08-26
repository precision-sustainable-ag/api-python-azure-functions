import os
import psycopg2
import pymysql
import sqlalchemy


pymysql.install_as_MySQLdb()


def connect_to_crown(environment):
    if environment == "Production":
        crown_host = os.environ.get('LIVE_HOST')
        crown_dbname = os.environ.get('LIVE_CROWN_DBNAME')
        crown_user = os.environ.get('LIVE_USER')
        crown_password = os.environ.get('LIVE_PASSWORD')
        crown_sslmode = os.environ.get('LIVE_SSLMODE')
        # Make crown connections
        crown_con_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
            crown_host, crown_user, crown_dbname, crown_password, crown_sslmode)

        crown_engine_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            crown_user, crown_password, crown_host, "5432", crown_dbname)
        crown_engine = sqlalchemy.create_engine(crown_engine_string)
    else:
        crown_host = os.environ.get('LOCAL_PROD_HOST')
        crown_dbname = os.environ.get('LOCAL_PROD_DBNAME')
        crown_user = os.environ.get('LOCAL_PROD_USER')
        crown_password = os.environ.get('LOCAL_PROD_PASSWORD')
        crown_sslmode = os.environ.get('LOCAL_PROD_SSLMODE')
        crown_port = os.environ.get('LOCAL_PROD_PORT')
        # Make crown connections
        crown_con_string = "host={0} user={1} dbname={2} password={3} sslmode={4} port={5}".format(
            crown_host, crown_user, crown_dbname, crown_password, crown_sslmode, crown_port)

        crown_engine_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            crown_user, crown_password, crown_host, crown_port, crown_dbname)
        crown_engine = sqlalchemy.create_engine(crown_engine_string)

    print(crown_con_string)

    # print(crown_con_string)
    crown_con = psycopg2.connect(crown_con_string)
    crown_cur = crown_con.cursor()
    crown_con.autocommit = True

    print("connected to crown {}".format(environment))

    return crown_con, crown_cur, crown_engine


def connect_to_shadow(environment):
    if environment == "Production":
        shadow_host = os.environ.get('LIVE_HOST')
        shadow_dbname = os.environ.get('LIVE_SHADOW_DBNAME')
        shadow_user = os.environ.get('LIVE_USER')
        shadow_password = os.environ.get('LIVE_PASSWORD')
        shadow_sslmode = os.environ.get('LIVE_SSLMODE')
        # Make shadow connections
        shadow_con_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
            shadow_host, shadow_user, shadow_dbname, shadow_password, shadow_sslmode)

        shadow_engine_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            shadow_user, shadow_password, shadow_host, "5432", shadow_dbname)
        shadow_engine = sqlalchemy.create_engine(shadow_engine_string)
    else:
        shadow_host = os.environ.get('LOCAL_SHADOW_HOST')
        shadow_dbname = os.environ.get('LOCAL_SHADOW_DBNAME')
        shadow_user = os.environ.get('LOCAL_SHADOW_USER')
        shadow_password = os.environ.get('LOCAL_SHADOW_PASSWORD')
        shadow_sslmode = os.environ.get('LOCAL_SHADOW_SSLMODE')
        shadow_port = os.environ.get('LOCAL_SHADOW_PORT')
        # Make shadow connections
        shadow_con_string = "host={0} user={1} dbname={2} password={3} sslmode={4} port={5}".format(
            shadow_host, shadow_user, shadow_dbname, shadow_password, shadow_sslmode, shadow_port)

        shadow_engine_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            shadow_user, shadow_password, shadow_host, shadow_port, shadow_dbname)
        shadow_engine = sqlalchemy.create_engine(shadow_engine_string)

    # # Make shadow connections
    shadow_con = psycopg2.connect(shadow_con_string)
    shadow_cur = shadow_con.cursor()
    shadow_con.autocommit = True

    print("connected to shadow {}".format(environment))

    return shadow_con, shadow_cur, shadow_engine


def connect_to_mysql():
    mysql_host = os.environ.get('MYSQL_HOST')
    mysql_dbname = os.environ.get('MYSQL_DBNAME')
    mysql_user = os.environ.get('MYSQL_USER')
    mysql_password = os.environ.get('MYSQL_PASSWORD')

    mysql_con = pymysql.connect(user=mysql_user, database=mysql_dbname, host=mysql_host,
                                password=mysql_password, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
    mysql_cur = mysql_con.cursor()
    mysql_con.autocommit = True

    # Make mysql connections
    mysql_engine_string = "mysql://{0}:{1}@{2}/{3}".format(
        mysql_user, mysql_password, mysql_host, mysql_dbname)
    mysql_engine = sqlalchemy.create_engine(mysql_engine_string)

    print("connected to mysql live")

    return mysql_con, mysql_cur, mysql_engine
