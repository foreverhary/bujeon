import os
from threading import Thread

from process_package.defined_variable_function import SAVE_DB_FILE_NAME, logger, SAVE_DB_RETRY_FILE_NAME


class UpdateDB(Thread):
    def __init__(self, mssql):
        super(UpdateDB, self).__init__()
        self.query_lines = []
        self.mssql = mssql
        self.start()

    def run(self):
        logger.debug("run")
        self.read_file(SAVE_DB_RETRY_FILE_NAME)
        self.db_update()
        self.read_file(SAVE_DB_FILE_NAME)
        self.db_update()

    def db_update(self):
        for query_str in self.query_lines:
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
                logger.info(query_args)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")
                logger.error(query_args)
                with open(SAVE_DB_RETRY_FILE_NAME, 'a') as f:
                    query_args[-1] = str(int(query_args[-1]) + 1)
                    f.write('\t'.join(query_args) + '\n')
        self.query_lines = []

    def read_file(self, filename):
        logger.debug(filename)
        if os.path.isfile(filename) and self.mssql.con:
            with open(filename, 'r') as f:
                query_lines = f.readlines()
                logger.debug(query_lines)
                self.query_lines = list(map(lambda x: x.replace('\n', ''),query_lines))
            self.remove_file(filename)

    def remove_file(self, filename):
        logger.debug(filename)
        if os.path.isfile(filename):
            os.remove(filename)

