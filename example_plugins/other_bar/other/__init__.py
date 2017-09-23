# coding: utf-8


"""Example of a plugin also implementing foo.Base."""


# [ Imports ]
import foo


# [ API ]
class Bar(foo.Base):
    """Other's Bar."""

    def bar(self):
        """Return the bar message."""
        return 'other bar'
