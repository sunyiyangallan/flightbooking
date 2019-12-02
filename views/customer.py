
from flask import Blueprint, render_template
from flask import redirect, request, session, url_for
from common.sql import db
import random
import time
import datetime
import hashlib
import base64
import matplotlib.pyplot as plt
import os
import numpy as np


cus_bp = Blueprint('customer', __name__)


@cus_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    注册视图， 如果请求为get，返回注册表单，如果为post方法，进行注册操作。
    登录成功跳转首页。
    :return:
    """
    if request.method == 'GET':
        return render_template('cus/register.html')

    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    building_number = request.form['building_number']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_number = request.form['phone_number']
    passport_number = request.form['passport_number']
    passport_expiration = request.form['passport_expiration']
    passport_country = request.form['passport_country']
    date_of_birth = request.form['date_of_birth']
    cur = db.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cur.execute(query, (email,))
    data = cur.fetchall()
    raw = (password).encode('utf-8')
    crypt_password = hashlib.md5(raw).hexdigest()

    if data:
        error = 'the email is registered.'
        return render_template('cus/register.html', error=error)
    ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cur.execute(ins, (email, name,crypt_password , building_number, street, city, state, phone_number, passport_number,
                      passport_expiration, passport_country, date_of_birth))
    db.commit()
    return render_template('index.html')


@cus_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    登录视图, 请求为get方法， 返回登录表单，请求为post方法，进行登录操作，
    登录成功返回查看航班首页。
    :return:
    """
    if request.method == 'GET':
        return render_template('cus/login.html')

    if session.get('email'):
        return redirect('/cus')

   

    email = request.form['email']
    password = request.form['password']
    raw = (password).encode('utf-8')

    crypt_password = hashlib.md5(raw).hexdigest()
    query = 'SELECT password FROM customer WHERE email = %s'
    cur = db.cursor()
    cur.execute(query, (email,))
    data = cur.fetchone()
    if not data:
        error = 'email dose not exist.'
        return render_template('cus/login.html', error=error)

    if crypt_password != data['password']:
        error = 'password error.'
        return render_template('cus/login.html', error=error)
    session['email'] = email
    return redirect('/cus')


@cus_bp.route('/')
def cus_index():
    try:
        email = session.get('email')
        return render_template('cus/cus.html', email=email)
    except:
        error = "you don't login"
        return render_template('cus/cus.html', error=error)


@cus_bp.route('/home')
def home():
    """这页定义"""
    email = session.get('email')
    if not email:
        return redirect('/cus/login')

    query = "SELECT ticket_id, purchase_date FROM purchases WHERE customer_email = %s"
    cur = db.cursor()
    cur.execute(query, (email,))
    pur_all = cur.fetchall()

    res_list = []
    for pur in pur_all:
        ticket_id = pur['ticket_id']
        purchase_data = pur['purchase_date']
        query_air = "SELECT airline_name FROM ticket WHERE ticket_id = %s"
        cur.execute(query_air, (ticket_id, ))
        air = cur.fetchone()
        query_flt = "SELECT * FROM flight WHERE airline_name = %s"
        cur.execute(query_flt, (air['airline_name'], ))
        flt = cur.fetchone()
        res_list.append(
            {'ticket_id': ticket_id, 'airline_name': air['airline_name'], 'purchase_date': purchase_data,
             'departure_airport': flt['departure_airport'], 'arrival_airport': flt['arrival_airport'],
             'arrival_time': flt['arrival_time'], 'price': flt['price'], 'status': flt['status']
             }
        )

    return render_template('cus/home.html', comments=res_list)


@cus_bp.route('/logout')
def logout():
    """
    注销登录
    :return:
    """
    try:
        session.pop('email')
    except:
        error = 'you are not login.'
        return render_template('cus/logout.html', error=error)
    return render_template('cus/logout.html')


@cus_bp.route('/flight', methods=['GET'])
def flight():
    """
    显示所有航班信息
    :return:
    """
    email = session.get('email')
    if not email:
        return redirect('/cus/login')
    cur = db.cursor()
    query_all = "SELECT * FROM flight where departure_time >= NOW() AND departure_time < NOW() + INTERVAL 1 MONTH"
    cur.execute(query_all, ())
    data = cur.fetchall()

    return render_template('cus/flight.html', comments=data)


@cus_bp.route('/search', methods=['POST'])
def search():

    if not session.get('email'):
        return redirect('/cus/login')

    arrival_airport = request.form['arrival_airport']
    departure_airport = request.form['departure_airport']
    arrival_city = request.form['arrival_city']
    departure_city = request.form['departure_city']
    date = request.form['date']

    que_0  = "SELECT flight.airline_name as airline_name, flight.arrival_time as arrival_time, flight.status as status, flight.flight_num as flight_num, flight.departure_time as departure_time, dept.airport_name as departure_airport, dept.airport_city as departure_city, \
                arr.airport_name as arrival_airport, arr.airport_city as arrival_city, flight.airline_name as airline, flight.price as price, flight.airplane_id as airplane_id\
				FROM (flight, airport as dept, airport as arr) WHERE flight.departure_airport=dept.airport_name and flight.arrival_airport=arr.airport_name AND flight.status = 'upcoming'"
    cur = db.cursor()
    

    if arrival_airport == '' and departure_airport == '' and arrival_city == '' and departure_city == '' and date == '':
        cur.execute(que_0, ())
        data_default = cur.fetchall()
        return render_template('cus/flight.html', comments=data_default)

    if arrival_airport != '':
        que_0 += "AND flight.arrival_airport = '%s'"%(arrival_airport)

    if departure_airport != '':
        que_0 += "AND flight.departure_airport = '%s'"%(departure_airport)

    if arrival_city != '':
        que_0 += "AND arr.airport_city = '%s'"%(arrival_airport)

    if departure_city != '':
        que_0 += "AND dep.airport_city = '%s'"%(departure_airport)

    if date != '':
        que_0 += "AND DATE(flight.departure_time) = '%s'"%(date)
        
    cur.execute(que_0)
    data = cur.fetchall()
    db.commit()
    cur.close()
    return render_template('cus/flight.html', comments=data)


@cus_bp.route('/buy/<airline_name>', methods=['GET'])
def buy(airline_name):
    """
    买票视图函数定义
    :param airline_name:
    :return:
    """
    try:
        email = session.get('email')
    except:
        return redirect('/login')

    ticket_id = str(random.randint(100000, 1000000))
    query = "SELECT flight_num FROM flight WHERE airline_name = %s"
    cur = db.cursor()
    cur.execute(query, (airline_name, ))
    data = cur.fetchone()
    if not data:
        return render_template('cus/buy.html', error='have a error.')
    flight_num = data['flight_num']

    # 插入数据到ticket表
    ticket_ins = "INSERT INTO ticket VALUE (%s , %s , %s)"
    cur.execute(ticket_ins, (ticket_id, airline_name, flight_num))

    purchase_ins = "INSERT INTO purchases VALUE (%s, %s, %s , %s)"

    agent_id = None
    dt = datetime.datetime.now().strftime("%Y-%m-%d")
    cur.execute(purchase_ins, (ticket_id, email, agent_id, dt))
    cur.close()
    db.commit()
    data = {'ticket_id': ticket_id, 'airline_name': airline_name, "purchase_date": dt}

    return render_template("cus/buy.html", comment=data)


@cus_bp.route('/cusspend', methods=['GET'])
def cusspend():
    if not session.get('email'):
        return redirect('/cus/login')
    email = session.get('email')
    query = "SELECT MONTH(p.purchase_date) as dates,SUM(f.price) as count FROM purchases p LEFT JOIN ticket t ON p.ticket_id = t.ticket_id LEFT JOIN flight f ON t.flight_num = f.flight_num where  MONTH(p.purchase_date)>= MONTH(date_add(NOW(),INTERVAL '-5' MONTH)) AND MONTH(p.purchase_date)<= now() AND p.customer_email = %s GROUP BY MONTH(p.purchase_date) "
    cur = db.cursor()
    cur.execute(query, (email))
    data = cur.fetchall()

    # 生成条形图
    plt.cla()
    name_list = []
    num_list = []

    for d in data:
        name_list.append(d["dates"])
        num_list.append(float(d['count']))

    print(name_list)
    print(num_list)
    plt.bar(name_list, num_list, 1, color='rgby')

    plt.xlabel('year or month or day')
    plt.ylabel('spend')

    plt.xticks(name_list)
    plt.yticks(np.arange(0, max(num_list), 100))
    # 储存图片
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    imgdir = '/static/cusspend6.jpg'
    file_path = basedir + imgdir
    plt.savefig(file_path)

    return render_template('cus/cusspend.html',c = data,r=time.time())

@cus_bp.route('/getCusspend', methods=['POST'])
def getcusspend():
    if not session.get('email'):
        return redirect('/cus/login')
    email =session.get('email')
    startyear = request.form['startyear']
    endyear = request.form['endyear']
    startmonth = request.form['startmonth']
    endmonth = request.form['endmonth']
    endday = request.form['endday']
    startday = request.form['startday']

    if startday and endday and startyear and startmonth:
        query = "SELECT day (p.purchase_date) as dates,SUM(f.price) as count FROM purchases p LEFT JOIN ticket t ON p.ticket_id = t.ticket_id LEFT JOIN flight f ON t.flight_num = f.flight_num where YEAR(p.purchase_date)=" + startyear + " AND MONTH(p.purchase_date)=" \
                + startmonth + " AND DAY(p.purchase_date)>=" + startday + " AND DAY(p.purchase_date)<=" + endday + " AND p.customer_email = %s  GROUP BY DAY(ppurchase_date) "
    elif startyear and startmonth and endmonth:
        query = "SELECT MONTH(p.purchase_date) as dates,SUM(f.price) as count FROM purchases p LEFT JOIN ticket t ON p.ticket_id = t.ticket_id LEFT JOIN flight f ON t.flight_num = f.flight_num where YEAR(p.purchase_date)=" + startyear + " AND MONTH(p.purchase_date)>=" \
                + startmonth + " AND MONTH(p.purchase_date)<=" + endmonth + " AND p.customer_email = %s GROUP BY MONTH(p.purchase_date) "
    elif startyear and endyear:
        query = "SELECT YEAR(p.purchase_date) as dates,SUM(f.price) as count FROM purchases p LEFT JOIN ticket t ON p.ticket_id = t.ticket_id LEFT JOIN flight f ON t.flight_num = f.flight_num where YEAR(p.purchase_date)>=" + startyear + " AND YEAR(p.purchase_date)<=" + endyear + " AND p.customer_email = %s GROUP BY YEAR(p.purchase_date) "

    cur = db.cursor()
    cur.execute(query, (email))
    data = cur.fetchall()

    # 生成条形图
    plt.cla()
    name_list = []
    num_list = []

    for d in data:
        name_list.append(d["dates"])
        num_list.append(float(d['count']))

    print(name_list)
    print(num_list)
    plt.bar(name_list, num_list, 1, color='rgby')

    plt.xlabel('year or month or day')
    plt.ylabel('spend')

    plt.xticks(name_list)
    plt.yticks(np.arange(0, max(num_list), 100))
    # 储存图片
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    imgdir = '/static/cusspend.jpg'
    file_path = basedir + imgdir
    plt.savefig(file_path)

    return render_template('cus/cusspend.html', comments=data,r=time.time())

