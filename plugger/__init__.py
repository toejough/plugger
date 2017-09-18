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
* Validates chosen plugin is an instance of the interface ABC.
* Multi-plugin support - if multiple plugins may implement an API
  simultaneously, all matching plugins are returned.
"""


# [ Imports ]
# [ -Python ]
import typing
import warnings
# [ -Third Party ]
import pkg_resources


# [ TypeVars ]
# Type, not constant
# pylint: disable=invalid-name
BaseClass = typing.TypeVar('BaseClass')
# pylint: enable=invalid-name


# [ API ]
def get_external_entry_point(
        plugins: typing.Sequence[BaseClass], *,
        interface: typing.Type[BaseClass],
        namespace: str,
) -> BaseClass:
    """Return the single external plugin if possible, or raise an exception."""
    external_plugins = []
    for this_plugin in plugins:
        plugin_module = this_plugin.__module__.split('.')[0]
        interface_module = interface.__module__.split('.')[0]
        if plugin_module != interface_module:
            external_plugins.append(this_plugin)

    num_external_plugins = len(external_plugins)
    if 1 < len(external_plugins):
        raise RuntimeError(f"Too many ({num_external_plugins}) plugins for {namespace}.")

    return external_plugins[0]


def resolve(
    interface: typing.Type[BaseClass], *,
    namespace: typing.Optional[str]=None,
    conflict_resolver: typing.Callable[..., BaseClass]=get_external_entry_point,
) -> BaseClass:
    """Resolve the plugin for the given interface."""
    plugins = resolve_any(interface, namespace=namespace)
    if not plugins:
        raise RuntimeError(f"No plugins found for {namespace}")
    elif 1 < len(plugins):
        plugin = conflict_resolver(plugins, interface=interface, namespace=namespace)
    else:
        plugin = plugins[0]
    return plugin


def resolve_any(
    interface: typing.Type[BaseClass], *,
    namespace: typing.Optional[str]=None,
) -> typing.List[BaseClass]:
    """Resolve the plugins for the given interface."""
    if namespace is None:
        namespace = interface.__module__.split('.')[0]
    namespace_entry_points = pkg_resources.iter_entry_points(namespace)
    interface_entry_points = [ep for ep in namespace_entry_points if ep.name == interface.__name__]
    plugins = [ep.load()() for ep in interface_entry_points]
    valid_plugins = []
    for entry_point, this_plugin in zip(interface_entry_points, plugins):
        if isinstance(this_plugin, interface):
            valid_plugins.append(this_plugin)
        else:
            warnings.warn(
                f"Plugin {entry_point.module_name}:{entry_point.name} is not a subclass"
                f" of the interface ABC ({interface})",
            )
    return valid_plugins


# [ Vulture Whitelist ]
# Used externally
# Whitelist here for vulture
# Disable pylint error for just the whitelist
# pylint: disable=pointless-statement
resolve
# pylint: enable=pointless-statement
