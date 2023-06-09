#!/usr/bin/env python3

import vcenter_api
import pmsg
import argparse
import os
import helper

def dprint(msg):
    if verbose:
        pmsg.debug(msg)

def check_vcenter_user(server, token, username, password):
    found_user = False
    if "@vsphere.local" in username:
        pmsg.warning("Users in @vsphere.local not manageable with the vCenter API.")
        return False

    json_obj = vcenter_api.api_get(server, "/api/appliance/local-accounts/" + username, token)
    if json_obj is not None:
        found_user = True
    if not found_user:
        if not dry_run:
            dprint ("Creating user: " + username)
            json_data = {"config": {"password": password, "roles": ["operator"] }, "username": username}
            rc = vcenter_api.api_post(server, "/api/appliance/local-accounts", token, json_data, 204)
            if rc:
                pmsg.green ("User " + username + " created.")
                found_user = True
            else:
                pmsg.fail ("I can't create the user: " + username + ". You may want to create it manually. Please check users/groups in vCenter and try again. See:")
                pmsg.underline ("https://docs.vmware.com/en/VMware-Tanzu-Kubernetes-Grid/1.5/vmware-tanzu-kubernetes-grid-15/GUID-mgmt-clusters-vsphere.html#vsphere-permissions")
        else:
            pmsg.dry_run ("Not creating user: " + username + ".")
    # Before returning, issue a govc command to make sure the user is in the Administrators group...
    if helper.run_a_command("govc sso.group.update -a " + username + "@local.os Administrators") != 0:
        pmsg.warning("Please check to see if the user: " + username + " is in the Administrators group.")
    return found_user


################################ Main #############################
# setup args...
help_text = "Create/Check vCenter users for TKGs install."

parser = argparse.ArgumentParser(description=help_text)
parser.add_argument('-d', '--dry_run', default=False, action='store_true', required=False, help='Just check things... do not make any changes.')
parser.add_argument('-v', '--verbose', default=False, action='store_true', required=False, help='Verbose mode.')
args = parser.parse_args()

# Making these three things global to script. Will not include these in arguments to functions.
verbose = args.verbose
dry_run = args.dry_run

server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
tkg_user = os.environ["tkg_user"]
tkg_user_password = os.environ["tkg_user_password"]
avi_vsphere_admin = os.environ["avi_vsphere_username"]
avi_vsphere_password = os.environ["avi_vsphere_password"]

os.environ["GOVC_URL"] = server
os.environ["GOVC_USERNAME"] = username
os.environ["GOVC_PASSWORD"] = password
os.environ["GOVC_INSECURE"] = "true"

token = vcenter_api.vcenter_login(server, username, password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)
dprint ("Session Token for REST API: " + token)

exit_code = 0

if check_vcenter_user(server, token, avi_vsphere_admin, avi_vsphere_password):
    pmsg.green("AVI vSphere user " + avi_vsphere_admin + " OK.")
else:
    pmsg.fail("AVI vSphere user " + avi_vsphere_admin + " not OK.")
    exit_code += 1

if check_vcenter_user(server, token, tkg_user, tkg_user_password):
    pmsg.green("TKG vSphere user " + tkg_user + " OK.")
else:
    pmsg.fail("TKG vSphere user " + tkg_user + " not OK.")
    exit_code += 1

exit(exit_code)
