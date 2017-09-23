#! /usr/bin/env python
# coding: utf-8


"""Core plugger functionality."""


# [ Imports ]
# [ -Python ]
import typing
import warnings
# [ -Third Party ]
import pkg_resources


# [ Internals ]
def _get_external_plugin(
        plugins: typing.Sequence[type], *,
        interface: type,
) -> type:
    """
    Return the single external plugin if possible, or raise an exception.

    Parameters:
        plugins - plugins to choose from
        interface - the interface the plugins implement

    Returns the single external plugin in `plugins`

    Raises:
        RuntimeError if there are multiple external plugins
    """
    external_plugins = []
    for this_plugin in plugins:
        interface_module = interface.__module__.split('.')[0]
        plugin_module = this_plugin.__module__.split('.')[0]
        if plugin_module != interface_module:
            external_plugins.append(this_plugin)

    num_external_plugins = len(external_plugins)
    if 1 < num_external_plugins:
        raise RuntimeError(f"Too many ({num_external_plugins}) plugins for {interface_module}.")

    return external_plugins[0]


def _discover_entry_points(
    *,
    get_group_map: typing.Callable = pkg_resources.get_entry_map,
    iterate_distributions: typing.Callable = pkg_resources.Environment,
) -> typing.List["EntryPoint"]:
    """
    Discover entry points.

    Parameters:
        get_group_map - a function which is expected to take a string argument
            (the distribution/package to scan for entry points), and return a
            dictionary/map like {group1: {entry_point_name1: entry_point1, ...}, ...}
            where the group names and entry_point names are strings, and the
            entry points are pkg_resources.EntryPoint objects.
        iterate_distributions - a function which is expected to take no arguments,
            and return an iterable of strings representing installed distriutions/packages.

    Returns a list of EntryPoint objects.
    """
    entry_points = []
    for distribution in iterate_distributions():
        for group, entry_point_map in get_group_map(distribution).items():
            for raw_entry_point in entry_point_map.values():
                entry_points.append(EntryPoint(
                    raw_entry_point=raw_entry_point,
                    group=group,
                ))
    return entry_points


# [ API ]
class EntryPoint:
    """
    Entry point object.

    Wraps a raw entry point with a cleaner API.
    The original entry point is available via the `raw` property.

    This object should not be instantiated directly by users.  Use the
    `get_entry_points` function instead.  Anyone defining the `discover`
    parameter to that function may have to instantiate these objects.
    """

    def __init__(
        self, *,
        raw_entry_point: pkg_resources.EntryPoint,
        group: str,
    ) -> None:
        """Init the state."""
        self.__raw_entry_point = raw_entry_point
        self.__group = group

    @property
    def raw(self) -> pkg_resources.EntryPoint:
        """
        Return the raw entry point object being wrapped.

        Note that no guarantees are made about this object.  This is provided
        in case you know what is being wrapped, and you want to access it directly
        in order to access some data which is not exposed by the EntryPoint
        object, but the raw object is not defined or controlled by this project,
        and its API is subject to arbitrary changes.  It is provided so that if
        you want, you can get into the nitty gritty low level details, but use it
        at your own risk.
        """
        return self.__raw_entry_point

    @property
    def package(self) -> typing.Optional[str]:
        """Return the name of the package the entry point was defined in."""
        if self.raw.dist:
            return self.raw.dist.project_name
        return None

    @property
    def version(self) -> typing.Optional[str]:
        """Return the version string of the package the entry point was defined in."""
        if self.raw.dist:
            return self.raw.dist.version
        return None

    @property
    def group(self) -> str:
        """Return the entry point group this entry point was defined in in setup.py."""
        return self.__group

    @property
    def name(self) -> str:
        """Return the name given to this entry point in setup.py."""
        return self.raw.name

    def load(self) -> typing.Any:
        """Load the plugin from the entry point."""
        return self.raw.load()

    def __repr__(self) -> str:
        """Return the repr of the entry point."""
        return f"{self.package}:{self.group}:{self.name} ({self.version})"

    def __eq__(self, other: typing.Any) -> bool:
        """Return whether self == other."""
        if other.__class__ is not self.__class__:
            raise NotImplementedError
        return bool(self.__dict__ == other.__dict__)


def get_entry_points(
    *,
    name: typing.Optional[str]=None,
    group: typing.Optional[str]=None,
    discover: typing.Callable=_discover_entry_points,
) -> typing.List[EntryPoint]:
    """
    Get the entry points for the given filter options.

    Parameters:
        name - the entry point name to filter by.  If none, no name filter will be used.
        group - the entry point group name to filter by  If none, no name filter will be used.
        discover - a function, taking no arguments, which returns EntryPoint objects for all
            the entry points on the system.  The default value is good enough for most cases,
            but this dependency is exposed for testing or advanced use.

    If both name and group are left empty, all discovered entry points will be returned.
    """
    return [ep for ep in discover() if (
        (name is None or ep.name == name) and
        (group is None or ep.group == group)
    )]


def load_all_plugins_for(
    interface: type, *,
    get_filtered: typing.Callable=get_entry_points,
) -> typing.List[type]:
    """
    Load the plugins for the given interface.

    Parameters:
        interface - a class to use both as the source of correct group/name
            attributes for target plugins, but also as the base class for
            validating those plugins on load.
        get_filtered - a function, taking group and name arguments, and returning
            a list of EntryPoint objects that match.  The default value is good
            enough for most cases, but this dependency is exposed for testing or
            advanced use.

    Returns a list of plugins which match the interface.

    Plugins are found according to the following rules:
    * in a group matching the root module the interface is defined in.
    * has a name matching the name of the interface.
    * is a subclass of the interface.
    """
    group = interface.__module__.split('.')[0]
    name = interface.__name__
    entry_points = get_filtered(name=name, group=group)
    plugins = []
    for this_entry_point in entry_points:
        this_plugin = this_entry_point.load()
        if issubclass(this_plugin, interface):
            plugins.append(this_plugin)
        else:
            warnings.warn(
                f"Plugin {this_entry_point}"
                f" is not a subclass of the interface ({interface})",
            )
    return plugins


def load_best_plugin_for(
    interface: type, *,
    resolve_conflict: typing.Callable[..., type]=_get_external_plugin,
    load_all: typing.Callable=load_all_plugins_for,
) -> type:
    """
    Load the plugin for the given interface.

    Parameters:
        interface - a class to use both as the source of correct group/name
            attributes for target plugins, but also as the base class for
            validating those plugins on load.
        resolve_conflict - a function, taking a list of plugins and an interface,
            and returning a single plugin.  The default value returns the only plugin
            defined in a different root module than the given interface, if there is
            only one.  Else it raises a RuntimeError.  This is exposed with the expectation
            that while this behavior is generally correct, there are going to be exceptions,
            and it may not always be sufficient, and callers will want to supply custom
            implementations for those cases.
        load_all - a function, taking an interface argument, and returning
            a list of EntryPoint objects that match.  The default value is good
            enough for most cases, but this dependency is exposed for testing or
            advanced use.

    Returns the single plugin which matches the interface and survives conflict resolution.

    Plugins are found according to the following rules:
    * in a group matching the root module the interface is defined in.
    * has a name matching the name of the interface.
    * is a subclass of the interface.
    * is chosen by the resolve_conflict function, if there are multiple matching plugins.
    """
    plugins = load_all(interface)
    if not plugins:
        raise RuntimeError(f"No plugins found for {interface}")
    elif 1 < len(plugins):
        best = resolve_conflict(plugins, interface=interface)
    else:
        best = plugins[0]
    return best
