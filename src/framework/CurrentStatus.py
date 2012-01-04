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
#     Andrea Ceccanti - andrea.ceccanti@cnaf.infn.it
#     Joel Casutt     - joel.casutt@switch.ch
#############################################################################
'''
Created on 9/dez/2011

@author: andreaceccanti
@author: joelcasutt
'''
from Status import ArgusStatus
import signal

__version__ = "1.0.0"

class ArgusCurrentStatus( ArgusStatus ):

    __enable_https_client_authentication = False

    def __init__( self, clientAuth ):
        super(ArgusCurrentStatus, self).__init__(clientAuth)
        self.__enable_https_client_authentication = clientAuth
        
    def getStatus( self ):
        d = ArgusStatus.getStatus( self )
        if d['Status'] == 'OK':
            ArgusStatus.nagios_ok(self, "Status Ok")
        else:
            ArgusStatus.nagios_critical(self, "\"Status: OK\" not found.")
        
def main():
    handler = ArgusCurrentStatus(False)
    
    signal.signal(signal.SIGALRM, handler.sig_handler)
    signal.signal(signal.SIGTERM, handler.sig_handler)
    
    handler.readOptions()
    
    status = handler.getStatus()
    print status.items()
    
if __name__ == '__main__':
    main()