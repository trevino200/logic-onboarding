==================
Log.ic on-boarding
==================

The onboarding will connect each NSG in the selected ResourceGroup in each region to a StorageAccount.
The script generates an output file which containing subscription id, resource group, storage_account name and key with a list of NSGs. When there is more than 1 storage account, the output file will be generated with a list of Storage accouns, each with it’s own NSGs.
 
Prerequisites
=============

Before running the script make sure that:

* AZ client is installed (Azure command line)
* Python3.5 and above is installed
* Each location of NSGs under the ResourceGroup that should be on-boarded to Logic has a 
  StorageAccount (Highly recommended that the StorageAccount is dedicated to flow logs).
* Make sure that your Azure subscription has the Microsoft.Insights enabled:
  1. go to the Azure Portal
  2. Subscriptions
  3. Click your subscription name
  4. Find `microsoft.insights` in the list 
  5. Make sure that it is enabled, if not click it and then click "Register"

 
  Keep in mind that flow logs must be sent to StorageAccount in the same location as the 
  Resource Group.



Installation
============

Download the script here:

 
https://github.com/dome9/logic-onboarding/releases/download/0.1/logic_onboarding-0.1-py2.py3-none-any.whl


Usage
=====

Running the script

* Run command **az login** in terminal/cmd (this is an Azure CLI command)
* Install the whl with command: **pip3 install logic_onboarding-0.1-py2.py3-none-any.whl**
* Run the command: **logic_onboarding azure output.json**

  Input is required as the script run in order to configure the NSG flow logs. Each step will give the relevant options. The reply should be numeric only.

  a. Select a subscription
  b. Authenticate connection to Azure account - connect to the URL given and input the code.
  c. Select a resource group
  d. For each location that has NSGs, select a correlating StorageAccount. If a dedicated StorageAccounts for the ResourceGroup does not exist, create one and re-run the script. 
 
 
After the script finishes, and output.json file is created AND the NSGs in the ResourceGroup will publish flow logs to StorageAccounts.
Send Dome9 the output.json file.
