# coding: utf-8


"""Setup for foo."""


# [ Imports ]
# [ -Python ]
from setuptools import setup, find_packages


# [ Main ]
setup(
    name='foo',
    version='0.1.0',
    description='Foo:  An example Plugin.',
    url='https://github.com/toejough/not-real',
    author='toejough',
    author_email='toejough@gmail.com',
    classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: Apache Software License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
    ],
    keywords="setuptools entrypoint plugin",
    packages=find_packages(),
    entry_points={
        'foo': [
            'Base = foo:Bar',
        ],
        'food': [
            'Base = foo:Bar',
        ],
    },
)
