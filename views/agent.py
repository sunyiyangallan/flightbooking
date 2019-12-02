from flask import Blueprint, render_template
from flask import redirect, request, session, url_for
from common.sql import db
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
import os
import numpy as np

import random
import time
import datetime
import hashlib
import base64

ag_bp = Blueprint('agent', __name__)

@ag_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('ag/register.html')

    email = request.form['email']
    password = request.form['password']
    booking_agent_id = request.form['booking_agent_id']
    cur = db.cursor()
    query = 'SELECT * FROM booking_agent WHERE email = %s'
    cur.execute(query, (email,))
    data = cur.fetchone()
    raw = (password).encode('utf-8')
    crypt_password = hashlib.md5(raw).hexdigest()
    print(crypt_password)

    if data:
        error = 'the email is registered.'
        return render_template('ag/register.html', error=error)
    ins = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
    cur.execute(ins, (email, crypt_password, booking_agent_id))
    db.commit()
    return render_template('index.html')


@ag_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('ag/login.html')

    if session.get('email'):
        return redirect('/ag')

    booking_agent_id = request.form['booking_agent_id']
    email = request.form['email']
    password = request.form['password']
    raw = (password).encode('utf-8')

    crypt_password = hashlib.md5(raw).hexdigest()
    print(crypt_password)
    query = 'SELECT password FROM booking_agent WHERE email = %s'
    cur = db.cursor()
    cur.execute(query, (email,))
    data = cur.fetchone()
    if not data:
        error = 'email dose not exist.'
        return render_template('ag/login.html', error=error)

    if crypt_password != data['password']:
        error = 'password error.'
        return render_template('ag/login.html', error=error)
    session['id'] = booking_agent_id
    return redirect('/ag')


@ag_bp.route('/')
def ag_index():
    try:
        id = session.get('id')
        return render_template('ag/ag.html', id=id)
    except:
        error = "you haven't login yet"
        return render_template('ag/ag.html', error=error)


@ag_bp.route('/home')
def home():

    id = session.get('id')
    if not id:
        return redirect('/ag/login')

    query = "SELECT ticket_id, purchase_date, customer_email FROM purchases WHERE booking_agent_id = %s"
    cur = db.cursor()
    cur.execute(query, (id,))
    pur_all = cur.fetchall()

    res_list = []
    for pur in pur_all:
        ticket_id = pur['ticket_id']
        purchase_data = pur['purchase_date']
        customer_email = pur['customer_email']
        query_air = "SELECT airline_name FROM ticket WHERE ticket_id = %s"
        cur.execute(query_air, (ticket_id, ))
        air = cur.fetchone()
        query_flt = "SELECT * FROM flight WHERE airline_name = %s"
        cur.execute(query_flt, (air['airline_name'], ))
        flt = cur.fetchone()
        res_list.append(
            {'ticket_id': ticket_id, 'airline_name': air['airline_name'], 'purchase_date': purchase_data,
             'customer_email': customer_email,
             'departure_airport': flt['departure_airport'], 'arrival_airport': flt['arrival_airport'],
             'arrival_time': flt['arrival_time'], 'price': flt['price'], 'status': flt['status']
             }
        )

    return render_template('ag/home.html', comments=res_list)


@ag_bp.route('/logout')
def logout():

    try:
        session.pop('id')
    except:
        error = 'you did not login.'
        return render_template('ag/logout.html', error=error)
    return render_template('ag/logout.html')


@ag_bp.route('/flight', methods=['GET'])
def flight():

    id = session.get('id')
    if not id:
        return redirect('/ag/login')
    cur = db.cursor()
    query_all = "SELECT * FROM flight where departure_time >= NOW() AND departure_time < NOW() + INTERVAL 1 MONTH"
    cur.execute(query_all, ())
    data = cur.fetchall()

    return render_template('ag/flight.html', comments=data)


@ag_bp.route('/search', methods=['POST'])
def search():
    if not session.get('id'):
        return redirect('/ag/login')

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
        return render_template('ag/flight.html', comments=data_default)

    if arrival_airport != '':
        que_0 += "AND flight.arrival_airport = '%s'"%(arrival_airport)

    if departure_airport != '':
        que_0 += "AND flight.departure_airport = '%s'"%(departure_airport)

    if arrival_city != '':
        que_0 += "AND arr.airport_city = '%s'"%(arrival_city)

    if departure_city != '':
        que_0 += "AND dep.airport_city = '%s'"%(departure_city)

    if date != '':
        que_0 += "AND DATE(flight.departure_time) = '%s'"%(date)
        
    cur.execute(que_0)
    data = cur.fetchall()
    db.commit()
    cur.close()
    return render_template('ag/flight.html', comments=data)

@ag_bp.route('/pre_buy/<airline_name>/<flight_num>', methods=['GET', 'POST'])
def pre_buy(airline_name, flight_num):

    try:
        session.get('id')
    except:
        return redirect('/login')

    cus_email = request.form['cus_email']
    session['cus_email'] = cus_email
    session['airline_name'] = airline_name
    session['flight_num'] = flight_num

    return render_template('ag/buy.html')

@ag_bp.route('/buy', methods=['GET', 'POST'])
def buy():

    id = session['id']
    
    airline_name = session['airline_name']
    flight_num = session['flight_num']
    cus_email = session['cus_email']

    query0 = 'SELECT * FROM customer WHERE email = %s'
    cur = db.cursor()
    cur.execute(query0, (cus_email, ))
    data0 = cur.fetchall()

    if not data0:
        error = 'customer not found'
        return render_template('ag/pre_buy.html', error=error)
    
    ticket_id = str(random.randint(100000, 1000000))

    ticket_ins = "INSERT INTO ticket VALUE (%s , %s , %s)"
    cur.execute(ticket_ins, (ticket_id, flight_num, airline_name))

    purchase_ins = "INSERT INTO purchases VALUE (%s, %s, %s , %s)"

    agent_id = id
    dt = datetime.datetime.now().strftime("%Y-%m-%d")
    cur.execute(purchase_ins, (ticket_id, cus_email, agent_id, dt))
    db.commit()
    cur.close()
    session.pop('airline_name')
    session.pop('flight_num')

    ticket_data = {'ticket_id': ticket_id, 'airline_name': airline_name, 'cus_email': cus_email, "purchase_date": dt}
    
    return render_template('ag/buy.html', comment=ticket_data)

@ag_bp.route('/getCom', methods=['GET','POST'])
def getCom():
	
    if not session.get('id'):
        return redirect('/ag/login')

    id = session['id']
    cur = db.cursor()
    try:
        start_date = str(request.form['start_date'])
        end_date = str(request.form['end_date'])
        if start_date>end_date:
            return render_template('commission_view.html', comment=['Date Error'])
        
        query = 'SELECT SUM(price)*0.1 AS tot_commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
    WHERE booking_agent_id=%s AND purchase_date>=%s AND purchase_date<=%s'
    
        cur.execute(query, (id, start_date, end_date))
        data = cur.fetchone()
        commission = data['tot_commission']
        if commission == None:
            commission = 0
            
        query = 'SELECT count(ticket_id) AS tot_ticket FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id=%s AND purchase_date>=%s AND purchase_date<=%s'
        cur.execute(query, (id, start_date, end_date))
        data = cur.fetchone()
        ticket = data['tot_ticket']
        result = ['Your total commission of this time period is %d'%(commission), 'Your total ticket sold of this time period is %d'%(ticket)]
        return render_template('commission_view.html', comment=result)

    except:
        start_date = (date.today()-timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()

        query = 'SELECT SUM(price)*0.1 AS tot_commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id=%s AND purchase_date>=%s AND purchase_date<=%s'
        cur.execute(query, (id, start_date, end_date))
        data = cur.fetchone()
        commission = data['tot_commission']
        if commission == None:
            commission = 0

        query = 'SELECT count(ticket_id) AS tot_ticket FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id=%s AND purchase_date>=%s AND purchase_date<=%s'
        cur.execute(query, (id, start_date, end_date))
        data = cur.fetchone()
        ticket = data['tot_ticket']
        if ticket!=0:
            commission = commission / ticket

        result = ['Your average commission per ticket of past 30 days is %.2f'%(commission), 'Your total ticket sold of past 30 days is %d'%(ticket)]
        
        return render_template('commission_view.html', comment=result)

@ag_bp.route('/bar', methods=['GET'])
def bar():

    if not session.get('id'):
        return redirect('/ag/login')
    id = session.get('id')

    end_date = date.today().isoformat()[:-3]+"-01"

    que_1 = "SELECT customer_email,COUNT(DISTINCT ticket_id) AS count FROM ticket NATURAL JOIN purchases WHERE booking_agent_id = %s \
            AND purchase_date >%s AND purchase_date < DATE_ADD(%s, INTERVAL 1 MONTH) GROUP BY customer_email ORDER BY count DESC "
    cur = db.cursor()

    year = date.today().year
    month = date.today().month
    start_month = month - 5
    if (start_month < 1):
        year = year - 1
        month = month + 12
    start_date = date(year,start_month,1).isoformat()
    cur.execute(que_1,(id, start_date, end_date))
    data_1 = cur.fetchall()[:5]

    pic_1 = []
    label_1 = []
    for i in range(len(data_1)):
        pic_1.append(data_1[i]['count'])
        label_1.append(data_1[i]['customer_email'])

    que_2 = "SELECT customer_email, SUM(price)*0.1 AS commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight WHERE booking_agent_id = %s AND purchase_date > %s AND purchase_date < DATE_ADD(%s, INTERVAL 1 MONTH) \
            GROUP BY customer_email ORDER BY commission DESC"
    cur.execute(que_2,(id, start_date, end_date))
    data_2 = cur.fetchall()[:5]

    pic_2 = []
    label_2 = []
    for i in range(len(data_2)):
        pic_2.append(data_2[i]['count'])
        label_2.append(data_2[i]['customer_email'])

    return render_template('ag/bar_chart.html',pic_1 = pic_1, pic_2 = pic_2, label_1 = label_1, label_2 = label_2)


