import configparser
import os


class Empty:
    pass


def getValue(value):
    try:
        evalValue = eval(value)
        if type(evalValue) in [int, float, list, tuple, dict]:
            return evalValue
    except NameError:
        pass
    return value


class Config:
    def __init__(self, configFilename, debug=False):
        self.debug = debug
        self.filename = configFilename
        if not os.path.exists(self.filename):
            self.init_config()
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option
        self.read_value()

    def init_config(self):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option
        for index in range(1, 6):
            potKey = f"pot{index}"
            config.add_section(potKey)
            config[potKey]['on_off'] = 'on'
            config[potKey]['calibration'] = '0'
            config[potKey]['min'] = '100'
            config[potKey]['max'] = '900'
        with open(self.filename, 'w') as configfile:
            config.write(configfile)

    def read_value(self):
        self.config.read(self.filename)

        for section in self.config.sections():
            if self.debug:
                pass
            if not hasattr(self, section):
                setattr(self, section, Empty())
            current_section = getattr(self, section)

            for option in self.config[section]:
                value = self.config.get(section, option)
                setattr(current_section, option, getValue(value))

    def getValue(self, section, option):
        return getValue(self.config[section][option])

    def setValue(self, section, option, value):
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
