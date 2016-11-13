"""Logging configuration routines."""

import logging
import logging.config
import os


def configure_logging_relative(logging_ini):
    """Configure logging from a relative file."""

    base_dir = os.path.dirname(__file__)
    logging_ini = os.path.join(base_dir, logging_ini)

    configure_logging(logging_ini)


def configure_logging(logging_ini):
    """Configure logging from a file."""

    logging.config.fileConfig(logging_ini)

    logging.info("logging configured using '%s'.", logging_ini)
