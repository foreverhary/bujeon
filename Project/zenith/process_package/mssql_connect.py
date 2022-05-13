import pandas as pd
import pymssql
from pymssql import _mssql, _pymssql, ProgrammingError
import uuid
import decimal

# mssql server
from process_package.Config import get_config_mssql
from process_package.defined_variable_function import MSSQL_IP, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE, MSSQL_PORT, \
    logger, NULL


def get_mssql_conn():
    conn = pymssql.connect(server=get_config_mssql(MSSQL_IP) + f":{get_config_mssql(MSSQL_PORT)}",
                           user=get_config_mssql(MSSQL_ID),
                           password=get_config_mssql(MSSQL_PASSWORD),
                           database=get_config_mssql(MSSQL_DATABASE),
                           autocommit=True,
                           login_timeout=1,
                           timeout=1)
    return conn, conn.cursor()


def select_order_process_with_dm(dm, keyword):
    conn, cursor = get_mssql_conn()
    sql = f"SELECT A.AUFNR, B.APLZL " \
          f"FROM PPRH as A " \
          f"LEFT JOIN AUFK as B on A.AUFNR = B.AUFNR " \
          f"WHERE DM = '{dm}' and LTXA1 like '%{keyword}%'"
    cursor.execute(sql)
    return cursor.fetchone()


def insert_pprd(dm=None, result=None, keyword=None, pcode='', ecode=''):
    aufnr, aplzl = select_order_process_with_dm(dm, keyword)
    conn, cursor = get_mssql_conn()
    sql = f"INSERT INTO PPRD (DM, AUFNR, APLZL, ITIME, RESULT, PCODE, ECODE) " \
          f"values('{dm}', '{aufnr}', '{aplzl}', GETDATE(), '{result}', '{pcode or NULL}', '{ecode or NULL}')"
    cursor.execute(sql)
    conn.commit()


def insert_pprh(*args):
    order, dm = args
    try:
        conn, cursor = get_mssql_conn()
        cursor.execute(f"""
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
                VALUES ('{dm}', '{order}', GETDATE())
                END
            """)
        conn.commit()
    except ProgrammingError as e:
        pass
    except Exception as e:
        logger.error(f"{type(e)}: {e}")


def select_touch_result_from_pprd(dm):
    conn, cursor = get_mssql_conn()
    sql = f"select * from PPRD where DM = {dm}"
    cursor.execute(sql)
    return cursor.f


def select_aplzl_with_order_keyword(order, keyword):
    conn, cursor = get_mssql_conn()
    sql = f"select APLZL from AUFK where AUFNR = '{order}' and LTXA1 like '%{keyword}%'"
    cursor.execute(sql)
    return cursor.fetchone()


def select_result_with_dm_keyword(dm, keyword):
    try:
        conn, cursor = get_mssql_conn()
        sql = f"""
            select top 1 C.RESULT from PPRH as A
            left join AUFK as B on A.AUFNR = B.AUFNR
            left join PPRD as C on A.DM = C.DM and B.APLZL = C.APLZL
            where A.DM = '{dm}' and B.LTXA1 like '%{keyword}%' order by C.ITIME desc
        """
        cursor.execute(sql)
        return cursor.fetchone()
    except pymssql._pymssql.OperationalError as e:
        pass
    except Exception as e:
        logger.error(f"{type(e)}:{e}")


def select_order_number_with_date_material_model(date,
                                                 order_keyword='',
                                                 material_keyword='',
                                                 model_keyword=''):
    conn, cursor = get_mssql_conn()
    sql = f"""
        select A.AUFNR as order_number, A.GSTRP as date, 
                B.APLZL as process_number, B.KTSCH as process_code, B.LTXA1 as process_name, 
                C.MATNR as material_code, C.MAKTX as model_name 
        from AFKO as A 
        left join AUFK as B on A.AUFNR = B.AUFNR 
        left join MATE as C on A.MATNR = C.MATNR
        where A.GSTRP = '{date}'
        and A.AUFNR like '%{order_keyword}%'
        and C.MATNR like '%{material_keyword}%' 
        and C.MAKTX like '%{model_keyword}%' 
        order by A.AUFNR
    """
    return pd.read_sql(sql, conn)


def get_process_error_code(process):
    conn, cursor = get_mssql_conn()
    sql = f"SELECT NGNU, NGNM FROM PNGC WHERE PCODE = '{process}'"
    return pd.read_sql(sql, conn)


def get_process_error_code_dict(process):
    return {row[1][1]: row[1][0] for row in get_process_error_code(process).iterrows()}


if __name__ == '__main__':
    insert_pprd(dm='AA1100001', result='NG', keyword='AUD', pcode='FUNCTION', ecode='1,2')
