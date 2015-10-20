#!/usr/bin/env python
#
# Windows Azure Linux Agent setup.py
#
# Copyright 2013 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
from azurelinuxagent.metadata import AGENT_NAME, AGENT_VERSION, \
                                     AGENT_DESCRIPTION, \
                                     DISTRO_NAME, DISTRO_VERSION, DISTRO_FULL_NAME

import azurelinuxagent.agent as agent
import setuptools
from setuptools import find_packages
from setuptools.command.install import install as  _install

root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)

def set_files(data_files, dest=None, src=None):
    data_files.append((dest, src))

def set_bin_files(data_files, dest="/usr/sbin", 
                  src=["bin/waagent", "bin/waagent2.0"]):
    data_files.append((dest, src))

def set_conf_files(data_files, dest="/etc", src=["config/waagent.conf"]):
    data_files.append((dest, src))

def set_logrotate_files(data_files, dest="/etc/logrotate.d", 
                        src=["config/waagent.logrotate"]):
    data_files.append((dest, src))

def set_sysv_files(data_files, dest="/etc/rc.d/init.d", src=["init/waagent"]):
    data_files.append((dest, src))

def set_systemd_files(data_files, dest="/lib/systemd/system", 
                      src=["init/waagent.service"]):
    data_files.append((dest, src))

def get_data_files(name, version, fullname):
    """
    Determine data_files according to distro name, version and init system type
    """
    data_files=[]

    if name == 'redhat' or name == 'centos':
        set_bin_files(data_files)
        set_conf_files(data_files)
        set_logrotate_files(data_files)
        if version >= "7.0":
            #redhat7.0+ uses systemd
            set_systemd_files(data_files, dest="/var/lib/systemd/system")
        else:
            set_sysv_files(data_files)

    elif name == 'coreos':
        set_bin_files(data_files, dest="/usr/share/oem/bin")
        set_conf_files(data_files, dest="/usr/share/oem")
        set_logrotate_files(data_files)
        set_files(data_files, dest="/usr/share/oem", 
                  src="init/coreos/cloud-config.yml")
    elif name == 'ubuntu':
        set_bin_files(data_files)
        set_conf_files(data_files, src=["config/ubuntu/waagent.conf"])
        set_logrotate_files(data_files)
        if version < "15.04":
            #Ubuntu15.04- uses upstart
            set_files(data_files, dest="/etc/init",
                      src=["init/ubuntu/walinuxagent.conf"])
            set_files(data_files, dest='/etc/default', 
                      src=['init/ubuntu/walinuxagent'])
        elif fullname == 'Snappy Ubuntu Core':
            set_files(data_files, dest="<TODO>", 
                      src=["init/ubuntu/snappy/walinuxagent.yml"])
        else:
            set_systemd_files(data_files, 
                              src=["init/ubuntu/walinuxagent.service"])
    elif name == 'suse':
        set_bin_files(data_files)
        set_conf_files(data_files, src=["config/suse/waagent.conf"])
        set_logrotate_files(data_files)
        if fullname == 'SUSE Linux Enterprise Server' and version >= '12' or \
                fullname == 'openSUSE' and version >= '13.2':
            set_systemd_files(data_files, dest='/var/lib/systemd/system')
        else:
            set_sysv_files(data_files, dest='/etc/init.d')
    else:
        #Use default setting
        set_bin_files(data_files)
        set_conf_files(data_files)
        set_logrotate_files(data_files)
        set_sysv_files(data_files)
    return data_files

class install(_install):
    user_options = _install.user_options + [
        # This will magically show up in member variable 'init_system'
        ('init-system=', None, 'deprecated, use --lnx-distro* instead'),
        ('lnx-distro=', None, 'target Linux distribution'),
        ('lnx-distro-version=', None, 'target Linux distribution version'),
        ('lnx-distro-fullname=', None, 'target Linux distribution full name'),
        ('register-service', None, 'register as startup service'),
        ('skip-data-files', None, 'skip data files installation'),
    ]

    def initialize_options(self):
        _install.initialize_options(self)
        self.init_system=None
        self.lnx_distro = DISTRO_NAME
        self.lnx_distro_version = DISTRO_VERSION
        self.lnx_distro_fullname = DISTRO_FULL_NAME
        self.register_service = False
        self.skip_data_files = False
        
    def finalize_options(self):
        _install.finalize_options(self)
        if self.skip_data_files:
            return

        if self.init_system is not None:
            print("WARNING: --init-system is deprecated,"
                  "use --lnx-distro* instead")
        data_files = get_data_files(self.lnx_distro, self.lnx_distro_version,
                                    self.lnx_distro_fullname)
        self.distribution.data_files = data_files
        self.distribution.reinitialize_command('install_data', True)

    def run(self):
        _install.run(self)
        if self.register_service:
            agent.register_service()

setuptools.setup(name=AGENT_NAME,
                 version=AGENT_VERSION,
                 long_description=AGENT_DESCRIPTION,
                 author= 'Yue Zhang, Stephen Zarkos, Eric Gable',
                 author_email = 'walinuxagent@microsoft.com',
                 platforms = 'Linux',
                 url='https://github.com/Azure/WALinuxAgent',
                 license = 'Apache License Version 2.0',
                 packages=find_packages(exclude=["tests"]),
                 cmdclass = {
                     'install': install
                 })
