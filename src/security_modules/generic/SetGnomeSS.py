#!/usr/bin/python
#
# Copyright (c) 2007-2014 Forcepoint LLC.
# This file is released under the GPLv3 license.  
# See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
# or visit https://www.gnu.org/licenses/gpl.html instead.
#

# This module needs to be simplified!!
#
# This module establishes "mandatory" settings in the Gnome
# manager's registry. Which means that normal users can't
# change them. This is done by using the gconftool-2 command
# against the primary register /etc/gconf/gconf.xml.mandatory.
#
#

import os
import sys

sys.path.append('/usr/share/oslockdown')
import tcs_utils
import TCSLogger
import sb_utils.os.info
import sb_utils.os.software


##############################################################################
class SetGnomeSS:

    def __init__(self):
        self.module_name = 'SetGnomeSS'

        try:
            self.logger = TCSLogger.TCSLogger.getInstance(6) 
        except TCSLogger.SingletonException:
            self.logger = TCSLogger.TCSLogger.getInstance() 

        self.CONFIG_SOURCE = ""

        for cfg in [ '/etc/gconf/gconf.xml.mandatory', '/etc/opt/gnome/gconf/gconf.xml.mandatory']: 
            if os.path.exists(cfg):
                self.CONFIG_SOURCE = cfg
                break

        self.CMD1 = "--direct --config-source "\
               "xml:readwrite:%s --type bool "\
               " --set /apps/gnome-screensaver/idle_activation_enabled true" % self.CONFIG_SOURCE

        self.CMD2 = "--direct --config-source "\
               "xml:readwrite:%s --type bool "\
               "--set /apps/gnome-screensaver/lock_enabled true" % self.CONFIG_SOURCE

        self.CMD3 = "--direct  --config-source "\
               "xml:readwrite:%s --type string "\
               "--set /apps/gnome-screensaver/mode blank-only" % self.CONFIG_SOURCE

        self.CMD4 = "--direct --config-source "\
               "xml:readwrite:%s --type int "\
               "--set /apps/gnome-screensaver/idle_delay " % self.CONFIG_SOURCE

        if os.path.isfile('/usr/bin/gconftool-2'):
            self.__cmd     = "/usr/bin/gconftool-2"
        else:
            # Novell SUSE 10 puts it in an odd location
            self.__cmd     = "/opt/gnome/bin/gconftool-2"

        self.__cfg_src = "--direct --config-source xml:readwrite:%s" % self.CONFIG_SOURCE

        self.__settings = ('/apps/gnome-screensaver/idle_activation_enabled,true,bool',
                           '/apps/gnome-screensaver/lock_enabled,true,bool',
                           '/apps/gnome-screensaver/mode,blank-only,string',
                           '/apps/gnome-screensaver/idle_delay,OPTION,int' )

    ##########################################################################
    def validate_input(self, optionDict):
        """Checks to see if a numeric value was supplied for \
        the timeout value"""
        if not optionDict or not 'gnomeSaverActivate' in optionDict:
            return 1
        try:
            value = int(optionDict['gnomeSaverActivate'])
        except ValueError:
            return 1
        if value == 0:
            return 1
        return 0

    ##########################################################################
    def scan(self, optionDict=None):
 
        messages = {'messages': []}

        if sb_utils.os.info.is_solaris() == True:
            pname = "SUNWgnome-config"
        else:
            if sb_utils.os.info.is_LikeSUSE() == True:
                pname = "gconf2"
            else:
                pname = "GConf2"

        results =  sb_utils.os.software.is_installed(pkgname=pname)
        if results == False:
            msg = "%s does not appear to be installed on the system" % pname
            self.logger.warn(self.module_name, 'Not Applicable: ' + msg)
            raise tcs_utils.ScanNotApplicable('%s %s' % (self.module_name, msg))
        else:
            msg = "%s package is installed" % pname
            messages['messages'].append("Okay: %s" % msg)
            self.logger.info(self.module_name, msg)

        if not os.path.isfile(self.__cmd):
            msg = "%s not found" % self.__cmd
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        else:
            msg = "Okay: Found %s utility" % self.__cmd
            messages['messages'].append(msg)

        failure_flag = False
        if self.validate_input(optionDict):
            msg = 'Invalid option value was supplied.'
            self.logger.error(self.module_name, 'Scan Error: ' + msg)
            raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))
        option = optionDict['gnomeSaverActivate']
        for line in self.__settings:
            optkey, optval, opttype = line.split(',')
            getconf = "%s %s --get %s 2>&1" % (self.__cmd, self.__cfg_src, optkey)

            msg = "Executing: %s" % getconf
            self.logger.info(self.module_name, msg)
         
            try:
                pipe = os.popen(getconf)
                curval = pipe.readlines()
            except (OSError, IOError), err:
                msg = "Failed to execute %s (%s)" % (getconf, err)
                self.logger.error(self.module_name, "Scan Error: " + msg)
                raise tcs_utils.ScanError('%s %s' % (self.module_name, msg))

            msg = "Executed: %s" % getconf
            self.logger.info(self.module_name, msg)

            for retval in curval:
                retval = retval.rstrip('\n')
                if retval.startswith('Resolved address'):
                    continue

                if retval.startswith('No value'):
                    msg = "gconftool-2 reports: %s" % retval
                    self.logger.info(self.module_name, msg)
                    failure_flag = True
                    continue

                if optval  == 'OPTION':
                    optval = option

                if retval != optval:
                    msg = "gconftool-2 reports: %s; expected %s" % (retval, optval)
                    messages['messages'].append("Fail: %s" % msg)
                    self.logger.info(self.module_name, msg)
                    failure_flag = True

            pipe.close()

        if failure_flag == True:
            return False, 'Mandatory Gnome screensaver not set correctly', messages

        return True, '', messages

    ##########################################################################
    def apply(self, optionDict=None):

        messages = {'messages': []}

        
        result, reason, msg = self.scan(optionDict)
        if result == True:
            return False, 'none', {}

        option = optionDict['gnomeSaverActivate']
        old_state = {}
        for line in self.__settings:
            optkey, optval, opttype = line.split(',')
            getconf = "%s %s --get %s 2>&1" % (self.__cmd, self.__cfg_src, optkey)

            msg = "Executing: %s" % getconf
            self.logger.info(self.module_name, msg)
         
            pipe = os.popen(getconf)
            curval = pipe.readlines()

            for retval in curval:
                retval = retval.rstrip('\n')
                if retval.startswith('Resolved address'):
                    continue

                if retval.startswith('No value'):
                    msg = "gconftool-2 reports: %s" % retval
                    self.logger.info(self.module_name, msg)
                    old_state[optkey.split('/')[-1]] = ''
                else:
                    old_state[optkey.split('/')[-1]] = retval

            pipe.close()

        change_record = old_state

        setlist = (self.CMD1, self.CMD2, self.CMD3, self.CMD4)
        for cmd in setlist:
            if cmd == self.CMD4:
                cmd = str(self.CMD4 + str(option))

            cmd = "%s %s" % (self.__cmd, cmd)
            results = tcs_utils.tcs_run_cmd(cmd, True) 
            if results[0] != 0:
                msg = "Failed to execute: %s (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = "Executed: %s" % (cmd)
                messages['messages'].append(msg)
                self.logger.notice(self.module_name, 'Apply Performed: ' + msg)

        msg = 'Mandatory Screen locking security settings now configured.'
        self.logger.notice(self.module_name, 'Apply performed: ' + msg)
        return True, str(change_record), messages

    ##########################################################################
    def undo(self, change_record):

        if not change_record:
            msg = "Unable to perform undo operation without change record."
            self.logger.notice(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        try:
            change_record = eval(change_record)
        except:
            msg = "Malformed change record, unable to convert to JSON "\
                  "object: %s" % change_record
            self.logger.notice(self.module_name, 'Undo Error: ' + msg)
            raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))

        base_cmd = "%s --direct --config-source "\
                   "xml:readwrite:%s " % (self.__cmd, self.CONFIG_SOURCE)
 
        app_path = "/apps/gnome-screensaver"

        temp_dict = {}
        for line in self.__settings:
            optkey, optval, opttype = line.split(',')
            temp_dict[optkey.split('/')[-1]] = opttype
            

        for line in change_record.keys():
            if not temp_dict.has_key(line):
                continue

            if change_record[line] == '':
                cmd = "%s --unset %s/%s %s " % \
                    (base_cmd, app_path, line, change_record[line])
            else:
                cmd = "%s --type %s --set %s/%s %s" % \
                    (base_cmd, temp_dict[line], app_path, line, change_record[line])


            results = tcs_utils.tcs_run_cmd(cmd, True) 
            if results[0] != 0:
                msg = "Failed to execute: %s (%s)" % (cmd, results[2])
                self.logger.error(self.module_name, "Undo Error: " + msg)
                raise tcs_utils.ActionError('%s %s' % (self.module_name, msg))
            else:
                msg = "Executed: %s" % (cmd)
                self.logger.notice(self.module_name, 'Undo Performed: ' + msg)

        msg = 'Gnome Screen Saver settings restored.'
        self.logger.notice(self.module_name, 'Undo Performed: ' + msg)
        return True, ''

