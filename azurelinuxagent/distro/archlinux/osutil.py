#
# Copyright 2014 Microsoft Corporation
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
# Requires Python 2.4+ and Openssl 1.0+
#

import os
import re
import pwd
import shutil
import socket
import array
import struct
import fcntl
import time
import azurelinuxagent.logger as logger
import azurelinuxagent.utils.fileutil as fileutil
import azurelinuxagent.utils.shellutil as shellutil
import azurelinuxagent.utils.textutil as textutil
from azurelinuxagent.metadata import DISTRO_NAME, DISTRO_VERSION, DISTRO_FULL_NAME
from azurelinuxagent.distro.default.osutil import DefaultOSUtil


class ArchLinuxOSUtil(ArchLinuxOSUtil):
    def __init__(self):
        super(ArchLinuxOSUtil, self).__init__()
        self.dhclient_name = 'dhcpcd'

    def stop_dhcp_service(self):
        cmd = "systemctl stop {0}".format(self.dhclient_name)
        return shellutil.run(cmd, chk_err=False)

    def start_dhcp_service(self):
        cmd = "systemctl start {0}".format(self.dhclient_name)
        return shellutil.run(cmd, chk_err=False)

    def start_network(self) :
        return shellutil.run("systemctl start network", chk_err=False)

    def restart_ssh_service(self):
        return shellutil.run("systemctl restart sshd", chk_err=False)

    def stop_agent_service(self):
        return shellutil.run("systemctl stop waagent", chk_err=False)

    def start_agent_service(self):
        return shellutil.run("systemctl start waagent", chk_err=False)

    def register_agent_service(self):
        return shellutil.run("systemctl enable waagent", chk_err=False)

    def unregister_agent_service(self):
        return shellutil.run("systemctl disable waagent", chk_err=False)


