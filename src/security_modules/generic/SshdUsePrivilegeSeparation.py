#!/usr/bin/env python
#
# Copyright (c) 2013-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

import re
import os
import sys
import shutil

sys.path.append("/usr/share/oslockdown")

import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software
import sb_utils.SELinux
import Ssh_Sshd_ConfigEditor

class SshdUsePrivilegeSeparation(Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor):
    """
    
    """

    def __init__(self):
        Ssh_Sshd_ConfigEditor.Ssh_Sshd_ConfigEditor.__init__(self)
        self.module_name    = "SshdUsePrivilegeSeparation"

        self.configfile = '/etc/ssh/sshd_config'
        self.settings = [ ['UsePrivilegeSeparation', 'yes',self._isEqualTo], 
                        ]

        self.logger = TCSLogger.TCSLogger.getInstance()

        if sb_utils.os.info.is_solaris() == True:
            self.package = 'SUNWsshdr'
        elif sb_utils.os.info.is_LikeSUSE() == True:
            self.package = 'openssh'
        else:
            self.package = 'openssh-server'

    def scan(self,options=None):
        return self.scanCfg(self.settings)
        
    def apply(self, options=None):
        return self.applyCfg(self.settings)
        
    def undo(self, changeRec=None):
        return self.undoCfg(changeRec)
      



if __name__ == '__main__':
    test = SshdUsePrivilegeSeparation()
    print test.scan()
