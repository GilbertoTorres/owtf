"""
owtf.api.handlers.report
~~~~~~~~~~~~~~~~~~~~~

"""

import collections
from time import gmtime, strftime
from collections import defaultdict


import tornado.gen
import tornado.web
import tornado.httpclient

from owtf.lib import exceptions
from owtf.constants import RANKS
from owtf.lib.general import cprint
from owtf.api.base import APIRequestHandler
from owtf.db.models import Session, Target, PluginOutput, Command, Host, Iface, Service, Cred, Vuln, Note
from sqlalchemy import and_

from random import randint
from owtf.managers.session import session_required

class ReportExportHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    def get(self, target_id=None):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not target_id:
            raise tornado.web.HTTPError(400)
        try:
            filter_data = dict(self.request.arguments)
            plugin_outputs = self.get_component("plugin_output").get_all(filter_data, target_id=target_id, inc_output=True)
        except exceptions.InvalidTargetReference as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        except exceptions.InvalidParameterType as e:
            cprint(e.parameter)
            raise tornado.web.HTTPError(400)
        # Group the plugin outputs to make it easier in template
        grouped_plugin_outputs = defaultdict(list)
        for output in plugin_outputs:
            # clean small_stdout for docxtemplate
            if output['commands']:
                for cmd in output['commands']:
                    # cmd['small_stdout'] = escape(cmd['small_stdout'])
                    pass
            if output['plugin']:
                output['plugin_type'] = output['plugin']['type']

            output['rank'] = RANKS.get(max(output['user_rank'], output['owtf_rank']))
            grouped_plugin_outputs[output['plugin']['code']].append(output)

            


        # Needed ordered list for ease in templates
        grouped_plugin_outputs = collections.OrderedDict(sorted(grouped_plugin_outputs.items()))

        # Get mappings
        mappings = self.get_argument("mapping", None)
        if mappings:
            mappings = self.get_component("mapping_db").get_mappings(mappings)

        # Get test groups as well, for names and info links
        test_groups = {}
        for test_group in self.get_component("db_plugin").get_all_test_groups():
            test_group["mapped_code"] = test_group["code"]
            test_group["mapped_descrip"] = test_group["descrip"]
            if mappings and test_group['code'] in mappings:
                code, description = mappings[test_group['code']]
                test_group["mapped_code"] = code
                test_group["mapped_descrip"] = description
            test_groups[test_group['code']] = test_group

        vulnerabilities = []
        for key, value in list(grouped_plugin_outputs.items()):
            test_groups[key]["data"] = value
            vulnerabilities.append(test_groups[key])

        result = self.get_component("target").get_target_config_by_id(target_id)
        result["vulnerabilities"] = vulnerabilities
        result["time"] = strftime("%Y-%m-%d %H:%M:%S", gmtime())


        result["report"] = dict()
        db = self.get_component("db")
        query = db.session.query(Command)
        query = query.join(PluginOutput)
        query = query.filter(and_(PluginOutput.target_id == target_id, Command.normalized == True))
        
        commands = query.all()
        command_ids = [cmd.id for cmd in commands]

        host_count = db.session.query(Host) \
                                .join(Command, Host.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        iface_count = db.session.query(Iface) \
                                .join(Command, Iface.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        service_count = db.session.query(Service) \
                                .join(Command, Service.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        vuln_count = db.session.query(Vuln) \
                                .join(Command, Vuln.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        cred_count = db.session.query(Cred) \
                                .join(Command, Cred.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        note_count = db.session.query(Note) \
                                .join(Command, Note.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        summary = dict(
                    host_count=host_count,
                    iface_count=iface_count,
                    service_count=service_count,
                    vuln_count=vuln_count,
                    cred_count=cred_count,
                    note_count=note_count
        )

        severity_passing = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "passing")) \
                        .distinct() \
                        .count()
        severity_info = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "info")) \
                        .distinct() \
                        .count()
        severity_low = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "low")) \
                        .distinct() \
                        .count()
        severity_medium = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "medium")) \
                        .distinct() \
                        .count()
        severity_high = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "high")) \
                        .distinct() \
                        .count()
        severity_critical = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "critical")) \
                        .distinct() \
                        .count()
        
        severities = dict(
                    passing=severity_passing,
                    info=severity_info,
                    low=severity_low,
                    medium=severity_medium,
                    high=severity_high,
                    critical=severity_critical,
                    )

        query = db.session.query(Host)
        hosts_obj = query.join(Command, Host.commands) \
                        .join(PluginOutput) \
                        .filter(and_(PluginOutput.target_id == target_id)).all()

        # query = db.session.query(Service)
        # services_obj = query.join(Command, Service.commands) \
        #                 .join(PluginOutput) \
        #                 .filter(and_(PluginOutput.target_id == target_id)).all()
                    
        # query = db.session.query(Vuln)
        # vulns_obj = query.join(Command, Vuln.commands) \
        #                 .join(PluginOutput) \
        #                 .filter(and_(PluginOutput.target_id == target_id)).all()

        # query = db.session.query(Cred)
        # creds_obj = query.join(Command, Cred.commands) \
        #                 .join(PluginOutput) \
        #                 .filter(and_(PluginOutput.target_id == target_id)).all()

        # query = db.session.query(Note)
        # notes_obj = query.join(Command, Note.commands) \
        #                 .join(PluginOutput) \
        #                 .filter(and_(PluginOutput.target_id == target_id)).all()

        query = db.session.query(Command)
        commands_obj = query \
                    .join(PluginOutput) \
                    .filter(and_(PluginOutput.target_id == target_id, Command.normalized == True)).all()

        hosts_arr = [obj.to_dict_full() for obj in hosts_obj]
        # services_arr = [obj.to_dict_full() for obj in services_obj]
        # vulns_arr = [obj.to_dict_full() for obj in vulns_obj]
        # creds_arr = [obj.to_dict_full() for obj in creds_obj]
        # notes_arr = [obj.to_dict() for obj in notes_obj]
        commands_arr = [obj.to_dict() for obj in commands_obj]

        data = dict(
            hosts=hosts_arr, 
            # services=services_arr, 
            # vulns=vulns_arr, 
            # creds=creds_arr, 
            # notes=notes_arr, 
            commands=commands_arr
        )
        result["report"]["data"] = data
        result["report"]["quantities"] = summary
        result["report"]["severities"] = severities


        if result:
            self.write(result)
        else:
            raise tornado.web.HTTPError(400)

class ReportVulnsSeverityHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    @session_required
    def get(self, type, id, session_id=None):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        
        db = self.get_component("db")

        query = db.session.query(Command)
        if type == "plugin_outputs":
            query = query.filter(and_(Command.plugin_output_id == id, Command.normalized == True))
        elif type == "commands":
            query = query.filter(and_(Command.id == id, Command.normalized == True))
        elif type == "targets":
            query = query.join(PluginOutput)
            query = query.filter(and_(PluginOutput.target_id == id, Command.normalized == True))
        elif type == "current_session":
            query = query.join(PluginOutput) \
                            .join(Target) \
                            .join(Session, Target.sessions)
            query = query.filter(and_(Session.id == session_id, Command.normalized == True))

        commands = query.all()
        command_ids = [cmd.id for cmd in commands]

        severity_passing = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "passing")) \
                        .distinct() \
                        .count()
        severity_info = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "info")) \
                        .distinct() \
                        .count()
        severity_low = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "low")) \
                        .distinct() \
                        .count()
        severity_medium = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "medium")) \
                        .distinct() \
                        .count()
        severity_high = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "high")) \
                        .distinct() \
                        .count()
        severity_critical = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id.in_(command_ids), Vuln.severity == "critical")) \
                        .distinct() \
                        .count()


        severities = dict(
                    passing=severity_passing,
                    info=severity_info,
                    low=severity_low,
                    medium=severity_medium,
                    high=severity_high,
                    critical=severity_critical,
                    )
        self.write(severities)


class ReportStatsTableHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    @session_required
    def get(self, type, id, entity, session_id):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not type or not type in ("plugin_outputs", "commands", "targets", "current_session"):
            raise tornado.web.HTTPError(400)
        if not entity or not entity in ("hosts","services","vulns","creds", "notes", "commands"):
            raise tornado.web.HTTPError(400)
        
        db = self.get_component("db")

        if entity == "hosts":
            query = db.session.query(Host)
            if type == "plugin_outputs":
                query = query.join(Command, Host.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Host.commands)
                query = query.filter(and_(Command.id == id))
            elif type == "targets":
                query = query.join(Command, Host.commands) \
                                .join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id))
            elif type == "current_session":
                query = query.join(Command, Host.commands) \
                                .join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))
        elif entity == "services":
            query = db.session.query(Service)
            if type == "plugin_outputs":
                query = query.join(Command, Service.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Service.commands)
                query = query.filter(and_(Command.id == id))
            elif type == "targets":
                query = query.join(Command, Service.commands) \
                                .join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id))
            elif type == "current_session":
                query = query.join(Command, Service.commands) \
                                .join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))
        elif entity == "vulns":
            query = db.session.query(Vuln)
            if type == "plugin_outputs":
                query = query.join(Command, Vuln.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Vuln.commands)
                query = query.filter(and_(Command.id == id))
            elif type == "targets":
                query = query.join(Command, Vuln.commands) \
                                .join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id))
            elif type == "current_session":
                query = query.join(Command, Vuln.commands) \
                                .join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))
        elif entity == "creds":
            query = db.session.query(Cred)
            if type == "plugin_outputs":
                query = query.join(Command, Cred.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Cred.commands)
                query = query.filter(and_(Command.id == id))
            elif type == "targets":
                query = query.join(Command, Cred.commands) \
                                .join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id))
            elif type == "current_session":
                query = query.join(Command, Cred.commands) \
                                .join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))
        elif entity == "notes":
            query = db.session.query(Note)
            if type == "plugin_outputs":
                query = query.join(Command, Note.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Note.commands)
                query = query.filter(and_(Command.id == id))
            elif type == "targets":
                query = query.join(Command, Note.commands) \
                                .join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id))
            elif type == "current_session":
                query = query.join(Command, Note.commands) \
                                .join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))
        elif entity == "commands":
            query = db.session.query(Command)
            if type == "plugin_outputs":
                query = query.filter(and_(Command.plugin_output_id == id, Command.normalized == True))
            elif type == "commands":
                query = query.filter(and_(Command.id == id, Command.normalized == True))
            elif type == "targets":
                query = query.join(PluginOutput)
                query = query.filter(and_(PluginOutput.target_id == id, Command.normalized == True))
            elif type == "current_session":
                query = query.join(PluginOutput) \
                                .join(Target) \
                                .join(Session, Target.sessions)
                query = query.filter(and_(Session.id == session_id, Command.normalized == True))

        objs = query.all()
        objs_arr = [obj.to_dict() for obj in objs]
        for obj in objs_arr:
            obj.update({'count': randint(0,5)}
                )
        self.write(objs_arr)

class ReportBadgeHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    @session_required
    def get(self, type, id, session_id):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not type or not type in ("plugin_outputs", "commands", "targets", "current_session"):
            raise tornado.web.HTTPError(400)
        
        db = self.get_component("db")

        query = db.session.query(Command)
        if type == "plugin_outputs":
            query = query.filter(and_(Command.plugin_output_id == id, Command.normalized == True))
        elif type == "commands":
            query = query.filter(and_(Command.id == id, Command.normalized == True))
        elif type == "targets":
            query = query.join(PluginOutput)
            query = query.filter(and_(PluginOutput.target_id == id, Command.normalized == True))
        elif type == "current_session":
            query = query.join(PluginOutput) \
                            .join(Target) \
                            .join(Session, Target.sessions)
            query = query.filter(and_(Session.id == session_id, Command.normalized == True))

        commands = query.all()
        command_ids = [cmd.id for cmd in commands]

        host_count = db.session.query(Host) \
                                .join(Command, Host.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        iface_count = db.session.query(Iface) \
                                .join(Command, Iface.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        service_count = db.session.query(Service) \
                                .join(Command, Service.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        vuln_count = db.session.query(Vuln) \
                                .join(Command, Vuln.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        cred_count = db.session.query(Cred) \
                                .join(Command, Cred.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()
        note_count = db.session.query(Note) \
                                .join(Command, Note.commands) \
                                .filter(and_(Command.id.in_(command_ids))) \
                                .distinct() \
                                .count()

        result = dict(
                    badge=dict(
                        host_count=host_count,
                        iface_count=iface_count,
                        service_count=service_count,
                        vuln_count=vuln_count,
                        cred_count=cred_count,
                        note_count=note_count
                        )
                    )
        self.write(result)

