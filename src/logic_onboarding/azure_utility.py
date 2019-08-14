import errno
import json
import os
import subprocess

import adal
from msrestazure.azure_active_directory import AADTokenCredentials
from azure.mgmt.network import NetworkManagementClient

AZURE_DIRECTORY_NAME = ".azure"
PROFILE_FILE_NAME = "azureProfile.json"

profile_path = os.path.join(os.path.expanduser("~"), AZURE_DIRECTORY_NAME, PROFILE_FILE_NAME)


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
            print("Please choose the account that you want to configure:\n")
            for i, sub in enumerate(profile['subscriptions'], 1):
                print("(%d)\t %s" % (i, sub['name']))
            option = input("\nAccount no.: ")
            subscription = profile['subscriptions'][int(option) - 1]
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


if __name__ == "__main__":
    subscription_id, tenant_id = get_credentials()
    network_client = NetworkManagementClient(authenticate_device_code(tenant_id), subscription_id)