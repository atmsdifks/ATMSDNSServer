# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import *
from atmsdns_data import app
import random
import os
import sqlite3
base = os.path.abspath(os.curdir)+'\\dnsbase'
sqldirectory = os.path.abspath(os.curdir)+'\\atmsdns_data\\sql\\'
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    list1 = ''
    list2 = ''
    whitesite = ''
    cache2=''
    con = sqlite3.connect(base)
    cur = con.cursor()
    cur.execute("select * from white")
    for row in cur.fetchall():
        whitesite = whitesite + row[0]+'\n'
    cur.execute("select * from ban")
    for row in cur.fetchall():
        list1 = list1 + row[0]+'\n'
    cur.execute("select * from log")
    for row in cur.fetchall():
        list2 = list2 + row[0]+': ['+row[2]+'->'+row[1]+'] from:'+row[3]+' info:'+row[4]+'\n'
    cur.execute("select * from cache")
    for row in cur.fetchall():
        cache2 = cache2 + row[0]+'->'+row[1]+'\n'

    con.close()
    return render_template(
        'index.html',
        title='ATMSDNS',
        year=datetime.now().year,
        bans=list1,
        logs=list2,
        white1=whitesite,
        cache1=cache2,
    )

@app.route('/one')
def one():
    return render_template('one.html')

@app.route('/1')
def log():
    """Renders the contact page."""
    return render_template(
        'redirect.html',
        inform='12345!',

        )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return "123"

@app.route('/inp', methods=['GET'])
def inp():
    if request.method == 'GET':
        if str(request.args['b']) == 'bt1':
            tm = datetime.strftime(datetime.now(), '%H%M%S')+str(random.randint(0, 999999999))+'.sql'
            sql = open(sqldirectory+tm,'w')
            sql.write('insert into white values("'+str(request.args['t'])+'")')
            sql.close()
            return render_template(
                'redirect.html',
                inform=u'Домен "'+str(request.args['t'])+u'" занесен в список разрешенных.',
            )
        if str(request.args['b']) == 'bt2':
            tm = datetime.strftime(datetime.now(), '%H%M%S')+str(random.randint(0, 999999999))+'.sql'
            sql = open(sqldirectory+tm,'w')
            sql.write('insert into ban values("'+str(request.args['t'])+'")')
            sql.close()
            return render_template(
                'redirect.html',
                inform=u'Домен "'+str(request.args['t'])+u'" занесен в список запрещенных.',
            )

@app.route('/add', methods=['GET'])
def add():
    if request.method == 'GET':
        a3 = "Вы ввели текст "+str(request.args['t2'])+" и "+str(request.args['t3'])+" и нажали "+str(request.args['b3'])
        return a3
