
from flask import Blueprint, render_template
from flask import redirect, request, session, url_for
from common.sql import db
import matplotlib.pyplot as plt
import os
import numpy as np

import time
import datetime
import hashlib
import base64



stf_bp = Blueprint('staff', __name__)


@stf_bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template("/stf/register.html")
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	airline_name = request.form['airline_name']
	cur = db.cursor()
	query = 'SELECT * FROM airline_staff WHERE username = %s'
	cur.execute(query, (username,))
	data = cur.fetchall()
	raw = (password).encode('utf-8')
	crypt_password = hashlib.md5(raw).hexdigest()
	if data:
		error = 'the username is registered.'
		return render_template('stf/register.html', error=error)


	query = 'SELECT * FROM airline WHERE airline_name = %s'
	cur.execute(query, (airline_name))
	data2 = cur.fetchall()
	if not data2:    #to ensure that the airline name is in the airline table
		error = 'the airline is registered.'
		return render_template('stf/register.html', error=error)

	ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
	cur.execute(ins, (username,crypt_password , first_name, last_name, date_of_birth, airline_name))
	db.commit()
	return render_template('index.html')


@stf_bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template("/stf/login.html")

	if session.get('username'):
		return redirect('/stf')

	username = request.form['username']
	password = request.form['password']

	raw = (password).encode('utf-8')
	crypt_password = hashlib.md5(raw).hexdigest()

	cur = db.cursor()
	query = 'SELECT password FROM airline_staff WHERE username = %s'
	cur.execute(query,(username))
	data = cur.fetchone()
	if not data:
		error = "the username does not exist"
		return render_template('stf/login.html', error=error)

	if crypt_password != data['password']:
		error = "password not correct"
		return render_template('stf/login.html', error=error)

	session['username'] = username
	return redirect('/stf')

@stf_bp.route('/')
def stf_index():
    try:
        username = session.get('username')
        return render_template('stf/stf.html',username=username)
    except:
        error = "you don't login"
        return render_template('stf/stf.html', error=error)


@stf_bp.route('/logout')
def logout():
    try:
        session.pop('username')
    except:
        error = 'you are not logined in'
        return render_template('stf/logout.html', error=error)
    return render_template('stf/logout.html')



'''
@stf_bp.route('/flight', methods=['GET'])
def flight():

    username = session.get('username')
    if not username:
        return redirect('/stf/login')
    cur = db.cursor()
    query_all = "SELECT * FROM flight where departure_time >= NOW() AND departure_time < NOW() + INTERVAL 1 MONTH"
    cur.execute(query_all, ())
    data = cur.fetchall()

    return render_template('stf/flight.html', comments=data)


@stf_bp.route('/search', methods=['POST'])
def search():
    if not session.get('username'):
        return redirect('/stf/login')
    arrival = request.form['arrival']
    depart = request.form['depart']
    date = request.form['date']
    arrival_city = request.form['arrival_city']
    depart_city = request.form['depart_city']
    
    query = "SELECT * FROM flight, airport WHERE arrival_airport = %s OR departure_airport = %s OR arrival_time = %s"
    cur = db.cursor()
    cur.execute(query, (arrival, depart, date))
    data = cur.fetchall()

    return render_template('stf/flight.html', comments=data). '''


@stf_bp.route('/flight', methods=['GET'])
def flight():

    email = session.get('username')
    if not email:
        return redirect('/stf/login')
    cur = db.cursor()
    query_all = "SELECT * FROM flight where departure_time >= NOW() AND departure_time < NOW() + INTERVAL 1 MONTH"
    cur.execute(query_all, ())
    data = cur.fetchall()

    return render_template('stf/flight.html', comments=data)


@stf_bp.route('/search', methods=['POST'])
def search():

	email = session.get('username')
	if not email:
		return redirect('/stf/login')
		
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
		return render_template('/stf/flight.html', comments=data_default)

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
	return render_template('/stf/flight.html', comments=data)


@stf_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
	username = session.get('username')
	if not username:
		return redirect('/stf/login')
	if request.method == 'GET':
		return render_template("/stf/createFlight.html")
	airline_name = request.form['airline_name']
	flight_num = request.form['flight_num']
	departure_airport = request.form['departure_airport']
	departure_time = request.form['departure_time']
	arrival_airport = request.form['arrival_airport']
	arrival_time = request.form['arrival_time']
	price = request.form['price']
	status = request.form['status']
	airplane_id = request.form['airplane_id']

	cur = db.cursor()
	# check if the airline is the same as the staff's
	query = 'SELECT airline_name FROM airline_staff WHERE username = %s and airline_name = %s'
	cur.execute(query, (username,airline_name))
	data = cur.fetchall()
	if not data:
		error = 'you cant register for other airline'
		return render_template('stf/createFlight.html', error=error)

	# check if the ariline's flight already exists
	query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s'
	cur.execute(query, (airline_name,flight_num))
	data2 = cur.fetchall()
	if data2:    #data2 exists
		error = 'the airlines flight is registered.'
		return render_template('stf/createFlight.html', error=error)

	query = 'SELECT * FROM airport WHERE airport_name = %s'
	cur.execute(query, (arrival_airport))
	data3 = cur.fetchall()
	if not data3:    #arrival airport not exist
		error = 'the arrival airport does not exist.'
		return render_template('stf/createFlight.html', error=error)

	query = 'SELECT * FROM airport WHERE airport_name = %s'
	cur.execute(query, (departure_airport))
	data3 = cur.fetchall()
	if not data3:    #arrival airport not exist
		error = 'the departure airport does not exist.'
		return render_template('stf/createFlight.html', error=error)

	query = 'SELECT * FROM airplane WHERE airplane_id = %s'
	cur.execute(query, (airplane_id))
	data4 = cur.fetchall()
	if not data4:    #arrival airport not exist
		error = 'the airplane_id does not exist.'
		return render_template('stf/createFlight.html', error=error)

	# check status
	if status not in ["upcoming","delayed","in progress"]:
		error = 'status not correct'
		return render_template('stf/createFlight.html', error=error)

	ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cur.execute(ins, (airline_name,flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id))
	db.commit()
	return render_template('stf/stf.html',username=username)

@stf_bp.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():
	username = session.get('username')
	if not username:
		return redirect('/stf/login')
	if request.method == 'GET':
		return render_template("/stf/changeStatus.html")
	airline_name = request.form['airline_name']
	flight_num = request.form['flight_num']
	status = request.form['status']

	cur = db.cursor()
	# check if the airline is the same as the staff's
	query = 'SELECT airline_name FROM airline_staff WHERE username = %s and airline_name = %s'
	cur.execute(query, (username,airline_name))
	data = cur.fetchall()
	if not data:
		error = 'you cant register for other airline'
		return render_template('stf/changeStatus.html', error=error)

	# check if the ariline's flight does not exist
	query = 'SELECT * FROM flight WHERE airline_name = %s and flight_num = %s'
	cur.execute(query, (airline_name,flight_num))
	data2 = cur.fetchall()
	if not data2:    #data2 not exists
		error = 'the airlines flight does not exist.'
		return render_template('stf/changeStatus.html', error=error)

	if status not in ["upcoming","delayed","in progress"]:
		error = 'status not correct'
		return render_template('stf/createFlight.html', error=error)

	ins = 'UPDATE flight SET status = %s where airline_name = %s and flight_num = %s'
	cur.execute(ins, (status, airline_name,flight_num))
	db.commit()
	return render_template('stf/stf.html',username=username)






@stf_bp.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():
	username = session.get('username')
	if not username:
		return redirect('/stf/login')
	if request.method == 'GET':
		return render_template("/stf/addAirplane.html")
	airline_name = request.form['airline_name']
	airplane_id = request.form['airplane_id']
	seats = request.form['seats']
	
	cur = db.cursor()
	# check if the airline is the same as the staff's
	query = 'SELECT airline_name FROM airline_staff WHERE username = %s and airline_name = %s'
	cur.execute(query, (username,airline_name))
	data = cur.fetchall()
	if not data:
		error = 'you cant add airplane for other airline'
		return render_template('stf/addAirplane.html', error=error)

	# check if the ariline's flight already exists
	query = 'SELECT * FROM airplane WHERE airline_name = %s and airplane_id = %s'
	cur.execute(query, (airline_name,airplane_id))
	data2 = cur.fetchall()
	if data2:    #data2 exists
		error = 'the airplane_id already exists.'
		return render_template('stf/addAirplane.html', error=error)


	ins = 'INSERT INTO airplane VALUES(%s, %s, %s)'
	cur.execute(ins, (airline_name,airplane_id, seats))
	db.commit()
	return render_template('stf/stf.html',username=username)





@stf_bp.route('/viewAgent', methods=['GET'])
def viewAgent():
    if not session.get('username'):
        return redirect('/stf/login')
    '''month = request.form['month']
    year = request.form['year']
    commission = request.form['commission'] '''
    query = "SELECT booking_agent_id, count(*) AS count FROM purchases where booking_agent_id is not null GROUP BY booking_agent_id"
   
    cur = db.cursor()
    cur.execute(query,())
    data = cur.fetchall()

    return render_template('stf/viewAgent.html', comments=data)



@stf_bp.route('/searchAgent', methods=['POST'])
def searchAgent():
    if not session.get('username'):
        return redirect('/stf/login')
    month = request.form['month']
    year = request.form['year']
    commission = request.form['commission']
    #query = "SELECT booking_agent_id, count(*) AS count FROM purchases where booking_agent_id is not null GROUP BY booking_agent_id"
    #search for top 5 for last month
    
    if month: 
    	query = "SELECT booking_agent_id, count(*) AS count FROM purchases where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <=date(purchase_date) AND booking_agent_id is not null GROUP BY booking_agent_id ORDER BY count DESC LIMIT 5"
    
    if year:
    	query = "SELECT booking_agent_id, count(*) AS count FROM purchases where DATE_SUB(CURDATE(), INTERVAL 365 DAY) <=date(purchase_date) AND booking_agent_id is not null GROUP BY booking_agent_id ORDER BY count DESC LIMIT 5"

    if commission:
    	query = 'SELECT booking_agent_id, sum(price) as commission FROM purchases NATURAL JOIN ticket NATURAL JOIN flight where DATE_SUB(CURDATE(), INTERVAL 1 year) <= date(purchase_date) AND booking_agent_id is not null GROUP BY booking_agent_id ORDER BY commission DESC LIMIT 5'

    cur = db.cursor()
    cur.execute(query,())
    data = cur.fetchall()

    return render_template('stf/viewAgent.html', comments=data)



# not implement for the year, but for the overall record
@stf_bp.route('/viewCus', methods=['GET'])
def viewCus():
    if not session.get('username'):
        return redirect('/stf/login')
    '''month = request.form['month']
    year = request.form['year']
    commission = request.form['commission'] '''

    query = "SELECT T.customer_email, T.count FROM (SELECT customer_email,count(*) AS count from purchases GROUP BY customer_email)AS T where count = (SELECT max(count) from (SELECT customer_email,count(*) AS count from purchases GROUP BY customer_email)AS T2) GROUP BY customer_email "
    cur = db.cursor()
    cur.execute(query,())
    data = cur.fetchall()

    return render_template('stf/viewCus.html', comments=data)



@stf_bp.route('/searchCus', methods=['GET'])
def searchCus():
    """
    显示所有航班信息
    :return:
    """
    email = session.get('username')
    if not email:
        return redirect('/stf/login')
    cur = db.cursor()
    query_all = "SELECT customer_email, ticket._ticket_id, flight.airline_name, flight.flight_num, flight.departure_airport, flight.departure_time, flight.arrival_airport, flight.arrival_time, flight.price, flight.status, flight.airplane_id FROM flight natural join ticket natural join airline_staff, ticket where username = %s and ticket.ticket_id = purchases.ticket_id"
    cur.execute(query_all, email)
    data = cur.fetchall()

    return render_template('stf/flight.html', comments=data)


@stf_bp.route('/searchCustomer', methods=['POST'])
def searchCustomer():
    if not session.get('username'):
        return redirect('/stf/login')
    arrival = request.form['arrival']
    depart = request.form['depart']
    date = request.form['date']

    query = "SELECT * FROM flight WHERE arrival_airport = %s OR departure_airport = %s or arrival_time = %s"
    cur = db.cursor()
    cur.execute(query, (arrival, depart, date))
    data = cur.fetchall()

    return render_template('stf/flight.html', comments=data)


@stf_bp.route('/searchPur', methods=['GET'])
def searchPur():
	if not session.get('username'):
		return redirect('/stf/login')


	return render_template('stf/searchPur.html')


@stf_bp.route('/getPur', methods=['POST'])
def getPur():
	if not session.get('username'):
		return redirect('/stf/login')


	startyear = request.form['startyear']
	endyear = request.form['endyear']
	startmonth = request.form['startmonth']
	endmonth = request.form['endmonth']
	endday = request.form['endday']
	startday = request.form['startday']

	if startday and endday and startyear  and startmonth :
		query = "SELECT day(purchase_date) as dates ,count(*) as count from purchases where YEAR(purchase_date)=" + startyear +" AND MONTH(purchase_date)=" \
				+ startmonth + " AND DAY(purchase_date)>="+startday+" AND DAY(purchase_date)<="+endday+"  GROUP BY DAY(purchase_date) "
	elif startyear  and startmonth and endmonth:
		query = "SELECT MONTH(purchase_date) as dates ,count(*) as count from purchases where YEAR(purchase_date)=" + startyear + " AND MONTH(purchase_date)>="\
				+startmonth+" AND MONTH(purchase_date)<="+endmonth+" GROUP BY MONTH(purchase_date) "
	elif startyear and endyear:
		query = "SELECT YEAR(purchase_date)as dates ,count(*) as count from purchases where YEAR(purchase_date)>="+startyear+" AND YEAR(purchase_date)<="+endyear+" GROUP BY YEAR(purchase_date) "



	cur = db.cursor()
	cur.execute(query, ())
	data = cur.fetchall()

#生成条形图
	plt.cla()
	name_list = []
	num_list = []
	for d in data:
		name_list.append(d["dates"])
		num_list.append(d['count'])
	print(name_list)
	print(num_list)

	plt.bar(name_list,num_list,1,color='rgby')

	plt.xlabel('year or month ')
	plt.ylabel('times')

	plt.xticks(name_list)
	plt.yticks(np.arange(0, max(num_list), 1))


#储存图片
	basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
	imgdir = '/static/count.jpg'
	file_path = basedir + imgdir
	plt.savefig(file_path)



	return render_template('stf/searchPur.html', comments=data,r=time.time())


@stf_bp.route('/fCustomer', methods=['GET'])
def fCustomer():
    if not session.get('username'):
        return redirect('/stf/login')

    return render_template('stf/fCustomer.html')

@stf_bp.route('/top_destination', methods=['GET', 'POST'])
def top_destination():
	
	query_m = 'select T.airport_city from (select count(*) as count, airport_city from ticket, flight, airport where ticket.flight_num = flight.flight_num and flight.arrival_airport = airport.airport_name and DATE_SUB(CURDATE(), INTERVAL 3 month) <= date(arrival_time) group by airport_city order by count DESC) as T limit 3'
	
	query_y = 'select T.airport_city from (select count(*) as count, airport_city from ticket, flight, airport where ticket.flight_num = flight.flight_num and flight.arrival_airport = airport.airport_name and DATE_SUB(CURDATE(), INTERVAL 1 year) <= date(arrival_time) group by airport_city order by count DESC) as T limit 3'
	
	cur = db.cursor()
	cur.execute(query_m, ())
	data_m = cur.fetchall()
	cur.execute(query_y, ())
	data_y = cur.fetchall()
	comment = []
	
	comment.append(data_m)
	comment.append(data_y)
	
	print(data_m)
	print(data_y)
	db.commit()
	cur.close()
	return render_template('stf/top_destination.html', comment=comment)


@stf_bp.route('/getfCustomer', methods=['POST'])
def getfCustomer():
    if not session.get('username'):
        return redirect('/stf/login')

    username = session.get('username')
    email = request.form['email']


    query = "SELECT a.ticket_id as at,a.customer_email as ac,a.purchase_date as ap ,b.airline_name as ba,b.flight_num as bf,c.departure_airport as cda,c.departure_time as cdt,c.arrival_airport as caa,c.arrival_time as cat,c.price as cp,c.`status` as cs,c.airplane_id as cai ,d.username as du FROM purchases a LEFT JOIN ticket b ON a.ticket_id=b.ticket_id LEFT JOIN flight c ON b.flight_num=c.flight_num LEFT JOIN airline_staff d ON d.airline_name = b.airline_name where a.customer_email =%s and d.username=%s"
    cur = db.cursor()
    cur.execute(query, (email,username))
    data = cur.fetchall()

    return render_template('stf/fCustomer.html', comments=data)

@stf_bp.route('/pie', methods=['GET', 'POST'])
def pie():

	if not session.get('username'):
		return redirect('/stf/login')
	username = session.get('username')

	cur = db.cursor()
	
	que_1 = 'SELECT airline_name FROM airline_staff WHERE username = %s'
	cur.execute(que_1,(username))
	data_1 = cur.fetchone()

	airline_name = str(data_1['airline_name'])
	data_2 = []
	label=['direct sales', 'indirect sales']
	data_3 = []

	que_2 = "SELECT count(DISTINCT ticket_id) as total FROM purchases NATURAL JOIN ticket \
			WHERE booking_agent_id is NULL AND purchase_date >= DATE_ADD(CURDATE(), INTERVAL -1 MONTH) AND purchase_date <= CURDATE() and airline_name = %s"
	cur.execute(que_2, (airline_name))
	data = cur.fetchone()

	if data == None:
		data_2.append(0)
	else:
		data_2.append(data['total'])

	query = "SELECT count(DISTINCT ticket_id) as total FROM purchases NATURAL JOIN ticket WHERE booking_agent_id is not NULL AND purchase_date >= DATE_ADD(CURDATE(), INTERVAL -1 MONTH) AND purchase_date <= CURDATE() and airline_name = %s" 
	cur.execute(query, (airline_name))
	data = cur.fetchone()

	if data == None:
		data_2.append(0)
	else:
		data_2.append(data['total'])	
	
	query = "SELECT count(DISTINCT ticket_id) as total FROM purchases NATURAL JOIN ticket \
			WHERE booking_agent_id is NULL AND purchase_date >= DATE_ADD(CURDATE(), INTERVAL -1 YEAR) AND purchase_date <= CURDATE() and airline_name = %s"
	cur.execute(query, (airline_name))
	data = cur.fetchone()

	if data == None:
		data_3.append(0)
	else:
		data_3.append(data['total'])

	query = "SELECT count(DISTINCT ticket_id) as total FROM purchases NATURAL JOIN ticket \
			WHERE booking_agent_id is not NULL AND purchase_date >= DATE_ADD(CURDATE(), INTERVAL -1 YEAR) AND purchase_date <= CURDATE() and airline_name = %s"
	cur.execute(query, (airline_name))
	data = cur.fetchone()

	if data == None:
		data_3.append(0)
	else:
		data_3.append(data['total'])

	return render_template('stf/pie_chart.html', data_1=data_2, label_1=label, data_2=data_3, label_2=label)

