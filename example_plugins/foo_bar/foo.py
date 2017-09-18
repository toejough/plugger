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
        return 'foo bar'


def main(multi=True):
    """Resolve and run the plugins."""
    if multi:
        bars = plugger.resolve_any(Base)
        for bar in bars:
            print(bar.bar())
    else:
        print(plugger.resolve(Base).bar())


# [ Static Analysis ]
# API's used by code Vulture can't see
Bar
main
