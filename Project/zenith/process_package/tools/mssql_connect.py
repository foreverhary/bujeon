import os
from threading import Thread

import pymssql
from PySide2.QtCore import QObject, Signal, QTimer
from pymssql._pymssql import OperationalError, InterfaceError, IntegrityError
# mssql server
from process_package.Views.CustomComponent import get_time
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_mssql
from process_package.tools.db_update_from_file import UpdateDB
from process_package.resource.number import CHECK_DB_TIME, CHECK_DB_UPDATE_TIME
from process_package.resource.string import STR_NULL, MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE


class MSSQL(QObject):
    connection_status_changed = Signal(bool)
    pre_process_result_signal = Signal(str)
    order_list_changed = Signal(list)

    def __init__(self, keyword=''):
        super(MSSQL, self).__init__()
        self.keyword = keyword
        self._con, self.cur = None, None
        self.aufnr = ''
        self.aplzl = ''

    @property
    def con(self):
        return self._con

    @con.setter
    def con(self, value):
        self._con = value
        self.connection_status_changed.emit(bool(self._con))

    def set_aplzl(self):
        cur = self.con.cursor()
        if self.aufnr and self.keyword:
            sql = f"""
                    SELECT 
                        APLZL 
                    FROM 
                        AUFK 
                    WHERE 
                        AUFNR = {self.aufnr} and 
                        LTXA1 LIKE '%{self.keyword}%'
                """
            cur.execute(sql)
            logger.debug(sql)
            if fetch := cur.fetchone():
                self.aplzl = fetch[0]

    def set_aufnr_with_dm(self, dm):
        cur = self.con.cursor()
        sql = f"SELECT AUFNR FROM PPRH WHERE DM = '{dm}'"
        cur.execute(sql)
        if fetch := cur.fetchone():
            if fetch[0] != self.aufnr:
                self.aufnr = fetch[0]
            return True
        logger.debug(fetch)

    def insert_pprd(self, dm, itime, result=None, pcode='', ecode=''):
        if not self.set_aufnr_with_dm(dm):
            raise TypeError
        self.set_aplzl()
        cur = self.con.cursor()
        sql = f"""
            INSERT INTO PPRD 
            (
                DM, 
                AUFNR, 
                APLZL, 
                ITIME, 
                RESULT, 
                PCODE, 
                ECODE
            )
            values
            (
                '{dm}', 
                '{self.aufnr}', 
                '{self.aplzl}', 
                '{itime}', 
                '{result}', 
                '{pcode or STR_NULL}', 
                '{ecode or STR_NULL}')
            """
        logger.debug(sql)
        cur.execute(sql)
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

    def select_aplzl_with_order_keyword(self):
        sql = f"select APLZL from AUFK where AUFNR = '{self.aufnr}' and LTXA1 like '%{self.keyword}%'"
        logger.debug(sql)
        cur = self.con.cursor()
        cur.execute(sql)
        if fetch := self.cur.fetchone():
            return fetch[0]

    def select_result_with_dm_keyword(self, dm, keyword):
        sql = f"""
            select top 1 C.RESULT from PPRH as A
            left join AUFK as B on A.AUFNR = B.AUFNR
            left join PPRD as C on A.DM = C.DM and B.APLZL = C.APLZL
            where A.DM = '{dm}' and B.LTXA1 like '%{keyword}%' order by C.ITIME desc
        """
        logger.debug(sql)
        cur = self.con.cursor()
        cur.execute(sql)
        if fetch := cur.fetchone():
            self.pre_process_result_signal.emit(fetch[0])
        else:
            self.pre_process_result_signal.emit('')

    def get_mssql_conn(self):  # sourcery skip: use-fstring-for-concatenation
        self.con = pymssql.connect(server=get_config_mssql(MSSQL_IP) + f":{get_config_mssql(MSSQL_PORT)}",
                                   user=get_config_mssql(MSSQL_ID),
                                   password=get_config_mssql(MSSQL_PASSWORD),
                                   database=get_config_mssql(MSSQL_DATABASE),
                                   autocommit=True,
                                   login_timeout=3,
                                   timeout=3)
        self.cur = self.con.cursor()

    def get_time(self):
        sql = "SELECT GETDATE()"
        self.cur.execute(sql)

    def start_query_thread(self, *args):
        Thread(target=self.start_sql_func, args=(*args,), daemon=True).start()

    def start_sql_func(self, *args):
        self(*args)

    def check_connect_db(self):
        if self.con:
            self.start_query_thread(self.get_time)
        else:
            self.start_query_thread(self.get_mssql_conn)

    def update_db(self):
        self.update_instance = UpdateDB(self)

    def timer_for_db_connect(self):
        self.db_connect_timer = QTimer(self)
        self.db_connect_timer.start(CHECK_DB_TIME)
        self.db_connect_timer.timeout.connect(self.check_connect_db)

        self.db_update_timer = QTimer(self)
        self.db_update_timer.start(CHECK_DB_UPDATE_TIME)
        self.db_update_timer.timeout.connect(self.update_db)

    def __call__(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (OperationalError,
                IntegrityError,
                InterfaceError,
                TypeError,
                AttributeError) as e:
            logger.error(f"{type(e)} : {e}")
            if "insert" in func.__name__:
                logger.error(f"{func.__name__} Need to Save!!")
                self.save_query_db_fail(func, *args)
            return False
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            logger.error(f"{func.__name__} To Do error proces")

    def save_query_db_fail(self, func, *args):
        if "pprh" in func.__name__:
            table = "PPRH"
        if "pprd" in func.__name__:
            table = "PPRD"

        if not os.path.isdir('./log'):
            os.mkdir('log')
        with open("./log/save_db.log", 'a') as f:
            merge_args = [table] + list(args) + ['0\n']
            f.write("\t".join(merge_args))

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


def get_mssql_conn():
    return pymssql.connect(
        server=get_config_mssql(MSSQL_IP) + f":{get_config_mssql(MSSQL_PORT)}",
        user=get_config_mssql(MSSQL_ID),
        password=get_config_mssql(MSSQL_PASSWORD),
        database=get_config_mssql(MSSQL_DATABASE),
        autocommit=True,
        login_timeout=0.5,
        timeout=3,
    )


def select_order_number_with_date_material_model(date,
                                                 order_keyword='',
                                                 material_keyword='',
                                                 model_keyword=''):
    conn = get_mssql_conn()
    cur = conn.cursor()
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
    cur.execute(sql)
    return cur.fetchall()


if __name__ == '__main__':
    mssql = MSSQL('touch')
    # print(mssql(mssql.select_order_with_dm, 'AA1100001'))
    print(mssql(mssql.insert_pprd, get_time(), 'AQ1100001', 'OK'))
