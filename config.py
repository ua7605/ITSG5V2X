import sys

import toml


class TomlReader(object):

    @staticmethod
    def configuration_toml(config: str):
        try:
            with open(config) as file:
                configuration_file = toml.load(f=file)
                return configuration_file
        except:
            print("File doesn't exists: " + config)
            sys.exit(0)
