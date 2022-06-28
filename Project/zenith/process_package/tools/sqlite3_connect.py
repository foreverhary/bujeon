import sqlite3

from process_package.resource.string import STR_NULL

SQL_FILE = 'log/data.sqlite'


def deco_sqlite3(func):
    def wrapper(*args, **kwargs):
        con = sqlite3.connect(SQL_FILE, check_same_thread=False, isolation_level=None)
        cur = con.cursor()
        value = func(cur, *args, **kwargs)
        con.close()
        return value

    return wrapper


@deco_sqlite3
def sqlite_init(cur):
    try:
        cur.execute(
            "CREATE table PPRH(DM text, AUFNR text, ITIME text, UP integer, RETRY integer)"
        )
        cur.execute(
            "create table PPRD(DM text, ITIME text, RESULT text, PCODE text, ECODE text, IP text, UP integer, RETRY integer)"
        )
    except:
        pass


def insert(func, *args):
    if 'pprh' in func.__name__:
        insert_pprh(*args)
    elif 'pprd' in func.__name__:
        insert_pprd(*args)


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


@deco_sqlite3
def insert_pprh(cur, dm, aufnr, itime):
    cur.execute("INSERT INTO PPRH VALUES(?, ?, ?, 0, 0)", (dm, aufnr, itime))


@deco_sqlite3
def insert_pprd(cur, dm, itime, result, pcode='', ecode='', ip=''):
    cur.execute("insert into PPRD values (?, ?, ?, ?, ?, ?, 0, 0)",
                (dm, itime, result, pcode or STR_NULL, ecode or STR_NULL, ip))


@deco_sqlite3
def select_pprh_not_update(cur):
    cur.execute("select DM, AUFNR, ITIME from PPRH where UP=0")
    return cur.fetchall()


@deco_sqlite3
def select_pprd_not_update(cur):
    cur.execute("select DM, ITIME, RESULT, PCODE, ECODE, IP from PPRD where UP=0")
    return cur.fetchall()


@deco_sqlite3
def update_pprh_up(cur, dm, itime):
    cur.execute(f"update PPRH SET UP = 1 where DM='{dm}' and ITIME='{itime}'")


@deco_sqlite3
def update_pprd_up(cur, dm, itime):
    cur.execute(f"update PPRD SET UP = 1 where DM='{dm}' and ITIME = '{itime}'")


@deco_sqlite3
def update_pprh_tryup(cur, dm, itime):
    cur.execute(f"update PPRH SET RETRY = RETRY + 1 where DM='{dm}' and ITIME='{itime}'")


@deco_sqlite3
def update_pprd_tryup(cur, dm, itime):
    cur.execute(f"update PPRD SET RETRY = RETRY + 1 where DM='{dm}' and ITIME='{itime}'")
