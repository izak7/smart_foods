#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Samuel Sekiwere <sekiskylink@gmail.com>

import os
import web
import urllib
import httplib
import logging
import psycopg2
import re
import time
from datetime import datetime
from datetime import timedelta
from urllib import urlencode
from urllib import urlopen
#from web.contrib.template import render_mako
from web.contrib.template import render_jinja
from pagination import *
from web import form
from models import *

class AppURLopener(urllib.FancyURLopener):
	version = "Smart Foods /0.1"

urllib._urlopener = AppURLopener()

#logging.basicConfig( format='%(asctime)s:%(levelname)s:%(message)s', filename='/tmp/smartfoods.log',
#		datefmt='%Y-%m-%d %I:%M:%S', level=logging.DEBUG)

#DB confs
db_host = 'localhost'
db_name = 'smart_foods'
db_user = 'postgres'
db_passwd = 'postgres'


urls = (
        "/","Index",
        "/suppliers","Suppliers",
        "/supplies","RecordSupply",
        "/rawmaterials","RawMaterials",
        "/products","Products",
        "/transactions","Transactions",
        "/settings","Settings",
        "/users","Users",
        "/logout","Logout",
        )

#web.config.smtp_server = 'mail.mydomain.com'
web.config.debug = False

app = web.application(urls, globals()) #XXX man autoreload = True  was killing me!!
db = web.database(
    dbn='postgres',
    user=db_user,
    pw=db_passwd,
    db=db_name,
    host=db_host
    )

store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store, initializer={'loggedin':False})
#if web.config.get('_session') is None:
#    session = web.session.Session(app, store, initializer={'loggedin':False})
#    web.config._session = session
#else:
#    session = web.config._session
#render = render_mako(
#        directories=[os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),],
#        input_encoding='utf-8',
#        output_encoding='utf-8',
#        )
render = render_jinja(
            'templates',
            encoding = 'utf-8')
render._lookup.globals.update(
        ses=session
        )

SETTINGS = {
        'PAGE_LIMIT': 5,
        }

## Helper Classes and Functions
def default(*args):
    p = [i for i in args if i or i==0]
    if p.__len__(): return p[0]
    if args.__len__(): return args[args.__len__()-1]
    return None

def require_login(f):
    """usage
    @require_login
    def GET(self):
        ..."""
    def decorated(*args, **kwargs):
        if session.loggedin == False:
            session.logon_err = "Please Logon"
            return web.seeother("/")
        else:
            session.logon_err = ""
        return f(*args,**kwargs)

    return decorated

class Index:
    def GET(self):
        l = locals(); del l['self']; #l['ses'] = session
        return render.start(**l)
    def POST(self):
        params = web.input(username="", password="")
        username = params.username
        password = params.password
        r = auth_user(db, username, password)
        if r[0]:
            session.loggedin = True
            info = r[1]
            session.username = info.firstname + " " + info.lastname
            l = locals(); del l['self']; #l['ses'] = session
            return web.seeother("/suppliers")
        else:
            session.loggedin = False
            session.logon_err = r[1]

        l = locals(); del l['self']; #l['ses'] = session
        return render.logon(**l)

class Suppliers:
    @require_login
    def GET(self):
        params = web.input(page=1, ed="",d_id="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0
        ed = params.ed
        if ed:
            r = db.query("SELECT * FROM suppliers WHERE id = %s"%ed)
            if r:
                rx = r[0]
                name=rx.name; address=rx.address; tel=rx.telephone; email=rx.email
        if params.d_id:
            db.query("DELETE FROM suppliers WHERE id=%s" % params.d_id)

        dic = lit(relations='suppliers', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/suppliers","?page=")
        print pagination_str

        l = locals(); del l['self'];
        return render.suppliers(**l)

    def POST(self):
        params = web.input(page=1, ed="", name="",
                address="", tel="", email="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0

        if not params.name or not params.address or \
                not params.tel or not params.email:
                    return render.suppliers(err_msg="Missing Parameters")

        with db.transaction():
            if params.ed:
                #we're editing
                pass
                update_sql = ("UPDATE suppliers SET name='%s', address='%s', "
                        " email='%s', telephone='%s' WHERE id = %s ")
                update_sql = update_sql % (params.name, params.address,
                        params.email, params.tel, params.ed)
                db.query(update_sql)
            else:
                db.insert('suppliers', name=params.name, email= params.email,
                        address= params.address, telephone=params.tel)

        dic = lit(relations='suppliers', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/suppliers","?page=")

        l = locals(); del l['self']; #l['ses'] = session
        return render.suppliers(**l)

class RawMaterials:
    @require_login
    def GET(self):
        params = web.input(page=1, ed="", d_id="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0
        ed = params.ed

        if ed:
            r = db.query("SELECT * FROM raw_materials WHERE id = %s"%ed)
            if r:
                rx = r[0]
                name=rx.name; address=rx.address; tel=rx.telephone; email=rx.email
        if params.d_id:
            db.query("DELETE FROM raw_materials WHERE id=%s" % params.d_id)

        dic = lit(relations='raw_materials', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/rawmaterials","?page=")

        l = locals(); del l['self'];
        return render.raw_materials(**l)

    def POST(self):
        params = web.input(page=1, ed="", d_id="",name="", descr="", qrank="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0

        if not params.name:
            return render.products(err_msg="Name is missing!")

        with db.transaction():
            if params.ed:
                update_sql = ("UPDATE raw_materials SET name='%s', descr='%s', quality_rank = '%s' WHERE id = %s ")
                update_sql = update_sql % (params.name, params.descr, params.qrank, params.ed)
                db.query(update_sql)
            else:
                db.insert('raw_materials', name=params.name, descr= params.descr,
                        quality_rank=params.qrank)
            #delet code follows

        dic = lit(relations='raw_materials', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/rawmaterials","?page=")

        l = locals(); del l['self'];
        return render.raw_materials(**l)

class Products:
    @require_login
    def GET(self):
        params = web.input(page=1, ed="", d_id="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0
        ed = params.ed

        if ed:
            r = db.query("SELECT * FROM products WHERE id = %s"%ed)
            if r:
                rx = r[0]
                name=rx.name; descr = rx.descr

        if params.d_id:
            db.query("DELETE FROM products WHERE id=%s" % params.d_id)

        dic = lit(relations='products', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/products","?page=")

        l = locals(); del l['self'];
        return render.products(**l)
    def POST(self):
        params = web.input(page=1, ed="", d_id="",name="", descr="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0

        if not params.name:
            return render.products(err_msg="Name is missing!")

        with db.transaction():
            if params.ed:
                update_sql = ("UPDATE products SET name='%s', descr='%s'  WHERE id = %s ")
                update_sql = update_sql % (params.name, params.descr, params.ed)
                db.query(update_sql)
            else:
                db.insert('products', name=params.name, descr= params.descr)
            #delet code follows

        dic = lit(relations='products', fields="*",
                order="name  ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/products","?page=")
        l = locals(); del l['self'];
        return render.products(**l)

class Transactions:
    @require_login
    def GET(self):
        l = locals(); del l['self'];
        return render.transactions(**l)
    def POST(self):
        params = web.input()

        l = locals(); del l['self'];
        return render.transactions(**l)

class Users:
    @require_login
    def GET(self):
        l = locals(); del l['self'];
        return render.users(**l)
    def POST(self):
        params = web.input()

        l = locals(); del l['self'];
        return render.users(**l)

class Settings:
    @require_login
    def GET(self):
        l = locals(); del l['self'];
        return render.settings(**l)
    def POST(self):
        params = web.input()

        l = locals(); del l['self'];
        return render.settings(**l)

class RecordSupply:
    @require_login
    def GET(self):
        params = web.input(page=1, ed="")
        try:
            page = int(params.page)
        except: page = 1
        limit = SETTINGS['PAGE_LIMIT']
        start = (page -1) * limit if page > 0 else 0
        ed = params.ed
        suppliers = db.query("SELECT id, name FROM suppliers")
        materials = db.query("SELECT id, name, quality_rank FROM raw_materials")

        dic = lit(relations='supplies', fields="*",
                order="cdate desc ", limit=limit,offset=start)
        res = doquery(db,dic)
        count = countquery(db, dic)
        pagination_str = getPaginationString(default(page,0),count,limit,2,"/supplies","?page=")

        l = locals(); del l['self'];
        return render.record_supply(**l)
    def POST(self):
        params = web.input()

        l = locals(); del l['self'];
        return render.record_supply(**l)

class Logout:
    def GET(self):
        session.kill()
        return web.seeother("/")

if __name__ == "__main__":
      app.run()

#makes sure apache wsgi sees our app
application = web.application(urls, globals()).wsgifunc()
