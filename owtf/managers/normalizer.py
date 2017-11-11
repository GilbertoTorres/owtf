"""
owtf.db.command_register
~~~~~~~~~~~~~~~~~~~~~~~~

Component to handle data storage and search of all commands run
"""

import json
import hashlib
from sqlalchemy.exc import SQLAlchemyError

from owtf.dependency_management.dependency_resolver import BaseComponent
from owtf.dependency_management.interfaces import CommandRegisterInterface, NormalizerInterface
from owtf.db import models
from owtf.managers.target import target_required

from sqlalchemy.sql.expression import ClauseElement

from owtf.managers.session import session_required


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        session.commit()

        return instance, True

class Normalizer(BaseComponent, NormalizerInterface):

    COMPONENT_NAME = "normalizer"

    def __init__(self):
        self.register_in_service_locator()
        self.db = self.get_component("db")

    def init(self):
        pass

    @session_required
    def process(self, filename, session_id=None):
        """Adds normalized data to DB

        :param command: Filename with json normalized output
        :type command: string
        :return: None
        :rtype: None
        """

        f = open(filename, "r")
        jcontent = f.read()
        f.close()

        jobj = json.loads(jcontent)

        session = None
        if session_id and len(session_id) > 0:
            session = session_id[0]
        for host in jobj.get('hosts'):
            
            host_obj, created = get_or_create(self.db.session, models.Host, None, 
                                                name=host.get('name'),
                                                os=host.get('os'),
                                                session_id=session
                                                )

            for iface in host.get('interfaces'):

                fields = dict(
                            mac=iface.get('mac'),
                            name=iface.get('name'),
                            description=iface.get('description'),
                            ipv4_address=iface.get('ipv4').get('address'),
                            ipv4_gateway=iface.get('ipv4').get('gateway'),
                            ipv4_mask=iface.get('ipv4').get('mask'),
                            ipv6_address=iface.get('ipv6').get('address'),
                            ipv6_gateway=iface.get('ipv6').get('gateway'),
                            ipv6_mask=iface.get('ipv6').get('mask')
                            )
                iface_obj, created = get_or_create(self.db.session, models.Iface, fields, 
                                                mac=iface.get('mac'),
                                                host_id=host_obj.id
                                                )

                for service in iface.get('services',[]):
                    fields = dict(
                            name=service.get('name'),
                            description=service.get('description'),
                            ports=json.dumps(service.get('ports', [])),
                            protocol=service.get('protocol'),
                            status=service.get('status'),
                            version=service.get('version'),
                            )
                    service_obj, created = get_or_create(self.db.session, models.Service, fields, 
                                                    name=service.get('name'),
                                                    version=service.get('version'),
                                                    iface_id=iface_obj.id,
                                                    )

                    for vuln in service.get('vulns',[]):
                        fields = dict(
                                name=vuln.get('name'),
                                description=vuln.get('description'),
                                refs=json.dumps(vuln.get('refs', [])),
                                resolution=vuln.get('resolution'),
                                severity=vuln.get('severity')
                                )
                        vuln_obj, created = get_or_create(self.db.session, models.Vuln, fields, 
                                                        name=vuln.get('name'),
                                                        service_id=service_obj.id,
                                                        )
                    for cred in service.get('creds',[]):
                        fields = dict(
                                    name=cred.get('name'),
                                    description=cred.get('description'),
                                    username=cred.get('username'),
                                    password=cred.get('password'),
                                )
                        cred_obj, created = get_or_create(self.db.session, models.Cred, fields, 
                                                        service_id=service_obj.id,
                                                        username=cred.get('username'),
                                                        password=cred.get('password'),
                                                        )

