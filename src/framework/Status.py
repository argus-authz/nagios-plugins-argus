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
from AbstractProbe import ArgusAbstractProbe
from Connection import ArgusConnection
import signal
from urllib2 import HTTPError, URLError
import urllib2

__version__ = "1.0.0"

class ArgusStatus( ArgusAbstractProbe ):

    __enable_https_client_authentication = False

    def __init__( self, clientAuth ):
        super(ArgusStatus, self).__init__(clientAuth)
        self.__enable_https_client_authentication = clientAuth
        
    def getStatus( self ):
    
        if self.__enable_https_client_authentication:
            cert_handler = ArgusConnection(key=self.options.key, 
                                                cert=self.options.cert,
                                                timeout=self.options.timeout) 
        
            opener = urllib2.build_opener(cert_handler)
            urllib2.install_opener(opener)
        
        try:
            if self.options.verbose:
                print "Contacting %s..." % self.url
            f = urllib2.urlopen(self.url)
        except HTTPError, e:
            self.nagios_critical("Error: %s: %s" % (self.url, e))   
        except URLError, e:
            self.nagios_critical("Error: %s: %s" % (self.url, e))
            
        d = dict()
        for line in f:
            (key, value) = line.rsplit('\n')[0].split(": ")
            d[key] = value
            
        return d
    
def main():
    handler = ArgusStatus(False)
    
    signal.signal(signal.SIGALRM, handler.sig_handler)
    signal.signal(signal.SIGTERM, handler.sig_handler)
    
    handler.readOptions()
    
    status = handler.getStatus()
    print status.items()
    
if __name__ == '__main__':
    main()