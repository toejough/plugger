#! /usr/bin/env python
# coding: utf-8


"""
Setuptools entry-points-based plugin library.

Features:
* Discovery:
    Discover plugins based on entrypoints defined in the
    `setup.py` of installed packages.
* Filtering:
    Filter entrypoints based on either strings (lower-level API)
    or a base class (higher level API - the entrypoint attributes
    to filter on are determined by inspecting the base class).
* Loading and Validation:
    Load plugins from entry points, and validate by ensuring
    the plugins implement a base class.
* Conflict Resolution:
    If a single plugin is desired, resolve multi-plugin conflicts.
    The default resolver prefers non-internal plugins, then raises
    an exception if there are still more than 1.

High-/low-level API's:
* high level:
    * `load_best_plugin_for`: load a single conflict resolved plugin for an interface
    * `load_all_plugins_for`: load all plugins for an interface
* low level:
    * `get_entry_points`: get all entry points, optionally filtered by group & name
"""


# [ Imports ]
from .core import EntryPoint, load_best_plugin_for, load_all_plugins_for, get_entry_points


# [ Vulture Whitelist ]
# Used externally
# Whitelist here for vulture
# Disable pylint error for just the whitelist
# pylint: disable=pointless-statement
EntryPoint
load_best_plugin_for
load_all_plugins_for
get_entry_points
# pylint: enable=pointless-statement
