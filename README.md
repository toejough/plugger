Setuptools entry-points-based plugin manager library.

# Features

* Gathers entrypoints based on namespace given
* Filters entrypoints based on the name of an ABC the plugin needs to implement
* Resolves entrypoint conflicts by preferring non-internal plugins, then
  raising an exception if there are still more than 1.
* Conflict resolver may be overridden to provide more fine-grained control.
* Validates chosen plugin is an instance of the interface ABC.
* Multi-plugin support - if multiple plugins may implement an API
  simultaneously, all matching plugins are returned.

# Examples

## Defining A Plugin Interface

Plugin requirements are described via a base class to be implemented.  To describe what methods a plugin should implement, define a class with those methods.  The plugin will be expected to provide a subclass of the given class.

```python
# "app" package
# Plugin interface
class Foo:
    def foo(self):
        return 'base foo'
```

Any plugin for `Foo` must inherit from `Foo`.

## Defining a Plugin

Plugins should inherit from the class defining the plugin's interface.

```python
# "plugin" package
# Plugin implementation
import app

class Foo(app.Foo):
    def foo(self):
        return 'plugin foo'
```

Plugins need to be advertised as setuptools entrypoints via their `setup.py`

```python
# setup.py for the "plugin" package
setup(
    ...,
    entry_points={  # specify entry points
        'app': [  # declare that we have entry points for the 'app' entrypoint namespace
            'Foo = plugin:Foo',  # declare entry point 'Foo', which is our 'Foo' class.
        ],
    },
)
```

## Loading a Plugin

Plugins get loaded via the `resolve` function, which resolves a given interface to an available plugin (discovered by the given namespace, which defaults to the top level module the given interface is defined in), and loads it.

```python
# "app" package
import plugger

class Foo: ...

foo_plugin = plugger.resolve(Foo)
```

## Loading Multiple Plugins for a Single Interface

Any number of plugins may implement any given interface.  If you have multiple plugins for a single interface installed, and you want to load them all, use `resolve_any`, which will return a list of discovered/loaded plugins for the given interface, instead of just one.

```python
# "app" package
import plugger

class Foo: ...

all_foo_plugins = plugger.resolve_any(Foo)
```

## Conflict Resolution for Multiple Plugins

Any number of plugins may implement any given interface.  If you have multiple plugins for a single interface installed, and you only want one, you will likely need to provide a conflict resolution function to `resolve`.  The default resolution function will return the external plugin if both the interface-defining package and a single external package define plugins, and will raise an exception if multiple external plugins are found.

```python
# "app" package
import plugger

class Foo: ...

def resolve_to_first_plugin(plugins, *, interface, namespace):
    """Return the first plugin."""
    return plugins[0]

foo_plugin = plugger.resolve(Foo, conflict_resolver=resolve_to_first_plugin)
```
