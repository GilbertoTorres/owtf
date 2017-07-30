"""
Plugin for probing x11
"""

from framework.dependency_management.dependency_resolver import ServiceLocator


DESCRIPTION = " pingx3 ping ping ping "


def run(PluginInfo):
    resource = ServiceLocator.get_component("resource").GetResources('PINGProbeMethods')
    return ServiceLocator.get_component("plugin_helper").CommandDump('Test Command', 'Output',
                                                                     resource, PluginInfo, [])  # No previous output
