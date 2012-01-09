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
from AbstractProbe import ArgusAbstractProbe
from HTTPSHandler import HTTPSClientAuthenticationHandler
from urllib2 import HTTPError, URLError
import urllib2

__version__ = "1.0.0"

class ArgusProbe( ArgusAbstractProbe ):

    def __init__( self, serviceName, clientAuth ):
        super(ArgusProbe, self).__init__(serviceName, clientAuth)
    
    """
    return the status dictionary
    """
    def getStatus( self ):
        
        if self.isHTTPSClientAuthNenabled():
        
            self.file_exists(self.options.key)
            self.file_exists(self.options.cert)
                
            cert_handler = HTTPSClientAuthenticationHandler(key=self.options.key, 
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
        status = dict()
        for line in f:
            (key, value) = line.rsplit('\n')[0].split(": ")
            status[key] = value
        return status
        
    def getPickleFile( self ):
        print "no pickle-file needed for this service (Status)"
    
    """
    Exits with NAGIOS_CRITICAL if file doesn't exist or is not readable
    """
    def file_exists(self, file):
        try:
            open(file, "r")
        except IOError, e:
            self.nagios_critical(e)        