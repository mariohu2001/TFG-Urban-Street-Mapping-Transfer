from configparser import ConfigParser
from typing import Tuple, List
import os


CONFIG_FOLDER: str = os.path.join(os.path.dirname(__file__), '..','..', 'config')
CONFIG_FILE = "config.ini"
config: ConfigParser = ConfigParser()

config.read(CONFIG_FOLDER+"/"+CONFIG_FILE)


def get_conf_values(section_key: str) -> Tuple[str]:

    return tuple(config[section_key].values())


def get_conf_key_value(section_key: str, conf_key: str) -> str:
    return config.get(section_key, conf_key)
