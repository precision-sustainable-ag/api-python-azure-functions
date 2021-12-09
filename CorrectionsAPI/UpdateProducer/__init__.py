import json
import logging
import os
import sys
import traceback

import azure.functions as func
import mysql.connector
import MySQLdb
import pandas as pd
import psycopg2
import pymysql
import sqlalchemy
from psycopg2 import sql

from ..SharedFunctions import authenticator

pymysql.install_as_MySQLdb()


class SubmitNewEntry:
    def __init__(self, req):
        self.connect_to_crown_live()

        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            self.token = req_body.get('token')
            self.producer_id = req_body.get('producer_id')
            self.code = req_body.get('code')

    def authenticate(self):
        authenticated, response = authenticator.authenticate(self.token)
        if not authenticated:
            return False, response
        else:
            return True, response

    def connect_to_crown_live(self):
        postgres_host = os.environ.get('LIVE_HOST')
        postgres_dbname = os.environ.get('LIVE_CROWN_DBNAME')
        postgres_user = os.environ.get('LIVE_USER')
        postgres_password = os.environ.get('LIVE_PASSWORD')
        postgres_sslmode = os.environ.get('LIVE_SSLMODE')

        # Make postgres connections
        postgres_con_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
            postgres_host, postgres_user, postgres_dbname, postgres_password, postgres_sslmode)
        # print(postgres_con_string)
        self.postgres_con = psycopg2.connect(postgres_con_string)
        self.postgres_cur = self.postgres_con.cursor()
        self.postgres_con.autocommit = True

        postgres_engine_string = "postgresql://{0}:{1}@{2}/{3}".format(
            postgres_user, postgres_password, postgres_host, postgres_dbname)
        self.postgres_engine = sqlalchemy.create_engine(postgres_engine_string)

        print("connected to crown live")

    def update_producer(self):
        sql_string = "UPDATE site_information SET producer_id = %s WHERE code = %s"
        self.postgres_cur.execute(sql_string, (self.producer_id, self.code))
        self.postgres_con.commit()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        sne = SubmitNewEntry(req)

        authenticated, response = sne.authenticate()
        if not authenticated:
            return func.HttpResponse(json.dumps(response), headers={'content-type': 'application/json'}, status_code=400)

        sne.update_producer()

        return func.HttpResponse(body="Successfully updated producer", headers={'content-type': 'application/json'}, status_code=201)

    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        return func.HttpResponse(error, status_code=400)
