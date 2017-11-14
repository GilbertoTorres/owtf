"""
owtf.db.plugin_manager

This module manages the plugins and their dependencies
"""

import os
import imp
import json

from sqlalchemy import or_

from owtf.db.models import Command, PluginOutput, Target, Host
from owtf.dependency_management.dependency_resolver import BaseComponent
from owtf.dependency_management.interfaces import ReportDBInterface
from owtf.utils import FileOperations

class ReportDB(BaseComponent, ReportDBInterface):

    COMPONENT_NAME = "db_report"

    def __init__(self):
        self.register_in_service_locator()
        self.db = self.get_component("db")

    def init(self):
        self.timer = self.get_component("timer")

    def get_hosts_for_plugin_output(self, plugin_output_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        hosts = self.db.session.query(Host).join(Command, Host.commands) \
                            .filter(Command.plugin_output_id == plugin_output_id) \
                            .all()
        if hosts:
            if full:
                return [host.to_dict_full() for host in hosts]
            else:
                return [host.to_dict() for host in hosts]
        return []

    def get_ifaces_for_plugin_output(self, plugin_output_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        ifaces = self.db.session.query(Iface).join(Command, Iface.commands) \
                            .filter(Command.plugin_output_id == plugin_output_id) \
                            .all()
        if ifaces:
            if full:
                return [iface.to_dict_full() for iface in ifaces]
            else:
                return [iface.to_dict() for iface in ifaces]
        return []

    def get_services_for_plugin_output(self, plugin_output_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        services = self.db.session.query(Service).join(Command, Service.commands) \
                            .filter(Command.plugin_output_id == plugin_output_id) \
                            .all()
        if services:
            if full:
                return [service.to_dict_full() for service in services]
            else:
                return [service.to_dict() for service in services]
        return []

    def get_vulns_for_plugin_output(self, plugin_output_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        vulns = self.db.session.query(Vuln).join(Command, Vuln.commands) \
                            .filter(Command.plugin_output_id == plugin_output_id) \
                            .all()
        if vulns:
            if full:
                return [vuln.to_dict_full() for vuln in vulns]
            else:
                return [vuln.to_dict() for vuln in vulns]
        return []

    def get_creds_for_plugin_output(self, plugin_output_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        creds = self.db.session.query(Cred).join(Command, Cred.commands) \
                            .filter(Command.plugin_output_id == plugin_output_id) \
                            .all()
        if creds:
            if full:
                return [cred.to_dict_full() for cred in creds]
            else:
                return [cred.to_dict() for cred in creds]
        return []

    def get_hosts_for_command(self, command_id, full=False):
        """Get all test groups from th DB

        :return:
        :rtype:
        """
        cmd = self.db.session.query(Command).get(command_id)
        if cmd:
            if full:
                return [host.to_dict_full() for host in cmd.hosts]
            else:
                return [host.to_dict() for host in cmd.hosts]
        return []
