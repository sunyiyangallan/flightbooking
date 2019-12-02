from flask import Flask
from flask import render_template
from flask import redirect, request, session, url_for
from views.customer import cus_bp
from views.agent import ag_bp
from views.staff import stf_bp

from flask import Blueprint, render_template
from common.sql import db
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
import os
import numpy as np

app = Flask(__name__)
app.config.from_pyfile('config.py')     # 加载配置文件

# 蓝图注册
app.register_blueprint(cus_bp, url_prefix='/cus')    # 消费者
app.register_blueprint(stf_bp, url_prefix='/stf')    # 职员
app.register_blueprint(ag_bp, url_prefix='/ag')   # 代理


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flight', methods=['GET'])
def flight():

    cur = db.cursor()
    query_all = "SELECT * FROM flight where departure_time >= NOW() AND departure_time < NOW() + INTERVAL 1 MONTH"
    cur.execute(query_all, ())
    data = cur.fetchall()

    return render_template('/search_flight.html', comments=data)

@app.route('/search', methods=['GET', 'POST'])
def search():

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
        return render_template('search_flight.html', comments=data_default)

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
    return render_template('search_flight.html', comments=data)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)