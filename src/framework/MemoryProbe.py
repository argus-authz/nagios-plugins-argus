#!/usr/bin/env python
#############################################################################
# Copyright (c) Members of the EGEE Collaboration. 2006-2010.
# See http://www.eu-egee.org/partners/ for details on the copyright holders.
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
# Authors:
#     Joel Casutt     - joel.casutt@switch.ch
#############################################################################
'''
Created on 4/jan/2012

@author: joelcasutt
'''
from Probe import ArgusProbe
from AbstractProbe import ArgusAbstractProbe
from optparse import OptionParser, OptionGroup

__version__ = "1.0.0"

class ArgusMemoryProbe( ArgusProbe ):

    VERSION = __version__

    __warning_memory_treshold__ = 224.0 #MBytes
    __critical_memory_treshold__ = 256.0 #MBytes

    def __init__( self, serviceName, clientAuth ):
        super(ArgusMemoryProbe, self).__init__( serviceName, clientAuth )
        
    def createParser( self ):
        super(ArgusMemoryProbe, self).createParser()
        optionParser = self.optionParser
        memory_options = OptionGroup(optionParser, "Memory options", 
                                    "These options are used to set the nagios-limits for the memory.")
        memory_options.add_option("-w", 
                                  "--warning",
                                  dest = "mem_warn",
                                  help = "Memory usage warning threshold in MB. (default=%default).", 
                                  default = self.getWarningMemoryTreshold())

        memory_options.add_option("-c",
                                  "--critical",
                                  dest = "mem_crit",
                                  help = "Memory usage critical threshold in MB. (default=%default).", 
                                  default = self.getCriticalMemoryTreshold())
        optionParser.add_option_group(memory_options)
        self.optionParser = optionParser
        
    def getWarningMemoryTreshold( self ):
        return self.__warning_memory_treshold__
        
    def setWarningMemoryTreshold ( self, treshold ):
        self.__warning_memory_treshold__ = treshold
        
    def getCriticalMemoryTreshold( self ):
        return self.__critical_memory_treshold__
        
    def setCriticalMemoryTreshold( self, treshold ):
        self.__critical_memory_treshold__ = treshold
        
    def check( self ):
        status = self.getStatus()
        self.setWarningMemoryTreshold(self.options.mem_warn)
        self.setCriticalMemoryTreshold(self.options.mem_crit)
        __current_used_memory = int(status['UsedMemory'].split()[0]) / 1048576
        perfdata = " | MemoryUsage=" + str(__current_used_memory) + "MB;" + \
                   str(self.getWarningMemoryTreshold()) + ";" + str(self.getCriticalMemoryTreshold())
        if not status['Service'] == self.getServiceName():
            self.nagios_critical("the answering service is not a %s" % self.getServiceName())
        if int(self.getWarningMemoryTreshold())>=int(self.getCriticalMemoryTreshold()):
            self.nagios_critical("critical: the threshold for warning (%sMB) is equal or higher than the threshold for critical (%sMB)" 
                                 % (self.getWarningMemoryTreshold(), self.getCriticalMemoryTreshold()))
        if __current_used_memory <= int(self.getWarningMemoryTreshold()):
            self.nagios_ok(status['Service'] + " " + status['ServiceVersion'] + ": Used memory "  + \
                           str(__current_used_memory) + "MB" + perfdata)
        elif __current_used_memory <= int(self.getCriticalMemoryTreshold()) and \
             __current_used_memory > int(self.getWarningMemoryTreshold()):
            self.nagios_warning("warning: used memory (%dMB) higher than warning threshold (%sMB)" \
                                % (__current_used_memory, self.getWarningMemoryTreshold()))
        else:
            self.nagios_critical("critical: used memory (%dMB) higher than critical threshold (%sMB)" \
                                 % (__current_used_memory, self.getCriticalMemoryTreshold()))