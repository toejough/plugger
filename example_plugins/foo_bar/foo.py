# coding: utf-8


"""Example of a project with a self-provided plugin foo.Base."""


# [ Imports ]
import plugger
import enum


# [ API ]
class Base:
    """Base class for foo's plugins."""

    def bar(self):
        """Return the bar message."""
        return 'base bar'


class Bar(Base):
    """Self-provided Bar."""

    def bar(self):
        """Return the bar message."""
        return 'foo bar'


class Level(enum.Enum):
    """Level of resolution."""

    SINGLE = enum.auto()
    MULTI = enum.auto()
    STRING = enum.auto()
    ALL = enum.auto()


def main(level=Level.SINGLE):
    """Load and run the plugins."""
    if level is Level.SINGLE:
        print(plugger.load_best_plugin_for(Base)().bar())
    elif level is Level.MULTI:
        bases = plugger.load_all_plugins_for(Base)
        for this_base in bases:
            print(this_base().bar())
    elif level is Level.STRING:
        base_entry_points = plugger.get_entry_points(group='foo', name='Base')
        for this_entry_point in base_entry_points:
            print(this_entry_point)
    elif level is Level.ALL:
        entry_points = plugger.get_entry_points()
        for this_entry_point in entry_points:
            print(this_entry_point)
    else:
        raise RuntimeError(f"Unknown level ({level})")


# [ Static Analysis ]
# API's used by code Vulture can't see
Bar
main
