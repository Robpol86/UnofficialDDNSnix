#!/usr/bin/env python2.6
"""Name.com class for UnofficialDDNSnix.
https://github.com/Robpol86/UnofficialDDNSnix
"""


from registrar_base import RegistrarBase


class RegistrarName(RegistrarBase):
    _url_base = "https://api.name.com/api"
    _url_get_current_ip = _url_base + "/hello"
    _url_authenticate = _url_base + "/login"
    _url_get_main_domain = _url_base + "/domain/list"
    _url_get_records_prefix = _url_base + "/dns/list"
    _url_delete_record_prefix = _url_base + "/dns/delete"
    _url_create_record_prefix = _url_base + "/dns/create"
    _url_logout = _url_base + "/logout"
