
import logging
import logging.config
import os

def configure_logging_relative(logging_ini):
    base_dir = os.path.dirname(__file__)
    logging_ini = os.path.join(base_dir, logging_ini)

    configure_logging(logging_ini)

def configure_logging(logging_ini):
    logging.config.fileConfig(logging_ini)

    logging.info("logging configured using '{0}'.".format(logging_ini))
