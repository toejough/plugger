Setuptools entry-points-based plugin library.

# Features

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

# High-/low-level API's

* high level:
    * `load_best_plugin_for`: load a single conflict resolved plugin for an interface
    * `load_all_plugins_for`: load all plugins for an interface
* low level:
    * `get_entry_points`: get all entry points, optionally filtered by group & name

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

class PluginFoo(app.Foo):
    def foo(self):
        return 'plugin foo'
```

Plugins need to be advertised as setuptools entrypoints via their `setup.py`

```python
# setup.py for the "plugin" package
setup(
    ...,
    entry_points={  # specify entry points
        'app': [  # declare that we have entry points for the 'app' entrypoint group
            'Foo = plugin:PluginFoo',  # declare entry point named 'Foo', which is our 'Foo' class.
        ],
    },
)
```

## Loading a Plugin

A single plugin gets loaded via the `load_best_plugin_for` function, which identifies and loads the best plugin on the system which implements the given base class.

```python
# "app" package
import plugger

class Foo: ...

foo_plugin = plugger.load_best_plugin_for(Foo)

# foo_plugin is now PluginFoo.
instance = foo_plugin()
result = instance.foo()

# result: 'plugin foo'
```

As the name `load_best_plugin_for` implies, any number of plugins may implement any given interface.  If a single plugin is found, it is returned.  If multiple plugins are found, the `resolve_conflict` function (a parameter of `get_best_plugin_for`) is called.  A default resolution function is provided for the case where a package includes its own default plugins, but there may be an overriding external plugin installed elsewhere on the system.  It will return the external plugin if there is only one, but will raise an exception if multiple external plugins are found for an interface.

## Loading Multiple Plugins for a Single Interface

If you have multiple plugins for a single interface installed, and you want to load them all, use `load_all_plugins_for`, which will return a list of plugins for the given interface, instead of just one.

```python
# "app" package
import plugger

class Foo: ...

all_foo_plugins = plugger.load_all_plugins_for(Foo)

# assuming 'Foo' is called out as a plugin for itself in setup.py, and
# the aforementioned 'plugin' package is installed with 'PluginFoo' also
# listed as a plugin for Foo...
# all_foo_plugins: [Foo, PluginFoo]
```

## Get Arbitrary Entry Points

If you'd like finer-grained control over what plugins get loaded, use `get_entry_points`.
You can filter by group, name, both, or none (which returns all the entrypoints on the system).

```python
# setup.py for the "app" package
setup(
    ...,
    entry_points={
        'app': [
            'Foo = plugin:Foo',
            'Bar = plugin:Bar',
        ],
    },
)
```

```python
# setup.py for the "plugin" package
setup(
    ...,
    entry_points={
        'app': [
            'Foo = plugin:PluginFoo',
            'Bar = plugin:PluginBar',
        ],
        'other': [
            'Foo = plugin:PluginOtherFoo',
        ],
    },
)
```

```python
# "app" package
import plugger

# Entry points from any package
# ... in a group named 'app'
# ... where the entry point is named 'Foo'
app_foo_entry_points = plugger.get_entry_points(group='app', name='Foo')
# [ app:app:Foo, plugin:app:Foo ]

# Entry points from any package
# ... in a group named 'app'
# ... with any entry point name
app_all_entry_points = plugger.get_entry_points(group='app')
# [ app:app:Foo, app:app:Bar, plugin:app:Foo, plugin:app:Bar ]

# Entry points from any package
# ... with any group name
# ... where the entry point is named 'Foo'
all_foo_entry_points = plugger.get_entry_points(name='Foo')
# [ app:app:Foo, plugin:app:Foo, plugin:other:Foo ]

# Entry points from any package
# ... with any group name
# ... with any entry point name
all_entry_points = plugger.get_entry_points()
# [ app:app:Foo, app:app:Bar, plugin:app:Foo, plugin:app:Bar, plugin:other:Foo ]
```

Once you have entry points, you can inspect them for things like source package (`entry_point.package`), source package version (`entry_point.version`), group name (`entry_point.group`), or entry point name (`entry_point.name`).  You can also load the plugin via `entry_point.load()`.

If that functionality isn't enough, you may also access the raw `pkg_resources.EntryPoint` object via `entry_point.raw`.
