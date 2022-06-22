import configparser
import os

from process_package.resource.string import CONFIG_FILE_NAME, POP_SECTION, ORDER_NUMBER, MSSQL_SECTION, \
    AUDIO_BUS_SECTION, COMPORT_SECTION, MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE, GRADE_FILE_PATH, \
    SUMMARY_FILE_PATH, A_GRADE_MIN, A_GRADE_MAX, B_GRADE_MIN, B_GRADE_MAX, C_GRADE_MIN, C_GRADE_MAX, MIC_SECTION, \
    FILE_PATH


class Empty:
    pass


def get_value(value):
    try:
        eval_value = eval(value)
        if type(eval_value) in [int, float, list, tuple, dict]:
            return eval_value
    except NameError:
        pass
    except SyntaxError:
        pass
    return value


def get_config_value(config_filename, section, option):
    config = Config(config_filename)
    return config.get_value(section, option)


def set_config_value(config_filename, section, option, value):
    config = Config(config_filename)
    return config.set_value(section, option, value)


def get_order_number():
    return get_config_value(CONFIG_FILE_NAME, POP_SECTION, ORDER_NUMBER)


def set_order_number(value):
    set_config_value(CONFIG_FILE_NAME, POP_SECTION, ORDER_NUMBER, value)


def set_config_mssql(option, value):
    set_config_value(CONFIG_FILE_NAME, MSSQL_SECTION, option, value)


def get_config_mssql(option):
    return get_config_value(CONFIG_FILE_NAME, MSSQL_SECTION, option)


def get_config_audio_bus(option):
    return get_config_value(CONFIG_FILE_NAME, AUDIO_BUS_SECTION, option)


def set_config_audio_bus(option, value):
    set_config_value(CONFIG_FILE_NAME, AUDIO_BUS_SECTION, option, value)


class Config:
    def __init__(self, config_filename='config.ini', debug=False):
        self.debug = debug
        self.filename = config_filename
        if not os.path.exists(self.filename):
            self.init_config()
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option
        self.read_value()

    def init_config(self):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option
        config.add_section(POP_SECTION)
        config[POP_SECTION][ORDER_NUMBER] = ''
        config.add_section(COMPORT_SECTION)

        config.add_section(MSSQL_SECTION)
        config[MSSQL_SECTION][MSSQL_IP] = '10.10.0.4'
        config[MSSQL_SECTION][MSSQL_PORT] = '1430'
        config[MSSQL_SECTION][MSSQL_ID] = 'POPDB'
        config[MSSQL_SECTION][MSSQL_PASSWORD] = 'bjpop6981'
        config[MSSQL_SECTION][MSSQL_DATABASE] = 'POP_LIV'

        config.add_section(MIC_SECTION)
        config[MIC_SECTION][FILE_PATH] = 'C:/TestData/BK9041'

        config.add_section(AUDIO_BUS_SECTION)
        config[AUDIO_BUS_SECTION][GRADE_FILE_PATH] = 'C:/Users/Admin/Desktop/BEM788/GRADE'
        config[AUDIO_BUS_SECTION][SUMMARY_FILE_PATH] = 'C:/Users/Admin/Desktop/BEM788'
        config[AUDIO_BUS_SECTION][A_GRADE_MIN] = '123'
        config[AUDIO_BUS_SECTION][A_GRADE_MAX] = '125'
        config[AUDIO_BUS_SECTION][B_GRADE_MIN] = '125.1'
        config[AUDIO_BUS_SECTION][B_GRADE_MAX] = '127'
        config[AUDIO_BUS_SECTION][C_GRADE_MIN] = '121'
        config[AUDIO_BUS_SECTION][C_GRADE_MAX] = '122.9'

        with open(self.filename, 'w') as configfile:
            config.write(configfile)

    def read_value(self):
        self.config.read(self.filename)

        for section in self.config.sections():
            if not hasattr(self, section):
                setattr(self, section, Empty())
            current_section = getattr(self, section)

            for option in self.config[section]:
                value = self.config.get(section, option)
                setattr(current_section, option, get_value(value))

    def get_value(self, section, option):
        self.config.read(self.filename)
        try:
            if type(return_value := get_value(self.config[section][option])) is int:
                return_value = str(return_value)
            return return_value
        except KeyError:
            self.set_value(section, option, '')
            return get_value(self.config[section][option])

    def set_value(self, section, option, value):
        self.config.read(self.filename)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = str(value)

        if not hasattr(self, section):
            setattr(self, section, Empty())
        current_section = getattr(self, section)
        setattr(current_section, option, value)
        self.save()

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
