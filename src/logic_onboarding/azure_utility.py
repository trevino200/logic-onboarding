import errno
import json
import os
import subprocess

import adal
from msrestazure.azure_active_directory import AADTokenCredentials
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient


AZURE_DIRECTORY_NAME = ".azure"
PROFILE_FILE_NAME = "azureProfile.json"

AUTO_GENERATED_STORAGE_ACCOUNT_SUFFIX = "_flow_logs"

profile_path = os.path.join(os.path.expanduser("~"), AZURE_DIRECTORY_NAME, PROFILE_FILE_NAME)


def choose(ls, text, name_extactor = lambda x: x):
    print("\n\n" + text + "\n")
    for i, item in enumerate(ls, 1):
        print("(%d)\t %s" % (i, name_extactor(item)))
    return ls[int(input("\ninput: ")) - 1]

def get_credentials():
    # EAFP check Azure CLI is installed
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.call(["az", "--help"], stdout=FNULL, stderr=subprocess.STDOUT)
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
            subscription = choose(profile['subscriptions'], "Please choose the account that you want to configure:", lambda x: x['name'])
            return subscription['id'], subscription['tenantId']
    else:
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


def configure(container_name):
    subscription_id, tenant_id = get_credentials()
    credentials = authenticate_device_code(tenant_id)
    resource_client = ResourceManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    storage_client = StorageManagementClient(credentials, subscription_id)
    rg = choose(list(resource_client.resource_groups.list()), "Choose the resource group to activate flow-logs on:", lambda x: x.name)
    nsgs = [nsg for nsg in network_client.network_security_groups.list(rg.name)]
    if len(nsgs) > 0:
        storage_account = choose(list(storage_client.storage_accounts.list_by_resource_group(rg.name)), "Choose the storage account to export logs to:", lambda x: x.name)
        nsg = choose(list(nsgs), "Choose the nsg to activate flow-logs on:", lambda x: x.name)
        # CREATE NETWORK WATCHER??
        network_client.network_watchers.set_flow_log_configuration(
            rg.name, "logic_flow_logs_" + rg.name, {
                "enabled": "true",
                "target_resource_id": nsg.id,
                "storage_id": storage_account.id
                # "format": {"value": "JSON"},
                # "log-version": {"value": "2"}
            })
    else:
        print("No storage accounts configured for resource group,"
              " please configure one manually so you will be able to dump the logs there.")


if __name__ == "__main__":
    configure("kaki")