"""
owtf.plugin.plugin_helper
~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains helper functions to make plugins simpler to read and write,
centralising common functionality easy to reuse

NOTE: This module has not been refactored since this is being deprecated
"""


import cgi
import logging
from tornado.template import Template

from owtf.dependency_management.dependency_resolver import BaseComponent
from owtf.lib.exceptions import FrameworkAbortException, PluginAbortException
from owtf.lib.general import *
from owtf.utils import FileOperations, hash_for_cmd


PLUGIN_OUTPUT = {"type": None, "output": None}  # This will be json encoded and stored in db as string


class PluginHelper(BaseComponent):

    COMPONENT_NAME = "plugin_helper"
    mNumLinesToShow = 25

    def __init__(self):
        self.register_in_service_locator()
        self.config = self.get_component("config")
        self.db = self.get_component("db")
        self.normalizer = self.get_component("normalizer")
        self.target = self.get_component("target")
        self.url_manager = self.get_component("url_manager")
        self.plugin_handler = self.get_component("plugin_handler")
        self.reporter = self.get_component("reporter")
        self.requester = self.get_component("requester")
        self.shell = self.get_component("shell")
        self.timer = self.get_component("timer")
        # Compile regular expressions only once on init:
        self.robots_allow_regex = re.compile("Allow: ([^\n  #]+)")
        self.robots_disallow_regex = re.compile("Disallow: ([^\n #]+)")
        self.robots_sitemap = re.compile("Sitemap: ([^\n #]+)")

    def multi_replace(self, text, replace_dict):
        """ This redundant method is here so that plugins can use it

        :param text: Text to replace with
        :type text: `str`
        :param replace_dict: Dict to modify
        :type replace_dict: `dict`
        :return: Replaced dict
        :rtype: `dict`
        """
        return multi_replace(text, replace_dict)

    def cmd_table(self, command):
        """Format the command table

        :param command: Command ran
        :type command: `str`
        :return: Plugin output
        :rtype: `list`
        """
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "cmd_table"
        plugin_output["output"] = {"Command": command}
        return [plugin_output]

    def link_list(self, link_list_name, links):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "link_list"
        plugin_output["output"] = {"link_listName": link_list_name, "Links": links}
        return [plugin_output]

    def resource_linklist(self, ResourceListName, ResourceList):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "resource_linklist"
        plugin_output["output"] = {"ResourceListName": ResourceListName, "ResourceList": ResourceList}
        return ([plugin_output])

    def Tabbedresource_linklist(self, ResourcesList):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "Tabbedresource_linklist"
        plugin_output["output"] = {"ResourcesList": ResourcesList}
        return ([plugin_output])

    def ListPostProcessing(self, ResourceListName, link_list, HTMLlink_list):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "ListPostProcessing"
        plugin_output["output"] = {
            "ResourceListName": ResourceListName,
            "link_list": link_list,
            "HTMLlink_list": HTMLlink_list
        }
        return ([plugin_output])

    def Requestlink_list(self, ResourceListName, ResourceList, PluginInfo):
        link_list = []
        for Name, Resource in ResourceList:
            Chunks = Resource.split('###POST###')
            URL = Chunks[0]
            POST = None
            Method = 'GET'
            if len(Chunks) > 1:  # POST
                Method = 'POST'
                POST = Chunks[1]
                Transaction = self.requester.get_transaction(True, URL, Method, POST)
                if Transaction is not None and Transaction.found:
                    RawHTML = Transaction.get_raw_response_body()
                    FilteredHTML = self.reporter.sanitize_html(RawHTML)
                    NotSandboxedPath = self.plugin_handler.dump_output_file("NOT_SANDBOXED_%s.html" % Name, FilteredHTML,
                                                                            PluginInfo)
                    logging.info("File: NOT_SANDBOXED_%s.html saved to: %s", Name, NotSandboxedPath)
                    iframe_template = Template("""
                        <iframe src="{{ NotSandboxedPath }}" sandbox="" security="restricted"  frameborder='0'
                        style="overflow-y:auto; overflow-x:hidden;width:100%;height:100%;" >
                        Your browser does not support iframes
                        </iframe>
                        """)
                    iframe = iframe_template.generate(NotSandboxedPath=NotSandboxedPath.split('/')[-1])
                    SandboxedPath = self.plugin_handler.dump_output_file("SANDBOXED_%s.html" % Name, iframe, PluginInfo)
                    logging.info("File: SANDBOXED_%s.html saved to: %s", Name, SandboxedPath)
                    link_list.append((Name, SandboxedPath))
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "Requestlink_list"
        plugin_output["output"] = {"ResourceListName": ResourceListName, "link_list": link_list}
        return ([plugin_output])

    def VulnerabilitySearchBox(self, SearchStr):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "VulnerabilitySearchBox"
        plugin_output["output"] = {"SearchStr": SearchStr}
        return ([plugin_output])

    def SuggestedCommandBox(self, PluginInfo, CommandCategoryList, Header=''):
        plugin_output = dict(PLUGIN_OUTPUT)
        PluginOutputDir = self.InitPluginOutputDir(PluginInfo)
        plugin_output["type"] = "SuggestedCommandBox"
        plugin_output["output"] = {
            "PluginOutputDir": PluginOutputDir,
            "CommandCategoryList": CommandCategoryList,
            "Header": Header
        }
        return ([plugin_output])

    def SetConfigPluginOutputDir(self, PluginInfo):
        PluginOutputDir = self.plugin_handler.get_plugin_output_dir(PluginInfo)
        # FULL output path for plugins to use
        self.target.set_path('plugin_output_dir', "%s/%s" % (os.getcwd(), PluginOutputDir))
        self.shell.refresh_replacements()  # Get dynamic replacement, i.e. plugin-specific output directory
        return PluginOutputDir

    def InitPluginOutputDir(self, PluginInfo):
        PluginOutputDir = self.SetConfigPluginOutputDir(PluginInfo)
        FileOperations.create_missing_dirs(PluginOutputDir)  # Create output dir so that scripts can cd to it :)
        return PluginOutputDir

    def RunCommand(self, command, plugin_output, plugin_output_dir):
        framework_abort = plugin_abort = False
        if not plugin_output_dir:
            plugin_output_dir = self.Initplugin_output_dir(plugin_output)
        self.timer.start_timer('FormatCommandAndOutput')

        cmd = None
        cmd_hsh = hash_for_cmd(command)
        try:
            if self.config.do_normalize:
                cmd, raw_output = self.shell.shell_exec_monitor2(plugin_output_dir, command, plugin_output)
            else:
                raw_output = self.shell.shell_exec_monitor(plugin_output_dir, command, plugin_output)
        except plugin_abortException as PartialOutput:
            raw_output = str(PartialOutput.parameter)  # Save Partial Output
            plugin_abort = True
        except framework_abortException as PartialOutput:
            raw_output = str(PartialOutput.parameter)  # Save Partial Output
            framework_abort = True

        if cmd and self.config.do_normalize:
            norm_file = os.path.join(plugin_output_dir, "%s.json" % cmd_hsh)
            if os.path.isfile(norm_file):
                self.normalizer.process(cmd, norm_file)


        time_str = self.timer.get_elapsed_time_as_str('FormatCommandAndOutput')

        logging.info("Time=%s", time_str)
        # out = [ModifiedCommand, framework_abort, plugin_abort, time_str, raw_output, plugin_output_dir]
        out = [command, framework_abort, plugin_abort, time_str, raw_output, plugin_output_dir]
        return out

    def GetCommandOutputFileNameAndExtension(self, InputName):
        OutputName = InputName
        OutputExtension = "txt"
        if InputName.split('.')[-1] in ['html']:
            OutputName = InputName[0:-5]
            OutputExtension = "html"
        return [OutputName, OutputExtension]

    def EscapeSnippet(self, Snippet, Extension):
        if Extension == "html":  # HTML
            return str(Snippet)
        return cgi.escape(str(Snippet))  # Escape snippet to avoid breaking HTML

    def CommandDump(self, command_intro, output_intro, resource_list, plugin_output, previous_output):
        output_list = []
        plugin_output_dir = self.InitPluginOutputDir(plugin_output)
        resource_list = sorted(resource_list, key=lambda x: x[0] == "Extract URLs")
        for name, command in resource_list:
            dump_file_name = "%s.txt" % os.path.splitext(name)[0]  # Add txt extension to avoid wrong mimetypes
            _plugin_output = dict(PLUGIN_OUTPUT)
            modified_command, framework_abort, plugin_abort, time_str, raw_output, plugin_output_dir = self.RunCommand(command,
                plugin_output, plugin_output_dir)
            _plugin_output["type"] = "CommandDump"
            _plugin_output["output"] = {
                "Name": self.GetCommandOutputFileNameAndExtension(name)[0],
                "CommandIntro": command_intro,
                "ModifiedCommand": modified_command,
                "RelativeFilePath": self.plugin_handler.dump_output_file(dump_file_name, raw_output, plugin_output,
                                                                         relative_path=True),
                "OutputIntro": output_intro,
                "TimeStr": time_str
            }
            _plugin_output = [_plugin_output]
            # This command returns URLs for processing
            if name == self.config.get_val('EXTRACT_URLS_RESERVED_RESOURCE_NAME'):
                #  The _plugin_output output dict will be remade if the resource is of this type
                _plugin_output = self.LogURLsFromStr(raw_output)
            # TODO: Look below to handle streaming report
            if plugin_abort:  # Pass partial output to external handler:
                raise PluginAbortException(previous_output + _plugin_output)
            if framework_abort:
                raise FrameworkAbortException(previous_output + _plugin_output)
            output_list += _plugin_output

        return output_list

    def LogURLsFromStr(self, RawOutput):
        plugin_output = dict(PLUGIN_OUTPUT)
        self.timer.start_timer('LogURLsFromStr')
        # Extract and classify URLs and store in DB
        URLList = self.url_manager.import_urls(RawOutput.strip().split("\n"))
        NumFound = 0
        VisitURLs = False
        # TODO: Whether or not active testing will depend on the user profile ;). Have cool ideas for profile names
        if True:
            VisitURLs = True
            # Visit all URLs if not in Cache
            for Transaction in self.requester.get_transactions(True, self.url_manager.get_urls_to_visit()):
                if Transaction is not None and Transaction.found:
                    NumFound += 1
        TimeStr = self.timer.get_elapsed_time_as_str('LogURLsFromStr')
        logging.info("Spider/URL scraper time=%s", TimeStr)
        plugin_output["type"] = "URLsFromStr"
        plugin_output["output"] = {"TimeStr": TimeStr, "VisitURLs": VisitURLs, "URLList": URLList, "NumFound": NumFound}
        return [plugin_output]

    def DumpFile(self, Filename, Contents, PluginInfo, LinkName=''):
        save_path = self.plugin_handler.dump_output_file(Filename, Contents, PluginInfo)
        if not LinkName:
            LinkName = save_path
        logging.info("File: %s saved to: %s", Filename, save_path)
        template = Template("""
            <a href="{{ Link }}" target="_blank">
                {{ LinkName }}
            </a>
            """)

        return [save_path, template.generate(LinkName=LinkName, Link="../../../%s" % save_path)]

    def DumpFileGetLink(self, Filename, Contents, PluginInfo, LinkName=''):
        return self.DumpFile(Filename, Contents, PluginInfo, LinkName)[1]

    def AnalyseRobotsEntries(self, Contents):  # Find the entries of each kind and count them
        num_lines = len(Contents.split("\n"))  # Total number of robots.txt entries
        AllowedEntries = list(set(self.robots_allow_regex.findall(Contents)))  # list(set()) is to avoid repeated entries
        num_allow = len(AllowedEntries)  # Number of lines that start with "Allow:"
        DisallowedEntries = list(set(self.robots_disallow_regex.findall(Contents)))
        num_disallow = len(DisallowedEntries)  # Number of lines that start with "Disallow:"
        SitemapEntries = list(set(self.robots_sitemap.findall(Contents)))
        num_sitemap = len(SitemapEntries)  # Number of lines that start with "Sitemap:"
        RobotsFound = True
        if 0 == num_allow and 0 == num_disallow and 0 == num_sitemap:
            RobotsFound = False
        return [num_lines, AllowedEntries, num_allow, DisallowedEntries, num_disallow, SitemapEntries, num_sitemap,
                RobotsFound]

    def ProcessRobots(self, PluginInfo, Contents, LinkStart, LinkEnd, Filename='robots.txt'):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "Robots"
        num_lines, AllowedEntries, num_allow, DisallowedEntries, num_disallow, SitemapEntries, num_sitemap, NotStr = \
            self.AnalyseRobotsEntries(Contents)
        SavePath = self.plugin_handler.dump_output_file(Filename, Contents, PluginInfo, True)
        TopURL = self.target.get('top_url')
        EntriesList = []
        # robots.txt contains some entries, show browsable list! :)
        if num_disallow > 0 or num_allow > 0 or num_sitemap > 0:
            for Display, Entries in [['Disallowed Entries', DisallowedEntries], ['Allowed Entries', AllowedEntries],
                                     ['Sitemap Entries', SitemapEntries]]:
                Links = []  # Initialise category-specific link list
                for Entry in Entries:
                    if 'Sitemap Entries' == Display:
                        URL = Entry
                        self.url_manager.add_url(URL)  # Store real links in the DB
                        Links.append([Entry, Entry])  # Show link in defined format (passive/semi_passive)
                    else:
                        URL = TopURL + Entry
                        self.url_manager.add_url(URL)  # Store real links in the DB
                        # Show link in defined format (passive/semi_passive)
                        Links.append([Entry, LinkStart + Entry + LinkEnd])
                EntriesList.append((Display, Links))
                plugin_output["output"] = {
                    "NotStr": NotStr,
                    "NumLines": num_lines,
                    "NumAllow": num_allow,
                    "NumDisallow": num_disallow,
                    "NumSitemap": num_sitemap,
                    "SavePath": SavePath,
                    "EntriesList": EntriesList
                }
                return ([plugin_output])

    def TransactionTable(self, transactions_list):
        # Store transaction ids in the output, so that reporter can fetch transactions from db
        trans_ids = []
        for transaction in transactions_list:
            trans_ids.append(transaction.GetID())
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "TransactionTableFromIDs"
        plugin_output["output"] = {"TransactionIDs": trans_ids}
        return ([plugin_output])

    def TransactionTableForURLList(self, UseCache, URLList, Method=None, Data=None):
        # Have to make sure that those urls are visited ;), so we
        # perform get transactions but don't save the transaction ids etc..
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "TransactionTableForURLList"
        plugin_output["output"] = {"UseCache": UseCache, "URLList": URLList, "Method": Method, "Data": Data}
        return ([plugin_output])

    def TransactionTableForURL(self, UseCache, URL, Method=None, Data=None):
        # Have to make sure that those urls are visited ;),
        # so we perform get transactions but don't save the transaction ids
        self.requester.get_transaction(UseCache, URL, method=Method, data=Data)
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "TransactionTableForURL"
        plugin_output["output"] = {"UseCache": UseCache, "URL": URL, "Method": Method, "Data": Data}
        return ([plugin_output])

    def CreateMatchTables(self, Num):
        TableList = []
        for x in range(0, Num):
            TableList.append(self.CreateMatchTable())
        return TableList

    def HtmlString(self, html_string):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "HtmlString"
        plugin_output["output"] = {"String": html_string}
        return ([plugin_output])

    def FindResponseHeaderMatchesForRegexpName(self, HeaderRegexpName):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "ResponseHeaderMatches"
        plugin_output["output"] = {"HeaderRegexpName": HeaderRegexpName}
        return ([plugin_output])

    def FindResponseHeaderMatchesForRegexpNames(self, HeaderRegexpNamesList):
        Results = []
        for HeaderRegexpName in HeaderRegexpNamesList:
            Results += self.FindResponseHeaderMatchesForRegexpName(HeaderRegexpName)
        return Results

    def FindResponseBodyMatchesForRegexpName(self, ResponseRegexpName):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "ResponseBodyMatches"
        plugin_output["output"] = {"ResponseRegexpName": ResponseRegexpName}
        return ([plugin_output])

    def FindResponseBodyMatchesForRegexpNames(self, ResponseRegexpNamesList):
        Results = []
        for ResponseRegexpName in ResponseRegexpNamesList:
            Results += self.FindResponseBodyMatchesForRegexpName(ResponseRegexpName)
        return Results

    def ResearchFingerprintInlog(self):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "FingerprintData"
        plugin_output["output"] = {}
        return ([plugin_output])

    def FindTopTransactionsBySpeed(self, Order="Desc"):
        plugin_output = dict(PLUGIN_OUTPUT)
        plugin_output["type"] = "TopTransactionsBySpeed"
        plugin_output["output"] = {"Order": Order}
        return ([plugin_output])
