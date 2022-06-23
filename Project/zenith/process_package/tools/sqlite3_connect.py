import sqlite3
from threading import Thread

from PySide2.QtCore import QObject, QTimer

from process_package.resource.number import CHECK_DB_UPDATE_TIME
from process_package.resource.string import STR_NULL

SQL_FILE = 'log/data.sqlite'


def sqlite_init():
    con = sqlite3.connect(SQL_FILE, check_same_thread=False)
    cur = con.cursor()

    try:
        cur.execute(
            "CREATE table PPRH(DM text, AUFNR text, ITIME text, UP integer, RETRY integer)"
        )
        cur.execute(
            "create table PPRD(DM text, ITIME text, RESULT text, PCODE text, ECODE text, UP integer, RETRY integer)"
        )
    except:
        pass


def get_cur():
    return sqlite3.connect(SQL_FILE, check_same_thread=False).cursor()


def insert(func, *args):
    if 'pprh' in func.__name__:
        insert_pprh(*args)
    elif 'pprd' in func.__name__:
        insert_pprd(*args)


def insert_pprh(dm, aufnr, itime):
    cur = get_cur()
    sql = f"""INSERT INTO PPRH VALUES('{dm}', '{aufnr}', '{itime}', 0, 0)"""
    cur.execute(sql)


def insert_pprd( dm, itime, result, pcode='', ecode=''):
    cur = get_cur()
    # sql = f"""INSERT INTO PPRD VALUES ('{dm}', '{itime}', '{result}', '{pcode or STR_NULL}', '{ecode or STR_NULL}', 0, 0"""
    cur.execute("insert into PPRD values (?, ?, ?, ?, ?, 0, 0)", (dm, itime, result, pcode or STR_NULL, ecode or STR_NULL))


def up(func, *args):
    if 'pprh' in func.__name__:
        update_pprh_up(args[0], args[2])
    elif 'pprd' in func.__name__:
        update_pprd_up(args[0], args[1])


def tryup(func, *args):
    if 'pprh' in func.__name__:
        update_pprh_tryup(args[0], args[2])
    elif 'pprd' in func.__name__:
        update_pprd_tryup(args[0], args[1])


def select_pprh_not_upload():
    cur = get_cur()
    return cur.execute("select DM, AUFNR, ITIME from PPRH where UP=0")


def select_pprd_not_upload():
    cur = get_cur()
    return cur.execute("select DM, ITIME, RESULT, PCODE, ECODE from PPRD where UP=0")


def update_pprh_up(dm, itime):
    cur = get_cur()
    cur.execute(f"update PPRH SET UP = 1 where DM='{dm}' and ITIME='{itime}'")


def update_pprd_up(dm, itime):
    cur = get_cur()
    cur.execute(f"update PPRD SET UP = 1 where DM='{dm}' and ITIME = '{itime}'")


def update_pprh_tryup(dm, itime):
    cur = get_cur()
    cur.execute(f"update PPRH SET RETRY = RETRY + 1 where DM='{dm}' and itime='{itime}'")


def update_pprd_tryup(dm, itime):
    cur = get_cur()
    cur.execute(f"update PPRH SET RETRY = RETRY + 1 where DM='{dm}' and itime='{itime}'")


class SQLite3Connect(QObject):
    def __init__(self, mssql):
        super(SQLite3Connect, self).__init__()
        self._mssql = mssql

        self.con = sqlite3.connect('log/data.sqlite')

        self.cur = self.con.cursor()
        try:
            self.cur.execute(
                "CREATE table PPRH(DM text, AUFNR text, ITIME text, UP integer, RETRY integer)"
            )
            self.cur.execute(
                "create table PPRD(DM text ITIME text, RESULT text, PCODE text, ECODE text, UP integer, RETRY integer)"
            )
        except:
            pass

        self.db_update_timer = QTimer(self)
        self.db_update_timer.start(CHECK_DB_UPDATE_TIME)
        self.db_update_timer.timeout.connect(self.update_db)

    def update_db(self):
        Thread(target=self.update_thread).start()

    def update_thread(self):
        for query in self.select_pprh_not_upload():
            try:
                self._mssql.insert_pprh(*query)
            except:
                self.tryup('pprh', query[0], query[2])
            else:
                self.up('pprh', query[0], query[2])

        for query in self.select_pprd_not_upload():
            try:
                self._mssql.insert_pprd(*query)
            except:
                self.tryup('pprd', query[0], query[2])
            else:
                self.up('pprd', query[0], query[2])

    def insert(self, func, *args):
        if 'pprh' in func.__name__:
            self.insert_pprh(*args)
        elif 'pprd' in func.__name__:
            self.insert_pprd(*args)

    def insert_pprh(self, dm, aufnr, itime):
        sql = f"INSERT INTO PPRH VALUES('{dm}', '{aufnr}', '{itime}', 0, 0)"
        self.cur.execute(sql)

    def insert_pprd(self, dm, itime, result, pcode, ecode):
        sql = f"INSERT INTO PPRD VALUES ('{dm}', '{itime}', '{result}', '{pcode}', '{ecode}', 0, 0"
        self.cur.execute(sql)

    def up(self, func, *args):
        if 'pprh' in func.__name__:
            self.update_pprh_up(args[0], args[2])
        elif 'pprd' in func.__name__:
            self.update_pprd_up(args[0], args[1])

    def tryup(self, func, *args):
        if 'pprh' in func.__name__:
            self.update_pprh_tryup(args[0], args[2])
        elif 'pprd' in func.__name__:
            self.update_pprd_tryup(args[0], args[1])

    def select_pprh_not_upload(self):
        return self.cur.execute("select DM, AUFNR, ITIME from PPRH where UP=0")

    def select_pprd_not_upload(self):
        return self.cur.execute("select DM, ITIME, RESULT, PCODE, ECODE from PPRD where UP=0")

    def update_pprh_up(self, dm, itime):
        self.cur.execute(f"update PPRH SET UP = 1 where DM={dm} and ITIME={itime}")

    def update_pprd_up(self, dm, itime):
        self.cur.execute(f"update PPRD SET UP = 1 where DM='{dm}' and ITIME = '{itime}'")

    def update_pprh_tryup(self, dm, itime):
        self.cur.execute(f"update PPRH SET RETRY = RETRY + 1 where DM='{dm}' and itime='{itime}'")

    def update_pprd_tryup(self, dm, itime):
        self.cur.execute(f"update PPRH SET RETRY = RETRY + 1 where DM='{dm}' and itime='{itime}'")
