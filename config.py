#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import os

# 数据库配置
DB_CONF = dict(
    host='localhost',
    user='root',
    password='',
    db='reservation system',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# 密钥
SECRET_KEY = os.urandom(32)


DEBUG = True







