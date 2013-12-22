#!/usr/bin/env python2.6
"""Base class for all registrars in UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""


import logging


class RegistrarBase(object):
    def __init__(self, config):
        self.config = config
        self.current_ip = None
        self.recorded_ip = None

    def __enter__(self):
        return self  # TODO open network connection, then return self.

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # TODO close connection

    class RegistrarException(Exception):
        """Exception to be raised inside RegistrarBase and its derivatives when a handled error occurs."""
        pass

    def get_current_ip(self):
        logger = logging.getLogger('%s.get_current_ip' % self.__class__.__name__)
        logger.debug("Method get_current_ip start.")

    def authenticate(self):
        logger = logging.getLogger('%s.authenticate' % self.__class__.__name__)
        logger.debug("Method authenticate start.")

    def validate_domain(self):
        logger = logging.getLogger('%s.validate_domain' % self.__class__.__name__)
        logger.debug("Method validate_domain start.")

    def get_records(self):
        logger = logging.getLogger('%s.get_records' % self.__class__.__name__)
        logger.debug("Method get_records start.")

    def update_record(self):
        logger = logging.getLogger('%s.update_record' % self.__class__.__name__)
        logger.debug("Method update_record start.")

    def logout(self):
        logger = logging.getLogger('%s.logout' % self.__class__.__name__)
        logger.debug("Method logout start.")
