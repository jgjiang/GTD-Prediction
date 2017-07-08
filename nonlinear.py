import MySQLdb
import numpy as np
from sympy import *
import math
from scipy.optimize import curve_fit

def getHcgValues2(pid):
    # connect database
    conn = MySQLdb.connect(
        host='52.51.228.36',
        port=3306,
        # unix_socket='/Applications/MAMP/tmp/mysql/mysql.sock',
        user='root',
        passwd='root@123',
        db='clinic_cms',
        charset='utf8'
    )

    cursor = conn.cursor()
    query_hcg = "SELECT week_num, hcg_value FROM hcg WHERE pid = "+str(pid)
    cursor.execute(query_hcg)

    # get hcg values and week numbers
    result = cursor.fetchall()

    # use list to store week number, hcg values and prediction
    week = []
    hcg = []
    for row in result:
        week.append(row[0])
        hcg.append(row[1])

    # use list to store week number, hcg prediction, and relative errors for prediction
    predict_week = []
    predict_hcg = []
    relative_error_list = []

    # 参数A,k, c
    A_list = []
    k_list = []
    c_list = []

    ###################################################################
    # mathmatical modeling
    try:
        n = 5
        while n < cursor.rowcount:
            x = np.array(week[1:n])
            y = np.array(hcg[1:n])


            # curve function needs to be fit
            def func(t, A, k, c):
                return A * np.exp(-k * t) + c

            # curve fit
            popt, pcov = curve_fit(func, x, y)

            A, k, c = popt
            A_list.append(A)
            k_list.append(k)
            c_list.append(c)

            ######################
            # predict value based on k, A, c
            predict_val = A * math.exp(-k * week[n]) + c
            # print week[n], predict_val, "\n"

            # cal relative errors
            def error_cal(predict, real):
                return abs(predict - real) / real

            relative_error = error_cal(predict_val, hcg[n])

            predict_week.append(week[n])
            predict_hcg.append(predict_val)
            relative_error_list.append(relative_error)
            n += 1

    except RuntimeError:
        error_msg = {"msg": "Optimal parameters not found"}
        print(error_msg)

    total = 0.0
    avg_error = 0.0
    for error in relative_error_list:
        total += error
        avg_error = total / len(relative_error_list)

    next_week_val = A_list[-1] * math.exp(-(k_list[-1]) * (week[n - 1] + 1)) + c_list[-1]
    predict_week.append(week[n - 1] + 1)
    predict_hcg.append(next_week_val)

    cursor.close()
    conn.close()

    return predict_week, predict_hcg, avg_error

