# coding: utf-8


"""Example of a project with a self-provided plugin foo.Base."""


# [ Imports ]
import plugger


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
        return 'bar'


def main():
    """Resolve and run the plugins."""
    bars = plugger.Plugger('foo').resolve_any(Base)
    for bar in bars:
        print(bar.bar())


# [ Static Analysis ]
# API's used by code Vulture can't see
Bar
main
