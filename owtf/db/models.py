"""
owtf.db.models
~~~~~~~~~~~~~~

The SQLAlchemy models for every table in the OWTF DB.
"""
import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import generic_relationship



Base = declarative_base()


# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
target_association_table = Table(
    'target_session_association',
    Base.metadata,
    Column('target_id', Integer, ForeignKey('targets.id')),
    Column('session_id', Integer, ForeignKey('sessions.id'))
)

Index('target_id_idx', target_association_table.c.target_id, postgresql_using='btree')


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    active = Column(Boolean, default=False)
    targets = relationship("Target", secondary=target_association_table, backref="sessions")


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_url = Column(String, unique=True)
    host_ip = Column(String)
    port_number = Column(String)
    url_scheme = Column(String)
    alternative_ips = Column(String, nullable=True)  # Comma seperated
    host_name = Column(String)
    host_path = Column(String)
    ip_url = Column(String)
    top_domain = Column(String)
    top_url = Column(String)
    scope = Column(Boolean, default=True)
    transactions = relationship("Transaction", cascade="delete")
    poutputs = relationship("PluginOutput", cascade="delete")
    urls = relationship("Url", cascade="delete")
    commands = relationship("Command", cascade="delete")
    # Also has a column session specified as backref in
    # session model
    works = relationship("Work", backref="target", cascade="delete")

    @hybrid_property
    def max_user_rank(self):
        user_ranks = [-1]
        user_ranks += [poutput.user_rank for poutput in self.poutputs]
        return(max(user_ranks))

    @hybrid_property
    def max_owtf_rank(self):
        owtf_ranks = [-1]
        owtf_ranks += [poutput.owtf_rank for poutput in self.poutputs]
        return(max(owtf_ranks))

    def __repr__(self):
        return "<Target (url='%s')>" % (self.target_url)


# This table actually allows us to make a many to many relationship
# between transactions table and grep_outputs table
transaction_association_table = Table(
    'transaction_grep_association',
    Base.metadata,
    Column('transaction_id', Integer, ForeignKey('transactions.id')),
    Column('grep_output_id', Integer, ForeignKey('grep_outputs.id'))
)

Index('transaction_id_idx', transaction_association_table.c.transaction_id, postgresql_using='btree')


class Transaction(Base):
    __tablename__ = "transactions"

    target_id = Column(Integer, ForeignKey("targets.id"))
    id = Column(Integer, primary_key=True)
    url = Column(String)
    scope = Column(Boolean, default=False)
    method = Column(String)
    data = Column(String, nullable=True)  # Post DATA
    time = Column(Float(precision=10))
    time_human = Column(String)
    local_timestamp = Column(DateTime)
    raw_request = Column(Text)
    response_status = Column(String)
    response_headers = Column(Text)
    response_size = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    binary_response = Column(Boolean, nullable=True)
    session_tokens = Column(String, nullable=True)
    login = Column(Boolean, nullable=True)
    logout = Column(Boolean, nullable=True)
    grep_outputs = relationship(
        "GrepOutput",
        secondary=transaction_association_table,
        cascade="delete",
        backref="transactions"
    )

    def __repr__(self):
        return "<HTTP Transaction (url='%s' method='%s' response_status='%s')>" % (self.url, self.method,
                                                                                   self.response_status)


class GrepOutput(Base):
    __tablename__ = "grep_outputs"

    target_id = Column(Integer, ForeignKey("targets.id"))
    id = Column(Integer, primary_key=True)
    name = Column(String)
    output = Column(Text)
    # Also has a column transactions, which is added by
    # using backref in transaction

    __table_args__ = (UniqueConstraint('name', 'output', target_id),)


class Url(Base):
    __tablename__ = "urls"

    target_id = Column(Integer, ForeignKey("targets.id"))
    url = Column(String, primary_key=True)
    visited = Column(Boolean, default=False)
    scope = Column(Boolean, default=True)

    def __repr__(self):
        return "<URL (url='%s')>" % (self.url)


class PluginOutput(Base):
    __tablename__ = "plugin_outputs"

    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    # There is a column named plugin which is caused by backref from the plugin class
    id = Column(Integer, primary_key=True)
    plugin_code = Column(String)  # OWTF Code
    plugin_group = Column(String)
    plugin_type = Column(String)
    date_time = Column(DateTime, default=datetime.datetime.now())
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    output = Column(String, nullable=True)
    error = Column(String, nullable=True)
    status = Column(String, nullable=True)
    user_notes = Column(String, nullable=True)
    user_rank = Column(Integer, nullable=True, default=-1)
    owtf_rank = Column(Integer, nullable=True, default=-1)
    output_path = Column(String, nullable=True)

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time

    __table_args__ = (UniqueConstraint('plugin_key', 'target_id'),)


cmd_host = Table('command_register_host', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('host_id', Integer, ForeignKey('hosts.id'))
)

cmd_iface = Table('command_register_iface', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('iface_id', Integer, ForeignKey('ifaces.id'))
)

cmd_service = Table('command_register_service', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('service_id', Integer, ForeignKey('services.id'))
)

cmd_cred = Table('command_register_cred', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('cred_id', Integer, ForeignKey('creds.id'))
)

cmd_vuln = Table('command_register_vuln', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('vuln_id', Integer, ForeignKey('vulns.id'))
)

cmd_note = Table('command_register_note', Base.metadata,
    Column('command_register_id', String, ForeignKey('command_register.original_command')),
    Column('note_id', Integer, ForeignKey('event.id'))
)

class Command(Base):
    __tablename__ = "command_register"

    start_time = Column(DateTime)
    end_time = Column(DateTime)
    success = Column(Boolean, default=False)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))

    modified_command = Column(String)
    original_command = Column(String, primary_key=True)

    plugin_output_id = Column(String, ForeignKey("plugin_outputs.id"))
    plugin_output = relationship(PluginOutput, backref=backref('commands', uselist=True))

    hosts = relationship(
        "Host",
        secondary=cmd_host,
        back_populates="commands")

    ifaces = relationship(
        "Iface",
        secondary=cmd_iface,
        back_populates="commands")

    services = relationship(
        "Service",
        secondary=cmd_service,
        back_populates="commands")

    creds = relationship(
        "Cred",
        secondary=cmd_cred,
        back_populates="commands")

    vulns = relationship(
        "Vuln",
        secondary=cmd_vuln,
        back_populates="commands")

    notes = relationship(
        "Note",
        secondary=cmd_note,
        back_populates="commands")

    @hybrid_property
    def run_time(self):
        return self.end_time - self.start_time


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True)
    owtf_message = Column(String)
    traceback = Column(String, nullable=True)
    user_message = Column(String, nullable=True)
    reported = Column(Boolean, default=False)
    github_issue_url = Column(String, nullable=True)

    def __repr__(self):
        return "<Error (traceback='%s')>" % (self.traceback)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    dirty = Column(Boolean, default=False)  # Dirty if user edited it. Useful while updating
    resource_name = Column(String)
    resource_type = Column(String)
    resource = Column(String)
    __table_args__ = (UniqueConstraint('resource', 'resource_type', 'resource_name'),)


class ConfigSetting(Base):
    __tablename__ = "configuration"

    key = Column(String, primary_key=True)
    value = Column(String)
    section = Column(String)
    descrip = Column(String, nullable=True)
    dirty = Column(Boolean, default=False)

    def __repr__(self):
        return "<ConfigSetting (key='%s', value='%s', dirty='%r')>" % (self.key, self.value, self.dirty)


class TestGroup(Base):
    __tablename__ = "test_groups"

    code = Column(String, primary_key=True)
    group = Column(String)  # web, network
    descrip = Column(String)
    hint = Column(String, nullable=True)
    url = Column(String)
    priority = Column(Integer)
    plugins = relationship("Plugin")


class Plugin(Base):
    __tablename__ = "plugins"

    key = Column(String, primary_key=True)  # key = type@code
    title = Column(String)
    name = Column(String)
    code = Column(String, ForeignKey("test_groups.code"))
    group = Column(String)
    type = Column(String)
    descrip = Column(String, nullable=True)
    file = Column(String)
    attr = Column(String, nullable=True)
    works = relationship("Work", backref="plugin", cascade="delete")
    outputs = relationship("PluginOutput", backref="plugin")

    def __repr__(self):
        return "<Plugin (code='%s', group='%s', type='%s')>" % (self.code, self.group, self.type)

    @hybrid_property
    def min_time(self):
        """
        Consider last 5 runs only, better performance and accuracy
        """
        poutputs_num = len(self.outputs)
        if poutputs_num != 0:
            if poutputs_num < 5:
                run_times = [poutput.run_time for poutput in self.outputs]
            else:
                run_times = [poutput.run_time for poutput in self.outputs[-5:]]
            return min(run_times)
        else:
            return None

    @hybrid_property
    def max_time(self):
        """
        Consider last 5 runs only, better performance and accuracy
        """
        poutputs_num = len(self.outputs)
        if poutputs_num != 0:
            if poutputs_num < 5:
                run_times = [poutput.run_time for poutput in self.outputs]
            else:
                run_times = [poutput.run_time for poutput in self.outputs[-5:]]
            return max(run_times)
        else:
            return None

    __table_args__ = (UniqueConstraint('type', 'code'),)


class Work(Base):
    __tablename__ = "worklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey("targets.id"))
    plugin_key = Column(String, ForeignKey("plugins.key"))
    active = Column(Boolean, default=True)
    # Columns plugin and target are created using backrefs

    __table_args__ = (UniqueConstraint('target_id', 'plugin_key'),)

    def __repr__(self):
        return "<Work (target='%s', plugin='%s')>" % (self.target_id, self.plugin_key)


class Mapping(Base):
    __tablename__ = 'mappings'

    owtf_code = Column(String, primary_key=True)
    mappings = Column(String)
    category = Column(String, nullable=True)

# Report Enhancement


class Host(Base):
    __tablename__ = 'hosts'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Host", _id, self.name)

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)
    name = Column(String)

    session_id = Column(Integer, ForeignKey('sessions.id'))
    session = relationship(Session, backref=backref('hosts', uselist=True))

    description = Column(String, nullable=True)
    os = Column(String, nullable=True)

    commands = relationship(
        "Command",
        secondary=cmd_host,
        back_populates="hosts")


class Iface(Base):
    __tablename__ = 'ifaces'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Iface", _id, self.name)

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)
    name = Column(String)
    description = Column(String, nullable=True)

    host_id = Column(Integer, ForeignKey('hosts.id'))
    host = relationship(Host, backref=backref('ifaces', uselist=True))


    mac = Column(String)

    ipv4_address = Column(String, nullable=True)
    ipv4_gateway = Column(String, nullable=True)
    ipv4_mask = Column(String, nullable=True)

    ipv6_address = Column(String, nullable=True)
    ipv6_gateway = Column(String, nullable=True)
    ipv6_mask = Column(String, nullable=True)

    network_segment = Column(String, nullable=True)

    commands = relationship(
        "Command",
        secondary=cmd_iface,
        back_populates="ifaces")


class Service(Base):
    __tablename__ = 'services'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Service", _id, self.name)

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)

    name = Column(String)
    description = Column(String, nullable=True)

    iface_id = Column(Integer, ForeignKey('ifaces.id'))
    iface = relationship(Iface, backref=backref('services', uselist=True))

    ports = Column(String, nullable=True) # json
    protocol = Column(String, nullable=True)
    status = Column(String, nullable=True)
    version = Column(String, nullable=True)


    commands = relationship(
        "Command",
        secondary=cmd_service,
        back_populates="services")

class Cred(Base):
    __tablename__ = 'creds'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Cred", _id, self.username + ":" + self.passord)

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)

    name = Column(String)
    description = Column(String, nullable=True)

    service_id = Column(Integer, ForeignKey('services.id'))
    service = relationship(Service, backref=backref('creds', uselist=True))

    username = Column(String, nullable=True)
    password = Column(String, nullable=True)

    commands = relationship(
        "Command",
        secondary=cmd_cred,
        back_populates="creds")


class Vuln(Base):
    __tablename__ = 'vulns'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Vuln", _id, self.name)

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)
    
    name = Column(String)
    description = Column(String, nullable=True)
    type = Column(String(20))

    service_id = Column(Integer, ForeignKey('services.id'))
    service = relationship(Service, backref=backref('vulns', uselist=True))

    resolution = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    refs = Column(String, nullable=True) # json


    commands = relationship(
        "Command",
        secondary=cmd_vuln,
        back_populates="vulns")

    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'vulns'
    }

class VulnWeb(Vuln):
    __mapper_args__ = {
        'polymorphic_identity':'vuln_webs'
    }
    path = Column(String, nullable=True)
    website = Column(String, nullable=True)
    request = Column(String, nullable=True)
    response = Column(String, nullable=True)
    method = Column(String, nullable=True)
    pname = Column(String, nullable=True)
    params = Column(String, nullable=True)
    query = Column(String, nullable=True)
    attachments = Column(String, nullable=True)


class Note(Base):
    __tablename__ = 'event'

    def __str__(self):
        _id = '(none)'
        if self.id:
            _id = self.id
        return "%s _id: %s_: %s" % ("Note", _id, self.name)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String, nullable=True)
    text = Column(String, nullable=True)

    # This is used to discriminate between the linked tables.
    object_type = Column(String(255))

    # This is used to point to the primary key of the linked row.
    object_id = Column(Integer)

    object = generic_relationship(object_type, object_id)


    commands = relationship(
        "Command",
        secondary=cmd_note,
        back_populates="notes")
