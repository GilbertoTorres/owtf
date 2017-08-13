import os
import json

from sqlalchemy.exc import SQLAlchemyError

from framework.dependency_management.dependency_resolver import BaseComponent
from framework.dependency_management.interfaces import WReportManagerInterface
from framework.lib.exceptions import InvalidParameterType
from framework.db import models
from framework.utils import FileOperations


class WReportManager(BaseComponent, WReportManagerInterface):

    COMPONENT_NAME = "wreport_manager"

    def __init__(self):
        self.register_in_service_locator()
        self.config = self.get_component("config")
        self.target = self.get_component("target")
        self.db_config = self.get_component("db_config")
        self.db = self.get_component("db")

    def init(self):
        return """
# Introduction

## Executive Summary

# Vulnerabilities

# Conclusion

"""

    def list(self):
        wreport = self.db.session.query(models.WriteReport).all()
        return wreport

    def load(self, id):
        wreport = self.db.session.query(models.WriteReport).get(id)
        return wreport

    def save(self, id, title, content):
        self.db.session.merge(
            models.WriteReport(
                id=id,
                title=title,
                content=content
            )
        )
        self.db.session.commit()