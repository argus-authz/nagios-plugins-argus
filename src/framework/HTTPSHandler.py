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
import sys
if sys.version_info[0]>2:
    import urllib.request as urllib2
    import http.client as httplib
else:
    import urllib2
    import httplib
import socket
from .AbstractProbe import ArgusAbstractProbe

class HTTPSClientAuthenticationHandler( urllib2.HTTPSHandler ):

    """
    key and cert MUST exists
    """
    def __init__(self, key, cert, timeout, context):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
        self.timeout = timeout
        self.ctx = context
        socket.setglobaltimeout = timeout
 
    def https_open(self, req):
        return self.do_open(self.getConnection, req)
    
    def getConnection(self, host, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
	if (self.ctx==None):
	    return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
	else:
	    return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert, context=self.ctx)

