================
logic-onboarding
================

The script connects each NSG in the selected ResourceGroup to a StorageAccount, from which we read the flow log files.


Prerequisites
=============

Before running the script make sure that:

* client is installed (Azure command line)
* and above is installed
* run command “az login” in terminal/cmd
* Each location with NSGs under the ResourceGroup that should be on-boarded to Logic has a StorageAccount (Highly recommended that the StorageAccount is dedicated to flow logs). Keep in mind that flow logs must be sent to Storage Account in the same location as the Resource Group.


Installation
============

.. code-block:: pip3 install logic_onboarding-0.1-py2.py3-none-any.whl


Usage
=====

Install the whl with command: pip3 install logic_onboarding-0.1-py2.py3-none-any.whl
Run the command: logic_onboarding azure output.json
Input is required as the script run in order to configure the NSG flow logs. Each step will give the relevant options. The reply should be numeric only.

1. Select a subscription
2. Authenticate connection to Azure account - connect to the URL given and input the code.
3. Select a resource group
4. For each location that has NSGs, select a correlating StorageAccount. If a dedicated StorageAccounts for the ResourceGroup does not exist, create one and re-run the script.

After the script finishes, and output.json file is created AND the NSGs in the ResourceGroup will publish flow logs to StorageAccounts.
Send Dome9 the output.json file.


Important Notes
===============

* For Windows platform, the script must be run with PowerShell
