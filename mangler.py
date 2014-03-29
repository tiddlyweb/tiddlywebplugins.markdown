"""
Adjusts module path to account for virtual namespace/namespace packages.

This is required primarily for testing.

The new setuptools allows implicit namespace packages so in order for us
to manipulate the paths associated with the namespace we need to load a
namespace first. Without it, a KeyError happens.
"""

import sys
import os

# Cause namespace to exist.
import tiddlywebplugins.utils


VIRTUAL_NAMESPACE = 'tiddlywebplugins'

if sys.version_info[0] <= 2:
    local_package = os.path.abspath(VIRTUAL_NAMESPACE)
    sys.modules[VIRTUAL_NAMESPACE].__dict__['__path__'].insert(0, local_package)
