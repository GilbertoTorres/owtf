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
from owtf.db.models import Vuln, Command, Service, Cred, Host
from sqlalchemy import and_

from random import randint


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
            output['rank'] = RANKS.get(max(output['user_rank'], output['owtf_rank']))
            grouped_plugin_outputs[output['plugin_code']].append(output)

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

        if result:
            self.write(result)
        else:
            raise tornado.web.HTTPError(400)


class ReportCommandsHostsHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    def get(self, command_id=None):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not command_id:
            raise tornado.web.HTTPError(400)
        
        result = self.get_component("db_report").get_hosts_for_command(command_id, full=True)
        db = self.get_component("db")
        
        severity_passing = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "passing")).count()
        severity_info = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "info")).count()
        severity_low = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "low")).count()
        severity_medium = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "medium")).count()
        severity_high = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "high")).count()
        severity_critical = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.id == command_id, Vuln.severity == "critical")).count()

        stats = dict(
            vulnerabilities=dict(
                severity=dict(
                    passing=severity_passing,
                    info=severity_info,
                    low=severity_low,
                    medium=severity_medium,
                    high=severity_high,
                    critical=severity_critical,
                    )))
        if result:
            self.write(dict(hosts=result, stats=stats))
        else:
            raise tornado.web.HTTPError(400)

class ReportPluginOutputsHostsHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    def get(self, plugin_output_id=None):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not plugin_output_id:
            raise tornado.web.HTTPError(400)
        
        result = self.get_component("db_report").get_hosts_for_plugin_output(plugin_output_id, full=True)
        db = self.get_component("db")
        # self..session.query(PluginOutput).filter_by(target_id=target_id, plugin_key=plugin_key).count()
        
        severity_passing = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "passing")).count()
        severity_info = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "info")).count()
        severity_low = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "low")).count()
        severity_medium = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "medium")).count()
        severity_high = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "high")).count()
        severity_critical = db.session.query(Vuln) \
                        .join(Command, Vuln.commands) \
                        .filter(and_(Command.plugin_output_id == plugin_output_id, Vuln.severity == "critical")).count()

        stats = dict(
            vulnerabilities=dict(
                severity=dict(
                    passing=severity_passing,
                    info=severity_info,
                    low=severity_low,
                    medium=severity_medium,
                    high=severity_high,
                    critical=severity_critical,
                    )))
        if result:
            self.write(dict(hosts=result, stats=stats))
        else:
            raise tornado.web.HTTPError(400)


class ReportStatsTableHandler(APIRequestHandler):
    """
    Class handling API methods related to export report funtionality.
    This API returns all information about a target scan present in OWTF.
    :raise InvalidTargetReference: If target doesn't exists.
    :raise InvalidParameterType: If some unknown parameter in `filter_data`.
    """
    # TODO: Add API documentation.

    SUPPORTED_METHODS = ['GET']

    def get(self, type, id, entity):
        """
        REST API - /api/targets/<target_id>/export/ returns JSON(data) for template.
        """
        if not type or not type in ("plugin_outputs", "commands"):
            raise tornado.web.HTTPError(400)
        if not entity or not entity in ("hosts","services","vulns","creds", "commands"):
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
        elif entity == "services":
            query = db.session.query(Service)
            if type == "plugin_outputs":
                query = query.join(Command, Service.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Service.commands)
                query = query.filter(and_(Command.id == id))
        elif entity == "vulns":
            query = db.session.query(Vuln)
            if type == "plugin_outputs":
                query = query.join(Command, Vuln.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Vuln.commands)
                query = query.filter(and_(Command.id == id))
        elif entity == "creds":
            query = db.session.query(Cred)
            if type == "plugin_outputs":
                query = query.join(Command, Cred.commands)
                query = query.filter(and_(Command.plugin_output_id == id))
            elif type == "commands":
                query = query.join(Command, Cred.commands)
                query = query.filter(and_(Command.id == id))
        elif entity == "commands":
            query = db.session.query(Command)
            if type == "plugin_outputs":
                query = query.filter(and_(Command.plugin_output_id == id, Command.normalized == True))
            elif type == "commands":
                query = query.filter(and_(Command.id == id, Command.normalized == True))

        objs = query.all()
        objs_dict = [obj.to_dict() for obj in objs]
        # FIXME: update with real data
        for obj in objs_dict:
            obj.update({'count': randint(0,5)}
                )
        self.write(dict(objs=objs_dict))
