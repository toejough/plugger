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
    """Return the single external plugin if possible, or raise an exception."""
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
    """Discover entry points."""
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
        """Return the raw entry point object being wrapped."""
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
    """Get the entry points for the given filter options."""
    return [ep for ep in discover() if (
        (name is None or ep.name == name) and
        (group is None or ep.group == group)
    )]


def load_all_plugins_for(
    interface: type, *,
    get_filtered: typing.Callable=get_entry_points,
) -> typing.List[type]:
    """Load the plugins for the given interface."""
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
    """Resolve the plugin for the given interface."""
    plugins = load_all(interface)
    if not plugins:
        raise RuntimeError(f"No plugins found for {interface}")
    elif 1 < len(plugins):
        best = resolve_conflict(plugins, interface=interface)
    else:
        best = plugins[0]
    return best
