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
from Status import ArgusStatus

__version__ = "1.0.0"

class ArgusCurrentStatus( ArgusStatus ):

    def __init__( self, clientAuth ):
        super(ArgusCurrentStatus, self).__init__(clientAuth)
        
    def getStatus( self, CURRENT_SERVICE ):
        d = ArgusStatus.getStatus( self )
        if not d['Service'] == CURRENT_SERVICE:
            super(ArgusCurrentStatus, self).nagios_critical("the answering service is not a %s" % CURRENT_SERVICE)
        if d['Status'] == 'OK':
            super(ArgusCurrentStatus, self).nagios_ok(d['Service'] + ": " + d['Status'] + " (Started: " + d['ServiceStartupTime'] + ")")
        else:
            super(ArgusCurrentStatus, self).nagios_critical("\"Status: OK\" not found.")