#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import mysql.connector

class MySQL(object):
    def __init__(self, host, user, password, database=None, port=3306):
        self.con = mysql.connector.connect(host=host, user=user, password=password,database=database, port=port)
        self.cur = self.con.cursor()
    
    def run(self, sql):
        self.cur.execute(sql)
    
    def close(self):
        self.cur.close()
        self.con.close()
    
if __name__=="__main__":
    logging.basicConfig(
        level = logging.DEBUG, 
        format= '%(asctime)-15s [%(levelname)-8s] - %(message)s'
    )
    
    con = mysql.connector.connect(host="172.16.132.71", user="kbm1422", password="ManinBlack2",database="testlink")
    cur = con.cursor()
    cur.execute("", ())
