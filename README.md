<p align="center">
  <img src="https://www.cloudbolt.io/wp-content/uploads/CloudBolt_hlogo_blue_cloud_w_text-small.png" alt="CloudBolt">
</p>

Try out CloudBolt in Vagrant!

## Getting Started

### Basic Installation

* Clone the repository
* `vagrant up` in repository dirctory 
* Access CloudBolt via https://192.168.2.2
* Request a license from https://www.cloudbolt.io/license-request

### Updated CloudBolt

The version of CloudBolt in the Vagrant box is likely out of date so we update
it during provisioning. Once CloudBolt is up and running, ssh into the CloudBolt
VM, download the upgrader, and install the latest version with:

```
$ wget http://downloads.cloudbolt.io/cloudbolt-upgrader-latest.tgz
$ tar xvf cloudbolt-upgrader-latest.tgz
$ cd cloudbolt_upgrader_*
$ ./upgrade_cloudbolt.sh
```

## Setup your variables for configuring instance
```
export RESOURCEHANDLERNAME='vCenter Dev'
export RESOURCEHANDLERIP='vcenter.domain.com'
export RESOURCEHANDLERDESCRIPTION='Dev Vcenter'
export RESOURCEHANDLERUSERNAME='ldap@domain'
export RESOURCEHANDLERPASSWORD='resourcehandlerpassword'
export RESOURCEHANDLERNETWORKNAMES='Name of Network'
export RESOURCEHANDLERVIRTUALFOLDERPATH='vagrant/{{ group }}-vagrant'
export ENVIRONMENTNAME='Dev'
export ENVIRONMENTCLUSTERNAME='vcenter cluster'
export ENVIRONMENTDATASTORE='vcenter datastore'
export TEMPLATENAME='myawesomewindowstemplate'
export OSBUILDNAME='Windows'
export OSBUILDFAMILY='Windows'
export OSBUILDENVIRONMENTS='Dev'
export TEMPLATEUSERNAME='Administrator'
export GITHUBUSERNAME='username'
export GITHUBPASSWORD='password'
export BLUEPRINTFILE='myfile.zip'
```

### Place License.bin file in same directory as Vagrantfile.
