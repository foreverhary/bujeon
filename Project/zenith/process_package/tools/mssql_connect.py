from threading import Thread

import pymssql
from PySide2.QtCore import QObject, Signal
from pymssql._pymssql import OperationalError, InterfaceError, IntegrityError

# mssql server
from process_package.component.CustomComponent import get_time
from process_package.resource.string import STR_NULL, MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_mssql
from process_package.tools.sqlite3_connect import sqlite_init, insert, up, insert_group, up_gruop


class MSSQL(QObject):
    connection_status_changed = Signal(bool)
    pre_process_result_signal = Signal(str)
    order_list_changed = Signal(list)
    data_matrix_with_air_touch_result_signal = Signal(list)

    def __init__(self, keyword=''):
        super(MSSQL, self).__init__()
        self.keyword = keyword
        self._con, self.cur = None, None
        self.aufnr = ''
        self.aplzl = ''
        sqlite_init()

    @property
    def con(self):
        return self._con

    @con.setter
    def con(self, value):
        self._con = value
        self.connection_status_changed.emit(bool(self._con))

    def select_pprd(self, dm, itime):
        cur = self.con.cursor()
        sql = f"select DM, ITIME from PPRD where DM = '{dm}' and ITIME = '{itime}'"
        logger.debug(sql)
        cur.execute(sql)
        return cur.fetchone()

    def insert_pprd_with_data_matrixs(self, dms, itime, result=None, pcode='', ecode='', ip=''):
        cur = self.con.cursor()
        sql = "INSERT INTO PPRD (DM, ITIME, RESULT, PCODE, ECODE, IP) VALUES "
        for dm in dms:
            sql += f"('{dm}','{itime}','{result}','{pcode or STR_NULL}','{ecode or STR_NULL}','{ip}'),"
        sql = sql[:-1]
        logger.debug(sql)
        cur.execute(sql)
        self.con.commit()
        return True

    def insert_pprd(self, dm, itime, result=None, pcode='', ecode='', ip=''):
        cur = self.con.cursor()
        sql = f"""
            INSERT INTO PPRD 
            (
                DM, 
                ITIME, 
                RESULT, 
                PCODE, 
                ECODE,
                IP
            )
            values
            (
                '{dm}', 
                '{itime}', 
                '{result}', 
                '{pcode or STR_NULL}', 
                '{ecode or STR_NULL}',
                '{ip}')
            """
        logger.debug(sql)
        cur.execute(sql)
        logger.debug('after execute')
        self.con.commit()
        return True

    def insert_pprh(self, dm, order, itime):
        sql = f"""
            IF EXISTS(
                SELECT DM from PPRH
                where DM = '{dm}'
            )
                BEGIN
                select 99 cnt
                END
            ELSE
                BEGIN
                INSERT INTO PPRH (DM, AUFNR, ITIME)
                VALUES ('{dm}', '{order}', '{itime}')
                END
            """
        logger.debug(sql)
        cur = self.con.cursor()
        cur.execute(sql)
        self.con.commit()
        return True

    def get_mssql_conn(self):
        self.con = pymssql.connect(server=f"{get_config_mssql(MSSQL_IP)}:{get_config_mssql(MSSQL_PORT)}",
                                   user=get_config_mssql(MSSQL_ID),
                                   password=get_config_mssql(MSSQL_PASSWORD),
                                   database=get_config_mssql(MSSQL_DATABASE),
                                   autocommit=True,
                                   login_timeout=3,
                                   timeout=3)
        self.cur = self.con.cursor()

    def get_time(self):
        sql = "SELECT GETDATE()"
        logger.debug(sql)
        self.cur.execute(sql)

    def start_query_thread(self, *args):
        Thread(target=self.start_sql_func, args=(*args,), daemon=True).start()

    def start_sql_func(self, *args):
        if "insert_pprd_with_data_matrixs" in args[0].__name__:
            insert_group(*args)
        elif "insert" in args[0].__name__:
            insert(*args)
        self(*args)

    def __call__(self, func, *args, **kwargs):
        try:
            self.get_mssql_conn()
            return_value = func(*args, **kwargs)
        except (OperationalError,
                IntegrityError,
                InterfaceError,
                TypeError,
                AttributeError) as e:
            logger.error(f"{type(e)} : {e}")
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            logger.error(f"{func.__name__} To Do error proces")
        else:
            if "insert_pprd_with_data_matrixs" in func.__name__:
                up_gruop(args[0], args[1])
            elif 'insert' in func.__name__:
                up(func, *args)
            self.con.close()
            return return_value

    def select_order_number_with_date_material_model(self,
                                                     date,
                                                     order_keyword='',
                                                     material_keyword='',
                                                     model_keyword=''):

        sql = f"""
            select A.AUFNR as order_number,
                    C.MATNR as material_code, C.MAKTX as model_name 
            from AFKO as A 
            left join MATE as C on A.MATNR = C.MATNR
            where A.GSTRP = '{date}'
            and A.AUFNR like '%{order_keyword}%'
            and C.MATNR like '%{material_keyword}%' 
            and C.MAKTX like '%{model_keyword}%' 
            order by A.AUFNR
        """

        self.cur.execute(sql)
        self.order_list_changed.emit(self.cur.fetchall())

    def select_pprd_with_data_matrix(self, dm):
        self.cur.execute(f"select DM, ITIME, RESULT, PCODE, ECODE, IP from PPRD where DM = '{dm}' order by ITIME desc")
        return self.cur.fetchall()

    def select_pprd_with_data_matrix_and_air_touch(self, dm):
        self.cur.execute(
            f"select DM, ITIME, RESULT, PCODE, ECODE, IP "
            f"from PPRD "
            f"where DM = '{dm}' and (PCODE = 'AIR' or PCODE = 'TOUCH')"
            f"order by PCODE asc, ITIME desc")
        self.data_matrix_with_air_touch_result_signal.emit(self.cur.fetchall())


if __name__ == '__main__':
    mssql = MSSQL('touch')
    # print(mssql(mssql.select_order_with_dm, 'AA1100001'))
    print(mssql(mssql.insert_pprd, get_time(), 'AQ1100001', 'OK'))
