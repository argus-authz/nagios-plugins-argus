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
import urllib2
import httplib
import socket

__version__ = "1.0.0"

class ArgusConnection( urllib2.HTTPSHandler ):

    key = "/etc/grid-security/hostkey.pem"
    cert = "/etc/grid-security/hostcert.pem"
    
    def __init__(self, key, cert, timeout):
        urllib2.HTTPSHandler.__init__(self)
        self.file_exists(key)
        self.key = key
        self.file_exists(cert)
        self.cert = cert
        self.timeout = timeout
 
    def https_open(self, req):
        return self.do_open(self.getConnection, req)
    
    def getConnection(self, host, timeout):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

    def file_exists(self, file):
        try:
            open(file)
        except IOError, e:
            print "Error: %s does not exist or is not readable" % (file)
            exit(2)