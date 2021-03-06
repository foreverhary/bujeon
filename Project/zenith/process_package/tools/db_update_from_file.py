import os
from threading import Thread, Lock

from PySide2.QtCore import QObject, QTimer
from pymssql._pymssql import OperationalError

from process_package.resource.number import CHECK_DB_UPDATE_TIME, CHECK_DB_TIME
from process_package.tools.CommonFunction import logger
from process_package.resource.string import SAVE_DB_RETRY_FILE_NAME, SAVE_DB_FILE_NAME
from process_package.tools.mssql_connect import MSSQL
from process_package.tools.sqlite3_connect import select_pprh_not_update, update_pprh_tryup, update_pprh_up, \
    update_pprd_tryup, update_pprd_up, select_pprd_not_update


class UpdateDB(QObject):
    def __init__(self):
        super(UpdateDB, self).__init__()

        self.db_update_timer = QTimer(self)
        self.db_update_timer.timeout.connect(self.update_db)
        self.db_update_timer.start(CHECK_DB_UPDATE_TIME)

    def update_db(self):
        self.thread = Thread(target=self.update_thread, daemon=True)
        self.thread.start()

    def update_thread(self):
        mssql = MSSQL()
        mssql.get_mssql_conn()
        for query in select_pprh_not_update():
            logger.debug(query)
            try:
                mssql.insert_pprh(*query)
            except:
                update_pprh_tryup(query[0], query[2])
            else:
                update_pprh_up(query[0], query[2])
        for query in select_pprd_not_update():
            logger.debug(query)
            try:
                mssql.insert_pprd(*query)
            except Exception as e:
                logger.debug(f"{type(e)}:{e}")
                update_pprd_tryup(*query[:2])
            else:
                update_pprd_up(*query[:2])
#
# class UpdateDB(Thread):
#     def __init__(self):
#         super(UpdateDB, self).__init__()
#         self.query_lines = []
#         self.start()
#
#     def run(self):
#         mssql = MSSQL()
#         mssql.get_mssql_conn()
#         for query in select_pprh_not_update():
#             logger.debug(query)
#             try:
#                 mssql.insert_pprh(*query)
#             except:
#                 update_pprh_tryup(query[0], query[2])
#             else:
#                 update_pprh_up(query[0], query[2])
#         for query in select_pprd_not_update():
#             logger.debug(query)
#             try:
#                 mssql.insert_pprd(*query)
#             except Exception as e:
#                 logger.debug(f"{type(e)}:{e}")
#                 update_pprd_tryup(*query[:2])
#             else:
#                 update_pprd_up(*query[:2])
