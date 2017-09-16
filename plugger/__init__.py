#! /usr/bin/env python
# coding: utf-8


"""
Setuptools entry-points-based plugin manager library.

Features:
* Gathers entrypoints based on namespace given
* Filters entrypoints based on the name of an ABC the plugin needs to implement
* Resolves entrypoint conflicts by preferring non-internal plugins, then
  raising an exception if there are still more than 1.
* Conflict resolver may be overridden to provide more fine-grained control.
* Validates chosen plugin is an instance of the target ABC.
* Multi-plugin support - if multiple plugins may implement an API
  simultaneously, all matching plugins are returned.
"""


# [ Imports ]
import pkg_resources
import warnings


# [ API ]
def get_external_entry_point(entry_points, *, target, namespace):
    """Return the single external entry_point if possible, or raise an exception."""
    if not entry_points:
        raise RuntimeError(f"No entry_points found for {namespace}")
    if len(entry_points) == 1:
        return entry_points[0]

    external_entry_points = []
    for this_entry_point in entry_points:
        entry_point_module = this_entry_point.module_name.split('.')[0]
        target_module = target.__module__.split('.')[0]
        if entry_point_module != target_module:
            external_entry_points.append(this_entry_point)

    num_external_entry_points = len(external_entry_points)
    if 1 < len(external_entry_points):
        raise RuntimeError(f"Too many ({num_external_entry_points}) plugins for {namespace}.")

    return external_entry_points[0]


class Plugger:
    """Plugin management tool."""

    def __init__(self, namespace):
        """Init the state."""
        self._namespace = namespace

    # [ API ]
    def resolve(self, target, *, conflict_resolver=get_external_entry_point, output=print):
        """Resolve the plugin for the given target."""
        plugins = {}
        output(f"Loading plugins for {self._namespace}...")
        namespace_entry_points = pkg_resources.iter_entry_points(self._namespace)
        namespace_entry_points = list(namespace_entry_points)
        target_entry_points = [ep for ep in namespace_entry_points if ep.name == target.__name__]
        entry_point = conflict_resolver(target_entry_points, target=target, namespace=self._namespace)
        plugin = entry_point.load()()
        if isinstance(plugin, target):
            output(f"  {entry_point.module_name}:{entry_point.name}")
        else:
            raise RuntimeError(f"Plugin {entry_point.module_name}:{entry_point.name} is not a subclass of the target ABC ({target})")
        return plugin

    def resolve_any(self, target, *, output=print):
        """Resolve the plugins for the given target."""
        plugins = {}
        output(f"Loading plugins for {self._namespace}...")
        namespace_entry_points = pkg_resources.iter_entry_points(self._namespace)
        target_entry_points = [ep for ep in namespace_entry_points if ep.name == target.__name__]
        plugins = [ep.load()() for ep in target_entry_points]
        valid_plugins = []
        for entry_point, this_plugin in zip(target_entry_points, plugins):
            if isinstance(this_plugin, target):
                output(f"  {entry_point.module_name}:{entry_point.name}")
                valid_plugins.append(this_plugin)
            else:
                warnings.warn(f"Plugin {entry_point.module_name}:{entry_point.name} is not a subclass of the target ABC ({target})")
        return valid_plugins
