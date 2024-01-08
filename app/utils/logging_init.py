import logging
from logging import config as logging_config
import os
import yaml


def setup_logging(default_path='logging.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    | **@author:** Prathyush SP
    | Logging Setup
    """
    path = default_path
    env_path = os.getenv(env_key, None)
    if env_path:
        path = env_path
    if os.path.exists(path):
        with open(path, 'rt', encoding='utf8') as f:
            try:
                # config = yaml.safe_load(f.read())
                config = yaml.unsafe_load(f.read())
                logging_config.dictConfig(config)
                # coloredlogs.install()
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=default_level)
                # coloredlogs.install(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        # coloredlogs.install(level=default_level)
        print('Failed to load configuration file. Using default configs')

setup_logging(default_level=logging.DEBUG)

