import os
import json

from sqlalchemy.exc import SQLAlchemyError

from framework.dependency_management.dependency_resolver import BaseComponent
from framework.dependency_management.interfaces import WReportManagerInterface
from framework.db import models
from framework.lib import exceptions


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
        wreport = self.db.session.query(models.WriteReport).order_by(models.WriteReport.updated_at.desc()).all()
        return wreport

    def load(self, id):
        wreport = self.db.session.query(models.WriteReport).get(id)
        return wreport

    def save(self, data):
        obj = self.load(data['id'])
        if not obj:
            raise exceptions.InvalidWriteReportReference("No write report with id: %s" % str(data['id']))

        obj.title = data['title']
        obj.content = data['content']
        self.db.session.merge(obj)
        try:
            self.db.session.commit()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
        return obj
        
    def create(self, data):
        obj = models.WriteReport(title=data['title'], content=data['content'])
        self.db.session.add(obj)
        try:
            self.db.session.commit()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
        return obj


    def delete(self, id):
        self.db.session.query(models.WriteReport).filter(models.WriteReport.id == id).delete()
        try:
            self.db.session.commit()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e