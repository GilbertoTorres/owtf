"""
owtf.db.command_register
~~~~~~~~~~~~~~~~~~~~~~~~

Component to handle data storage and search of all commands run
"""

import logging
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

    def found_log(self, obj, created):
        if created:
            condition = "new"
        else:
            condition = "existing"
        logging.info("%10s %s found!", condition, obj)




    @session_required
    def process(self, cmd, filename, session_id=None):
        """Adds normalized data to DB

        :param command: Filename with json normalized output
        :type command: string
        :return: None
        :rtype: None
        """

        # hack: we have to get a new instance so it works. If not, we get an Exception:
        # 'This Session's transaction has been rolled back due to a previous exception during flush [...]'
        new_cmd_instance = register_entry = self.db.session.query(models.Command).get(cmd.id)

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
            host_obj.commands.append(new_cmd_instance)
            self.found_log(host_obj, created)

            for note in host.get('notes',[]):
                fields = dict(
                            name=note.get('name'),
                            description=note.get('description'),
                            text=note.get('text'),
                        )
                note_obj, created = get_or_create(self.db.session, models.Note, fields, 
                                                object=host_obj,
                                                text=note.get('text'),
                                                )
                note_obj.commands.append(new_cmd_instance)
                self.found_log(note_obj, created)


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
                                                host=host_obj
                                                )
                iface_obj.commands.append(new_cmd_instance)
                self.found_log(iface_obj, created)

                for note in iface.get('notes',[]):
                    fields = dict(
                                name=note.get('name'),
                                description=note.get('description'),
                                text=note.get('text'),
                            )
                    note_obj, created = get_or_create(self.db.session, models.Note, fields, 
                                                    object=ifacet_obj,
                                                    text=note.get('text'),
                                                    )
                    note_obj.commands.append(new_cmd_instance)
                    self.found_log(note_obj, created)

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
                                                    iface=iface_obj,
                                                    )
                    service_obj.commands.append(new_cmd_instance)
                    self.found_log(service_obj, created)

                    
                    for note in service.get('notes',[]):
                        fields = dict(
                                    name=note.get('name'),
                                    description=note.get('description'),
                                    text=note.get('text'),
                                )
                        note_obj, created = get_or_create(self.db.session, models.Note, fields, 
                                                        object=service_obj,
                                                        text=note.get('text'),
                                                        )
                        note_obj.commands.append(new_cmd_instance)
                        self.found_log(note_obj, created)

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
                                                        service=service_obj,
                                                        )
                        vuln_obj.commands.append(new_cmd_instance)
                        self.found_log(vuln_obj, created)
                        
                    for cred in service.get('creds',[]):
                        fields = dict(
                                    name=cred.get('name'),
                                    description=cred.get('description'),
                                    username=cred.get('username'),
                                    password=cred.get('password'),
                                )
                        cred_obj, created = get_or_create(self.db.session, models.Cred, fields, 
                                                        service=service_obj,
                                                        username=cred.get('username'),
                                                        password=cred.get('password'),
                                                        )
                        cred_obj.commands.append(new_cmd_instance)
                        self.found_log(cred_obj, created)

