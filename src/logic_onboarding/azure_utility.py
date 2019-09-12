import errno
import json
import os
import subprocess
from time import sleep

import adal
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from msrestazure.azure_active_directory import AADTokenCredentials

AZURE_DIRECTORY_NAME = ".azure"
PROFILE_FILE_NAME = "azureProfile.json"
STORAGE_ACCOUNTS_KEY = 'key1'

AUTO_GENERATED_STORAGE_ACCOUNT_SUFFIX = "_flow_logs"

profile_path = os.path.join(os.path.expanduser("~"), AZURE_DIRECTORY_NAME, PROFILE_FILE_NAME)


def choose(ls, resource_type, name_extactor=lambda x: x, additional_description=None):
    if len(ls) > 0:
        if additional_description: print(additional_description)
        print("\nchoose `" + resource_type + "` to activate flow-logs on:")
        for i, item in enumerate(ls, 1):
            print("(%d)\t %s" % (i, name_extactor(item)))
        option = ls[int(input("Input: ")) - 1]
        print("You Chose: " + name_extactor(option) + "\n")
        return option
    else:
        print("no `" + resource_type + "` configured, please configure and re-run the script")
        exit(1)


def get_credentials():
    # EAFP check Azure CLI is installed
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.call(["az", "--help"], stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("Azure CLI is not installed, please install it."
                  " https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest")
            exit(1)
        else:
            print(e)
            exit(1)

    if os.path.exists(profile_path):
        with open(profile_path, 'rb') as profile_file:
            profile = json.load(profile_file)
            if 'subscriptions' in profile:
                subscription = choose(profile['subscriptions'], "account", lambda x: x['name'])
                return subscription['id'], subscription['tenantId']
    print(
        "azure connection files were not initialized, please run `az login` and then run the onboarding script again")
    exit(1)


def authenticate_device_code(tenant_id):
    """
    Authenticate the end-user using device auth.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    authority_uri = authority_host_uri + '/' + tenant_id
    resource_uri = 'https://management.core.windows.net/'
    client_id = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    code = context.acquire_user_code(resource_uri, client_id)
    print(code['message'])
    mgmt_token = context.acquire_token_with_device_code(resource_uri, code, client_id)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials


def configure():
    subscription_id, tenant_id = get_credentials()
    credentials = authenticate_device_code(tenant_id)
    resource_client = ResourceManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    storage_client = StorageManagementClient(credentials, subscription_id)
    rg = choose(list(resource_client.resource_groups.list()), "resource group", lambda x: x.name)

    storage_accounts = {}

    print("Configuring flow logs for all network security groups in resource group " + rg.name)
    nsgs = list(network_client.network_security_groups.list(rg.name))
    for nsg in nsgs:
        nw_name = "NetworkWatcher_" + nsg.location
        if nsg.location not in storage_accounts:
            network_client.network_watchers.create_or_update("NetworkWatcherRG", nw_name, {
                "enabled": "true",
                "location": nsg.location
            })
            sleep(3)  # waiting for resource to be truly created
            print("enabled default network watcher for " + nsg.location + " location")

            available_storage_accounts = [sa for sa in storage_client.storage_accounts.list_by_resource_group(rg.name)
                                          if sa.location == nsg.location]
            storage_accounts[nsg.location] = choose(available_storage_accounts,
                                                    "storage account for " + nsg.location + " location",
                                                    lambda x: x.name,
                                                    "It is highly recommended to have a dedicated storage account for Flow-Logs, "
                                                    "if you dont have any, please configure one in the Azure Portal and re-run the script to choose it")
        network_client.network_watchers.set_flow_log_configuration(
            "NetworkWatcherRG", nw_name, {
                "enabled": "true",
                "target_resource_id": nsg.id,
                "storage_id": storage_accounts[nsg.location].id,
                "format": {
                    "type": "JSON",
                    "version": "2"
                }
            })
        print("enabled flow-logs for nsg " + nsg.name)
    return {
        "subscription_id": subscription_id,
        "resource_group": rg.name,
        "storage_accounts": [{
            "name": sa.name,
            "key": next(filter(lambda x: x.key_name == STORAGE_ACCOUNTS_KEY,
                               storage_client.storage_accounts.list_keys(rg.name, sa.name).keys)).value,
            "network_security_groups": [nsg.name for nsg in nsgs if nsg.location == sa.location]
        } for sa in storage_accounts.values()]
    }


def run(out_path):
    onboarding_json = configure()
    with open(out_path, 'w') as out_file:
        json.dump(onboarding_json, out_file)
        print("saved log.ic configuration file on " + out_path)
