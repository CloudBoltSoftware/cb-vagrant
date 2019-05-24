
import os
import sys
import yaml
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
sys.path.append('/opt/cloudbolt')
django.setup()
from behavior_mapping.models import CustomFieldMapping
from resourcehandlers.vmware.models import VmwareDatastore, VmwareDisk, VmwareNetwork, VmwareServerInfo, VsphereOSBuildAttribute, VsphereResourceHandler
from jobs.models import Job
from resourcehandlers.models import ResourceHandler, ResourceNetwork, ResourceTechnology
from django.contrib.auth.models import User
from utilities.models import LDAPUtility, ConnectionInfo
from infrastructure.models import Environment, CustomField
from externalcontent.models import OSBuild, OSFamily
from accounts.models import Group, GroupType, GroupRoleMembership, Role, UserProfile
from accounts.factories import GroupFactory
from utilities.models import GlobalPreferences
from portals.models import PortalConfig
from cbhooks.models import RemoteScriptHook
from cbhooks.models import CloudBoltHook
from utilities.models import LDAPUtility, ConnectionInfo
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def add_parameter(object, parameter_name):
    field = CustomField.objects.get(name=parameter_name)
    object.custom_fields.add(field)
    object.save()

def create_remote_script(name, description, os_families, source_code_url, shared, execution_timeout, remove_after_run, groups, environments):
    script, status = RemoteScriptHook.objects.get_or_create(
        name=name,
        description=description,
        source_code_url=source_code_url,
        shared=shared,
        execution_timeout=execution_timeout,
        remove_after_run=remove_after_run)
    for family_name in os_families:
        family = OSFamily.objects.get(name=family_name)
        script.os_families.add(family.id)
        script.save()
    return status, script

def add_resource_handler_network(network_name, resource_handler_name):
    #get Resource Handler
    resource_handler = ResourceHandler.objects.get(name=resource_handler_name)
    # Setup a Network
    network, status = resource_handler.networks.get_or_create(
        name=network_name,
        network=network_name)
    resource_handler.vsphereresourcehandler.save()
    print(network)

def create_local_user(username, email, first_name, last_name, password, superuser, staffuser):
    new_local_user, status = User.objects.get_or_create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password)
    if superuser:
        new_local_user.is_superuser = True
        local_user_profile = new_local_user.userprofile
        local_user_profile.super_admin = True
        local_user_profile.save()
    if staffuser:
        new_local_user.is_staff = True
    new_local_user.save()
    return True, new_local_user


class CloudBoltSetupException(Exception):
    pass

def create_connectionInfo(name, ip, username, password, port, protocol):
    connection, status = ConnectionInfo.objects.get_or_create(
        name=name,
        ip=ip,
        username=username,
        password=password,
        port=port,
        protocol=protocol)
    connection.save()
    return connection, status

def create_group(name, description, parent, parameter_names=None):
    try:
        group_type = GroupType.objects.first()
        group = Group(
            name=name,
            description=description,
            parent=parent, type=group_type)
        group.save()
        # set permissions for group
        gp = GlobalPreferences.get()
        gp.group_type_order_filter.add(group.type)
        for profile in UserProfile.objects.all():
            GroupRoleMembership.objects.bulk_create(
                [GroupRoleMembership(group=group, profile=profile, role=role)
                 for role in Role.assignable_objects.all()])
        group.save()
        if parameter_names:
            for parameter_name in parameter_names:
                add_parameter(object=group, parameter_name=parameter_name)
        return True, group
    except:
        return False, name

def create_resource_handler(name, ip, technology, description, username, password, port, virtual_folder_path, network_names):
    # Setup a resource handler that connects to vCenter
    if technology == "vcenter":
        rh, status =  VsphereResourceHandler.objects.get_or_create(
            name=name,
            ip=ip,
            protocol='http',
            description=description,
            serviceaccount=username,
            servicepasswd=password,
            virtual_folder_path=virtual_folder_path,
            clone_tmpl_timeout=600,
            ignore_vm_folders='^(?!.*-[Vv][Aa][Gg][Rr][Aa][Nn][Tt]$).*$',
            resource_technology=ResourceTechnology.objects.get(
                name="VMware vCenter")
        )
        if status:
            for network_name in network_names:
                networks, _, _ = rh.discover_networks()
                for network in networks:
                    if network['name'] == network_name:
                        rh.add_network(**network)
            return True, rh
    raise CloudBoltSetupException(f"Technology Not Found {technology}")

def create_environment(resource_handler_name, environment_name, cluster_name, disk_type, data_store, network_names, parameter_names=None):
    # Set up an Environment that is linked to a vCenter Cluster
    resource_handler = ResourceHandler.objects.get(name=resource_handler_name)
    environment = resource_handler.vsphereresourcehandler.create_location_specific_env(
        location_name=cluster_name,
        env_name=environment_name,
        location_display=environment_name)
    environment.name = environment_name
    environment.vmware_disk_type = disk_type
    environment.vmware_datastore = VmwareDatastore.objects.get(name=data_store)
    for network_name in network_names:
        network = ResourceNetwork.objects.get(name=network_name)
        if network:
            environment.add_network(network)
        environment.save()
    if parameter_names:
        for parameter_name in parameter_names:
            add_parameter(object=environment, parameter_name=parameter_name)
    return True, environment

def create_os_build(name, family_name, environment_names=None):
    print('Creating OSBuild')
    os_family = OSFamily.objects.get(name=family_name)
    osbuild, status = OSBuild.objects.get_or_create(
        name=name,
        os_family_id=os_family.id
    )
    print("Adding OSBuild to Environments")
    if environment_names:
        for environment_name in environment_names:
            environment = Environment.objects.get(name=environment_name)
            osbuild.environments.add(environment)
            osbuild.save()
    print(osbuild)

def get_auth(username, password, domain=None):
    if domain:
        token_auth = {"username": username, "password": password, "domain": domain}
    else:
        token_auth = {"username": username, "password": password}
    get_token = requests.post(
        'https://localhost/api/v2/api-token-auth/',
        json=token_auth, verify=False,
        headers={'Content-Type': 'application/json'})
    token = json.loads(get_token.content)
    return token

def import_template(os_build, template_name, username, password, domain=None):
    token = get_auth(username, password, domain)
    url = 'https://localhost:443/api/v2/resource-handlers/1/import-template/'
    response = requests.post(url,
        data={
            'template':f"{template_name}",
            'os-build':f"{os_build}"
        },
        headers={
            'Authorization': "Bearer " + token["token"],
            'Content-Encoding': 'gzip',
            'Accept': 'Application/json'
        },
        verify=False,
        allow_redirects=False
        )
    if response.status_code == 200:
        status = True
    else:
        status = False
    return status, response

def set_template_creds(template_name, template_username, template_password, username, password, domain=None, template_sshkey=None):
    token = get_auth(username, password, domain)
    url = 'https://localhost/api/v2/resource-handlers/1/set-template-creds/'
    data = {
        'template': f"{template_name}",
        'user-name': f"{template_username}",
        'password': f"{template_password}"
    }
    response = requests.post(
        url,
        data=data,
        headers={
            'Authorization': "Bearer " + token["token"],
            'Content-Encoding': 'gzip',
            'Accept': 'Application/json'
        },
        verify=False,
        allow_redirects=False
        )
    if response.status_code == 200:
        status = True
    else:
        status = False
    return status, response

def create_blueprint(file_name, username, password, file_path, domain=None):
    files = {"file": (file_name, open(file_path+'/'+file_name, 'rb'))}
    token = get_auth(username, password, domain)
    url = 'https://localhost/api/v2/blueprints/import/'
    response = requests.post(url,
        files=files,
        headers={
            'Authorization': "Bearer " + token["token"],
            'Content-Encoding': 'gzip',
            'Accept': 'Application/json'
        },
        verify=False,
        allow_redirects=False
        )
    if response.status_code == 200:
        status = True
    else:
        status = False
    return status, response

print("Creating local User")
status, new_local_user = create_local_user(
    username='vagrant',
    email="vagrant@cloudbolt.io",
    first_name='vagrant',
    last_name='vagrant',
    password='pbkdf2_sha256$36000$y6HhbsgAhKdh$I8Idg+mUlnB3Svxt3Qp3bhmWF8/8/ZbkAy2z93Xbl2k=',
    staffuser=True,
    superuser=True)
print(f"Created user {new_local_user}")

print("Creating Resource Handler")
status, rh = create_resource_handler(
    technology='vcenter',
    name=os.environ['RESOURCEHANDLERNAME'],
    ip=os.environ['RESOURCEHANDLERIP'],
    description=os.environ['RESOURCEHANDLERDESCRIPTION'],
    username=os.environ['RESOURCEHANDLERUSERNAME'],
    password=os.environ['RESOURCEHANDLERPASSWORD'],
    port=443,
    network_names=os.environ['RESOURCEHANDLERNETWORKNAMES'].replace(', ', ',').split(','),
    virtual_folder_path=os.environ['RESOURCEHANDLERVIRTUALFOLDERPATH']
)
print(f'created Resource Handler {rh.name}')

print("Creating Connection INFO")
create_connectionInfo(
    name='Source Control Repository',
    ip='github.com',
    username=os.environ['GITHUBUSERNAME'],
    password=os.environ['GITHUBPASSWORD'],
    port=443,
    protocol="HTTPS")
print("Added Connection info")

status, group = create_group(
    name="vagrant",
    description="Vagrant Group for Quick Test Purposes",
    parent=None,
    parameter_names=None)
print("Created Vagrant group")

status, environment = create_environment(
    resource_handler_name=os.environ['RESOURCEHANDLERNAME'],
    environment_name=os.environ['ENVIRONMENTNAME'],
    cluster_name=os.environ['ENVIRONMENTCLUSTERNAME'],
    disk_type='Thin Provision',
    data_store=os.environ['ENVIRONMENTDATASTORE'],
    network_names=os.environ['RESOURCEHANDLERNETWORKNAMES'].replace(', ','').split(',')
)
print(f"Created Environment {environment.name}")

print("Importing Template")
status, response = import_template(
    template_name=os.environ['TEMPLATENAME'],
    os_build=os.environ['OSBUILDNAME'],
    username='vagrant',
    password='cbvagrant',
)
print(f"Template Imported {status} , response: {response}")

print("Creating OSBUILD")
create_os_build(
    name=os.environ['OSBUILDNAME'],
    family_name=os.environ['OSBUILDFAMILY'],
    environment_names=os.environ['OSBUILDENVIRONMENTS'].replace(', ', '').split(',')
)
print("OSBUILD CREATED")

print("Imported template")
status, response = set_template_creds(
    template_name=os.environ['TEMPLATENAME'],
    template_username=os.environ['TEMPLATEUSERNAME'],
    template_password='vagrant',
    username='vagrant',
    password='cbvagrant'
)
print("set Creds on Template")
print(f"status: {status}  response {response} reason: {response.reason}")

print("Creating Blueprint")
status, response = create_blueprint(
    file_name='vagrant_server.zip',
    username='vagrant',
    password='cbvagrant',
    file_path='/vagrant')
print(f"status: {status}  response {response} reason: {response.reason}")
