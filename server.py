"""
run server script
if you messed up the database, just delete the file -> dnsbase
"""
import subprocess
import sqlite3
import os
from atmsdns_data import app
base = os.path.abspath(os.curdir)+'\\dnsbase'
if not os.path.isfile(base):
    print('Create a new database: '+base)
    con = sqlite3.connect(base)
    cur = con.cursor()
    cur.execute('CREATE TABLE LOG(TIME TEXT, INIP TEXT, DOMEN TEXT, SENDIP TEXT, CMD TEXT)')
    cur.execute('CREATE TABLE BAN(DOMEN TEXT)')
    cur.execute('CREATE TABLE WHITE(DOMEN TEXT)')
    cur.execute('CREATE TABLE CACHE(DOMEN TEXT,SENDIP TEXT)')
    cur.execute('CREATE TABLE JOB(JOB TEXT)')
    cur.execute('insert into job values("1")') # default mode
    con.commit()
    con.close()
#subprocess.Popen('python sql.py', shell = True)
subprocess.Popen('python dns_server.py', shell = True)
HOST = '0.0.0.0'
PORT = 80
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.run(HOST, PORT)
