# coding: utf-8


"""Setup for plugger."""


# [ Imports ]
# [ -Python ]
from setuptools import setup, find_packages


# [ Main ]
setup(
    name='plugger',
    version='0.1.0',
    description='Plugger:  A simple setuptools-entrypoints-based plugin manager.',
    url='https://github.com/toejough/plugger',
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
    extras_require={
        'checkers': [
            'pylint', 'flake8', 'dodgy', 'vulture',
            'flake8-docstrings', 'mccabe', 'flake8-import-order',
            'pep8-naming', 'flake8-bugbear', 'flake8-tidy-imports',
            'flake8-quotes', 'flake8-commas',
            'flake8-comprehensions', 'flake8-todo', 'flake8-debugger',
            'flake8-blind-except', 'flake8-string-format',
            'flake8-tuple', 'flake8-builtins', 'flake8-coding', 'flake8-deprecated',
            'flake8-mutable', 'mypy',
        ],
        'testing': ['dado', 'pytest'],
    },
)
