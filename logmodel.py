#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  1 15:50:32 2017

@author: tony
"""

import MySQLdb
import numpy as np
from scipy.optimize import leastsq
from sympy import *
import math


def getHcgValues(pid):
    # connect database
    conn = MySQLdb.connect(
        host = '52.51.228.36',
        port = 3306,
        #unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
        user = 'root',
        passwd = 'root@123',
        db = 'clinic_cms',
        charset = 'utf8'
        )

    cursor = conn.cursor()
    query_hcg = "SELECT week_num, hcg_value FROM hcg WHERE pid ="+str(pid)
    cursor.execute(query_hcg)

    # get hcg values and week numbers
    result = cursor.fetchall()

    # use list to store week number, hcg values and prediction
    week = []
    hcg = []
    for row in result:
        week.append(row[0])
        hcg.append(row[1])

    # use list to store week number, hcg prediction for prediction
    predict_week = []
    predict_hcg = []
    relative_error_list = []

    #参数A,k, c
    A_list = []
    k_list = []
    c_list = []

    ###################################################################
    # mathmatical modeling
    n = 4
    while n < cursor.rowcount:
        x = np.array(week[:n])
        y = np.array(hcg[:n])
        # ln(y)
        y_log = [math.log(item, math.e) for item in y]
        # log linear function which needs to be fit
        def func(p,x):
            k,a = p
            return -k*x+a
        # error
        def error(p,x,y):
            return func(p,x)-y
        p0=[10,4]
        Para = leastsq(error, p0, args=(x,y_log))
        k,a = Para[0]
        k_list.append(k)
        #print "k=",k

        A = math.exp(a)
        A_list.append(A)
        #print "A=",A
        c = Symbol("c")
        x_new = np.array(week[n-1:n+1])
        y_new = np.array(hcg[n-1:n+1])

        # c is constant in expontienal function
        def sum_func(x, A, k, c, y):
            return np.sum((A * np.exp(-k * x) + c - y)**2)

        df_value = diff(sum_func(x_new, A, k, c, y_new),c)
        c = solve(df_value, c)[0]
        c_list.append(c)
        #print "c=",c

        ######################
        # predict value based on k, A, c
        predict_val = A * math.exp(-k * week[n]) + c
        #print week[n], predict_val, "\n"

        # cal relative errors
        def error_cal(predict, real):
            return abs(predict - real)/real

        relative_error = error_cal(predict_val , hcg[n])

        predict_week.append(week[n])
        predict_hcg.append(predict_val)
        relative_error_list.append(relative_error)
        n+=1

    total = 0.0
    for error in relative_error_list:
        total += error
        avg_error = total / len(relative_error_list)


    next_week_val = A_list[-1] * math.exp(-(k_list[-1]) * (week[n-1]+1))+ c_list[-1]
    predict_week.append(week[n-1]+1)
    predict_hcg.append(next_week_val)

    cursor.close()
    conn.close()
    return predict_week, predict_hcg, avg_error
    

