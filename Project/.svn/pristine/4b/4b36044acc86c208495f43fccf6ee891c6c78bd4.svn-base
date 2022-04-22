import PySimpleGUI as sg
# import pandas as pd
import pymssql
from defined_string import *
from random import randint, choice
from threading import Thread, Lock
from pymssql import _mssql
from pymssql import _pymssql
import uuid
import decimal
import os
import time
import sys

sg.theme('DarkTeal11')

conn = pymssql.connect(server=DB_IP_PORT,
                       user=DB_USER,
                       password=DB_PASSWORD,
                       database=DB_DATABASE,
                       autocommit=True)

lock = Lock()

model_list = ['B788_L', 'B788_R']
line_list = [i for i in range(10)]
confirm_list = ['ok', 'ng']
db_column = ["airleak", "mic1", "mic2", "integ", "audio"]
thread_count = 10


def make_frame(index):
    frame_layout = [[sg.T(f'{"MODEL" if not index else ""}', key=f'{index}_model', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"LINE" if not index else ""}', key=f'{index}_line', justification='center', font=('Helvetica', 15), size=(5, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"DM" if not index else ""}', key=f'{index}_dm', justification='center', font=('Helvetica', 15), size=(12, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"AIRLEAK" if not index else ""}', key=f'{index}_airleak', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"MIC1" if not index else ""}', key=f'{index}_mic1', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"MIC2" if not index else ""}', key=f'{index}_mic2', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"통합검사" if not index else ""}', key=f'{index}_integ', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"Audio Bus" if not index else ""}', key=f'{index}_audio', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None),
                     sg.T(f'{"Out OK" if not index else ""}', key=f'{index}_out', justification='center', font=('Helvetica', 15), size=(8, 1), relief=sg.RELIEF_RIDGE if index else None)]]
    return frame_layout


layout = [
    [
        [sg.Frame(f"", layout=make_frame(index))] for index in range(thread_count + 1)
    ],
    [sg.RButton("start", key="start", font=('Helvetica', 15), size=(8, 1)),
     sg.RButton("cancel", key="cancel", font=('Helvetica', 15), size=(8, 1))]
]

window = sg.Window("db test", layout)

thread = list()
dm_limit = 1000000


def select_query(sql):
    r_value = None
    lock.acquire()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        r_value = cur.fetchone()
    except Exception as e:
        print(e, sql)

        # os._exit()
    lock.release()
    # cur.execute(sql)
    return r_value


def insert_query(sql):
    lock.acquire()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e, sql)
    lock.release()
    # cur.execute(sql)
    # conn.commit()


def update_query(sql):
    lock.acquire()
    cur = conn.cursor()
    try:
        cur.execute(sql)
    except Exception as e:
        print(e, sql)
    lock.release()
    # cur.execute(sql)


def sleep_time():
    # time.sleep(0.1)
    pass


def start_function(index, dm=None):

    sequence_num = 0
    input_dm = dm

    while True:
        while sequence_num < 5:
            if input_dm:
                sql = f"SELECT MODEL, LINE, out from dbo.B788_out where DM = '{input_dm}'"
                result = select_query(sql)
            else:
                result = None

            if result:
                model, line, out = result
                if out == 'ok' and sequence_num == 0:
                    input_dm, *tmp = insert_new_dm_out(index)

            else:
                input_dm, model, line = insert_new_dm_out(index)

            pass_result = choice(confirm_list)
            sql = f"INSERT INTO dbo.B788_{db_column[sequence_num]} " \
                  f"(C_TIME, MODEL, DM, LINE, RESULT) values " \
                  f"(getdate(), '{model}', '{input_dm}', {line}, '{pass_result}')"
            insert_query(sql)
            sql = f"UPDATE dbo.B788_out " \
                  f"SET {db_column[sequence_num]}_time = getdate(), " \
                  f"{db_column[sequence_num]} = '{pass_result}' where DM = '{input_dm}'"
            update_query(sql)

            window[f'{index + 1}_{db_column[sequence_num]}'].update(pass_result,
                                                                    background_color="blue" if pass_result == "ok" else "red")
            # sleep_time

            if pass_result == 'ok' or randint(0, 10) > 7:
                sequence_num += 1

        sequence_num = last_confirm(index, input_dm)


def last_confirm(index, dm):
    # print(sys._getframe(0).f_code.co_name, index, dm)
    sql = f"SELECT airleak, mic1, mic2, integ, audio from dbo.B788_out where DM = '{dm}'"
    result = select_query(sql)
    r_value = 0
    if result:
        ok_ng = result
        all_pass = True

        for l in db_column:
            window[f'{index + 1}_{l}'].update("", background_color="#405559")
        for i, (column, pass_value) in enumerate(zip(db_column, ok_ng)):
            if pass_value == 'ok':
                window[f'{index + 1}_{column}'].update(pass_value, background_color="blue")
            else:
                window[f'{index + 1}_{column}'].update(pass_value, background_color="red")
                window[f'{index + 1}_out'].update(pass_value, background_color="red")
                sleep_time()
                all_pass = False
                break
        if all_pass:
            window[f'{index + 1}_out'].update("ok", background_color="blue")
            sleep_time()
            for l in db_column:
                window[f'{index + 1}_{l}'].update("", background_color="#405559")
            window[f'{index + 1}_out'].update("", background_color="#405559")
            sql = f"UPDATE dbo.B788_out " \
                  f"SET out_time = getdate(), " \
                  f"out = 'ok' where DM = '{dm}'"
            update_query(sql)
        else:
            window[f'{index + 1}_out'].update("", background_color="#405559")
            r_value = i

    return r_value


def insert_new_dm_out(index=None):
    lock.acquire()
    cur = conn.cursor()
    sql = "select top 1 DM from dbo.B788_out order by DM desc"
    cur.execute(sql)
    dm = cur.fetchone()
    if dm:
        input_dm = raise_dm(dm[0])
    else:
        input_dm = f"VA{1:07d}"
    model = choice(model_list)
    line = choice(line_list)
    cur = conn.cursor()
    sql = f"INSERT INTO dbo.B788_out (S_TIME, MODEL, DM, LINE) values (getdate(), '{model}', '{input_dm}', {line})"
    cur.execute(sql)
    conn.commit()
    lock.release()
    window[f'{index + 1}_model'].update(model)
    window[f'{index + 1}_line'].update(line)
    window[f'{index + 1}_dm'].update(input_dm)
    return input_dm, model, line


def raise_dm(dm):
    v, a, *tmp_dm = dm
    dm_num = int(''.join(tmp_dm))
    dm_num += 1
    if dm_num > dm_limit:
        stop_process()
    return f"VA{dm_num:07d}"


def start_process():
    # print(sys._getframe(0).f_code.co_name)
    global thread
    for index in range(thread_count):
        thread.append(Thread(target=start_function, args=(index,)))

    for th in thread:
        th.start()


def stop_process():
    global thread
    for th in thread:
        th.stop()


while True:
    event, values = window.read()
    if event is None:
        os._exit(1)
        break

    if event == 'start':
        start_process()
    elif event == 'cancel':
        stop_process()
window.close()
