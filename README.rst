================
logic-onboarding
================

This script configures cloud environment to connect to Log.ic.

It lets you choose a resource group for which it will configure all the NSGs to dump flow-logs, and create a
 configuration file with the configuration that is necessary to collect the flow-logs.


Installation
============

.. code-block:: bash

    python3 setup.py install

Usage
=====

.. code-block:: bash

    logic_onboarding [-h] [--version] cloud out-path

Important Notes
===============

* For Windows platform, the script must be run with PowerShell