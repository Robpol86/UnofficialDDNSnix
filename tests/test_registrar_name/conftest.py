#!/usr/bin/env python2.6
import logging.config
import tempfile
import pytest
import libs
import registrar_name


@pytest.fixture(scope='session')
def log_file(request):
    f = tempfile.NamedTemporaryFile()
    with libs.LoggingSetup(True, f.name, False) as cm:
        logging.config.fileConfig(cm.config)
    request.addfinalizer(lambda: f.close())
    return f


# noinspection PyProtectedMember
@pytest.fixture()
def session(request):
    s = registrar_name.RegistrarName(dict(user="USER", passwd="PASSWD", domain="sub.example.com"))
    s._url_base = "http://127.0.0.1"
    s._url_get_current_ip = s._url_base + "/hello"
    s._url_authenticate = s._url_base + "/login"
    s._url_get_main_domain = s._url_base + "/domain/list"
    s._url_get_records_prefix = s._url_base + "/dns/list/"
    s._url_delete_record_prefix = s._url_base + "/dns/delete/"
    s._url_create_record_prefix = s._url_base + "/dns/create/"
    s._url_logout = s._url_base + "/logout"

    if 'test_get_records_decider' in request.module.__name__:
        s._main_domain = "example.com"
        s.current_ip = "127.0.0.1"
        s.create_record = lambda: logging.debug("New Record")
        s.delete_record = lambda record: logging.debug("Delete Record %s" % record)
    return s
