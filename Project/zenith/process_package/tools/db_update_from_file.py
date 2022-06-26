import os
from threading import Thread, Lock

from pymssql._pymssql import OperationalError

from process_package.tools.CommonFunction import logger
from process_package.resource.string import SAVE_DB_RETRY_FILE_NAME, SAVE_DB_FILE_NAME
from process_package.tools.sqlite3_connect import select_pprh_not_update, update_pprh_tryup, update_pprh_up, \
    update_pprd_tryup, update_pprd_up, select_pprd_not_update


class UpdateDB(Thread):
    def __init__(self, mssql):
        super(UpdateDB, self).__init__()
        self.query_lines = []
        self.mssql = mssql
        self.start()

    def run(self):
        for query in select_pprh_not_update():
            logger.debug(query)
            try:
                self.mssql.insert_pprh(*query)
            except:
                update_pprh_tryup(query[0], query[2])
            else:
                update_pprh_up(query[0], query[2])
        for query in select_pprd_not_update():
            logger.debug(query)
            try:
                self.mssql.insert_pprd(*query)
            except:
                update_pprd_tryup(*query[:2])
            else:
                update_pprd_up(*query[:2])
        # self.read_file(SAVE_DB_RETRY_FILE_NAME)
        # self.db_update()
        # with Lock():
        #     self.read_file(SAVE_DB_FILE_NAME)
        # self.db_update()

    def db_update(self):
        for index, query_str in enumerate(self.query_lines):
            query_args = query_str.split('\t')
            if int(query_args[-1]) > 1000:
                continue
            if query_args[0] == "PPRH":
                func = self.mssql.insert_pprh
            elif query_args[0] == "PPRD":
                func = self.mssql.insert_pprd
            else:
                continue
            try:
                func(*query_args[1:-1])
            except OperationalError as e:
                logger.debug(type(e))
                with open(SAVE_DB_RETRY_FILE_NAME, 'a') as f:
                    for line in self.query_lines[index:]:
                        line_split = line.split('\t')
                        line_split[-1] = str(int(line_split[-1]) + 1)
                        f.write('\t'.join(line_split) + '\n')
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                logger.error(query_args)
                with open(SAVE_DB_RETRY_FILE_NAME, 'a') as f:
                    query_args[-1] = str(int(query_args[-1]) + 1)
                    f.write('\t'.join(query_args) + '\n')
        self.query_lines = []

    def read_file(self, filename):
        if os.path.isfile(filename) and self.mssql.con:
            with open(filename, 'r') as f:
                query_lines = f.readlines()
                self.query_lines = list(map(lambda x: x.replace('\n', ''), query_lines))
            self.remove_file(filename)

    def remove_file(self, filename):
        if os.path.isfile(filename):
            os.remove(filename)
