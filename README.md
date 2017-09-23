Setuptools entry-points-based plugin library.

* [Features](#features)
* [High-/low-level API's](#apis)
* [How-To Examples](#howto)
* [Tutorial](#tutorial)
* [API Docs](#docs)
* [Discussion](#discussion)

<a name='features' />

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

<a name='apis' />

# High-/low-level API's

* high level:
    * `load_best_plugin_for`: load a single conflict resolved plugin for an interface
    * `load_all_plugins_for`: load all plugins for an interface
* low level:
    * `get_entry_points`: get all entry points, optionally filtered by group & name

<a name='howto' />

# Specific How-To Examples

The [tutorial](#tutorial) takes advantage of the plugin interface and implementations provided in `example_plugins`.  The below walks you through creating your own, as well as more examples of using the API.

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

<a name='tutorial' />

# Tutorial

The [how-to's](#howto) give a good high-level overview of what's possible with this library,
but if you want a hands-on example, here it is.  This tutorial uses the `example_plugins` directory.
This will get you up to speed with what is a plugin interface, a plugin, an entry point, and how to use the API's plugger provides.

1. clone this repo `git clone git@github.com:toejough/plugger.git`
1. cd in `cd plugger`
1. install the example packages `pip install example_plugins/*`
1. launch the interactive python shell `python`
1. import `foo` and `plugger`
    ```
    >>> import foo
    >>> import plugger
    ```
1. load all the plugins on the system that implement the `foo.Base` interface
    ```
    >>> all_bases = plugger.load_all_plugins_for(foo.Base)
    >>> all_bases
    [<class 'other.Bar'>, <class 'foo.Bar'>]
    >>> all_bases[0]().bar()
    'other bar'
    >>> all_bases[1]().bar()
    'foo bar'
    ```
1. load just the best plugin (by default, the external plugin)
    ```
    >>> best = plugger.load_best_plugin_for(foo.Base)
    >>> best
    <class 'other.Bar'>
    >>> bar = best()
    >>> bar
    <other.Bar object at 0x10c49dc18>
    >>> bar.bar()
    'other bar'
    ```
1. get the entry points for `foo.Base`
    ```
    >>> entry_points = plugger.get_entry_points(group='foo', name='Base')
    >>> entry_points
    [other:foo:Base (0.1.0), foo:foo:Base (0.1.0)]
    ```
1. load a plugin from an entry point
    ```
    >>> other_entry_point = entry_points[0]
    >>> other_entry_point
    other:foo:Base (0.1.0)
    >>> OtherBar = other_entry_point.load()
    >>> OtherBar
    <class 'other.Bar'>
    >>> other_bar = OtherBar()
    >>> other_bar
    <other.Bar object at 0x10c49df28>
    >>> other_bar.bar()
    'other bar'
    ```
1. get all installed entry points
    ```
    >>> plugger.get_entry_points()
    [wheel:console_scripts:wheel (0.30.0), wheel:distutils.commands:bdist_wheel (0.30.0), vulture:console_scripts:vulture (0.26), twine:console_scripts:twine (1.9.1), twine:twine.registered_commands:register (1.9.1), twine:twine.registered_commands:upload (1.9.1), ...
    ```

<a name='docs' />

# API Docs

* [EntryPoint](entrypoint) class
* [load_best_plugin_for](load-best) function
* [load_all_plugins_for](load-all) function
* [get_entry_points](get-eps) function

<a name='entrypoint' />

## class: `EntryPoint`

Entry point object.

Wraps a `pkg_resources.EntryPoint` with a cleaner API.
The original entry point is available via the `raw` property.

This object should not be instantiated directly by users.  Use the
`get_entry_points` function instead.

```python
def __init__(
    self, *,
    raw_entry_point: pkg_resources.EntryPoint,
    group: str,
) -> None:
```

Parameters:

* `raw_entry_point` - the raw entry point to wrap
* `group` - the group name the entry point was defined under

### property: `raw`

The raw entry point object being wrapped.

If using the default `discover` function passed to `get_entry_points`, this
object will currently either be `None` or `pkg_resources.EntryPoint`.

Note that no guarantees are made about this object.  This is provided
in case you know what is being wrapped, and you want to access it directly
in order to access some data which is not exposed by the EntryPoint
object, but the raw object is not defined or controlled by this project,
and its API is subject to arbitrary changes.  It is provided so that if
you want, you can get into the nitty gritty low level details, but use it
at your own risk.

### property: `package`

A `str` or `None`.  If `str`, it's the name of the package the entry point was defined in.

### property: `version`

A `str` or `None`.  If `str`, it's the version of the package the entry point was defined in.

### property: `group`

A `str`.  The group the entry point was defined in.

### property: `name`

A `str`.  The name the entry point was defined as.

### method: load

```python
def load() -> typing.Any
```

Load the plugin from the entry point.


<a name='get-eps' />

## function: `get_entry_points`

```python
def get_entry_points(
    *,
    name: typing.Optional[str]=None,
    group: typing.Optional[str]=None,
    discover: typing.Callable=_discover_entry_points,
) -> typing.List[EntryPoint]:
```

Get the entry points for the given filter options.

Parameters:

* `name` - the entry point name to filter by.  If none, no name filter will be used.
* `group` - the entry point group name to filter by  If none, no name filter will be used.
* `discover` - a function, taking no arguments, which returns EntryPoint objects for all
    the entry points on the system.  The default value is good enough for most cases,
    but this dependency is exposed for testing or advanced use.

Returns: a list of entry points that passed the filter.

If both name and group are left empty, all discovered entry points will be returned.

<a name='load-all' />

## function: `load_all_plugins_for`

```python
def load_all_plugins_for(
    interface: type, *,
    get_filtered: typing.Callable=get_entry_points,
) -> typing.List[type]:
```

Load the plugins for the given interface.

Parameters:
* `interface` - a class to use both as the source of correct group/name
    attributes for target plugins, but also as the base class for
    validating those plugins on load.
* `get_filtered` - a function, taking group and name arguments, and returning
    a list of EntryPoint objects that match.  The default value is good
    enough for most cases, but this dependency is exposed for testing or
    advanced use.

Returns a list of plugins which match the interface.

Plugins are found according to the following rules:
* in a group matching the root module the interface is defined in.
* has a name matching the name of the interface.
* is a subclass of the interface.

<a name='load-best' />

## function: `load_best_plugin_for`

```python
def load_best_plugin_for(
    interface: type, *,
    resolve_conflict: typing.Callable[..., type]=_get_external_plugin,
    load_all: typing.Callable=load_all_plugins_for,
) -> type:
```

Load the plugin for the given interface.

Parameters:

* `interface` - a class to use both as the source of correct group/name
    attributes for target plugins, but also as the base class for
    validating those plugins on load.
* `resolve_conflict` - a function, taking a list of plugins and an interface,
    and returning a single plugin.  The default value returns the only plugin
    defined in a different root module than the given interface, if there is
    only one.  Else it raises a RuntimeError.  This is exposed with the expectation
    that while this behavior is generally correct, there are going to be exceptions,
    and it may not always be sufficient, and callers will want to supply custom
    implementations for those cases.
* `load_all` - a function, taking an interface argument, and returning
    a list of EntryPoint objects that match.  The default value is good
    enough for most cases, but this dependency is exposed for testing or
    advanced use.

Returns the single plugin which matches the interface and survives conflict resolution.

Plugins are found according to the following rules:
* in a group matching the root module the interface is defined in.
* has a name matching the name of the interface.
* is a subclass of the interface.
* is chosen by the resolve_conflict function, if there are multiple matching plugins.

<a name='discussion' />

# Discussion

## Why does this library exist?

This library mainly exists because I've been trying different ways to decouple code and
manage things like dependency injection, and plugins keep popping up as a good route, and
I wanted something simple and flexible, and I didn't find that already out there.

## Why do the `load` functions take classes?

The `load` functions take classes for the sake of callsite simplicity (a single argument
that completely identifies plugin definitions) and plugin validation (plugins must be
subclasses of the single argument).

To be useful, a plugin's expected API's need to be documented.  Doing this via a base class
seems like an obvious choice.  Further, this allows us to use the root module the base class
is defined in for the entry point group, and the name of the base class for the entry point
name, and to validate the expected API has been met.

With `plugger`, we do:

```python
# awesome_app
UserInterface = plugger.load_best_plugin(awesome_app.plugin_interfaces.UserInterface)
```

That hides the complexity of:

* discovering the installed entry points
* filtering them by desired group and name
* resolving possible conflicts between a default implementation and an external plugin
* loading the plugin from the entry point
* validating the plugin meets a desired API

## Why validate that a plugin is a subclass?

AKA, why not use duck typing?  Validating the plugin is a subclass provides better safeguards
against incomplete or incorrectly implemented plugins at plugin load time.  EAFP (Easier to Ask
Forgiveness than Permission) is cool and all, but we're not expecting the availability of plugin
methods or attributes to change at runtime, so why not detect garbage inputs early?

If you feel like this is too limiting, you can still use this library and just use the `get_entry_points`
function instead.

## Why use setuptools entry points?

Plugger uses setuptools entry points to discover/define plugins because they exist.  Unless absolutely
necessary, I don't want to reinvent that wheel, especially because discovering and loading python functions
from installed packages is full of corner cases and pitfalls.

## `load_best_plugin_for` vs `load_all_plugins_for` with custom confilct resolver

To resolve many matched plugins down to a single "best" plugin with a custom conflict resolver,
you can either pass the resolver to `load_best_plugin_for` or just get all the plugins via
`load_all_plugins_for` and then pass those to a custom resolver in another step.

The first path has a slight edge in that the resolver will not be called if only one plugin is found,
whereas the second path requires you to either write that conditional into your resolver or handle it manually
yourself.  The first path is also a single call, vs at least two calls in your code for the second path.

The second path is the more flexible one, however - there's no call signature for your custom resolve to adhere
to, you can store the winner *and* the losers (perhaps for access later?), and you can perform the resolution
whenever you want, rather than requiring resolution immediately.

Which to choose ultimately comes down to your needs and personal preference.

## Why not use some other plugin manager?

### `pike`

Pike uses the filesystem and imported modules to identify plugin classes.  That requires you to know exactly where
your plugins are (filesystem method) or what modules they're in (imported modules method).  Those are both less flexible
methods than using setuptools entry points (which only require you to install the package to have them found).  The
filesystem method seems a bit insecure to me (the app loading the plugin can scan and load any class from anywhere it has access to
in your filesystem, without you knowing where it might be loading & executing code from).  Plugger is a bit more secure in
that the plugin must be declared, and the scan space is more restricted (installed packages in your environment rather than
the whole filesystem).  I may be missing something there, but it seems safer and more flexible to do things the Plugger way.

### `stevedore`

Stevedore uses setuptools for plugin identification, similarly to `plugger`.  I wrote `plugger` as a way to get the flexibility and
relative safety `stevedore` supplies with a simpler footprint/API.  Stevedore has 9 plugin manager classes for use in different plugin
scenarios, which allow different kinds of plugin discovery, loading, and verification for 3 distinct types of plugins `stevedore` defines.

I greatly appreciate their documentation's analysis of differing plugin types and uses and methodologies in use by different libraries to
define/discover/load plugins, but at the end of the day, `stevedore` seemed unnecessarily complex.  I wondered if maybe I was missing something,
and that's part of why I wrote `plugger`.  So far, my assessment stands.  That complexity isn't required to have a flexible plugin manager.

`stevedore` also explicitly takes an EAFP stance to plugin validation, opting to let you perform stronger validation if you want to as the caller.
Plugger takes the opposite approach - performing validation by default, and allowing you to bypass it if you don't want that.

## Loading arbitrary endpoints

It's fully expected that users will want to load arbitrary endpoints, and that's what the `get_entry_points` function is for.  Specify a group, or
a name, both, or none, perform any additional filtering/validation you want on the returned entry points, load them up, perform
any additional validation or filtering you want, and use them however you want.

Plugins loaded this way can be anything that can be specified as setuptools entry points, including modules, classes, functions, and objects.
