# -*- coding: utf-8 -*-
"""
    Setup file for logic_onboarding.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 3.2.1.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

from pkg_resources import VersionConflict, require
from setuptools import setup

try:
    require('setuptools>=38.3')
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)


if __name__ == "__main__":
    setup(use_pyscaffold=True,
          install_requires=[
              "azure-mgmt-network",
              "azure-mgmt-resource",
              "azure-mgmt-storage==4.0.0",
              "msrestazure",
              "adal"
          ])