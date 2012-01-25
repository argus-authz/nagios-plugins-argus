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
from optparse import OptionParser, OptionGroup
from sys import stderr, exit
from urlparse import urlparse
import sys
import signal
import inspect

import Version

class ArgusAbstractProbe( object ):
    """
    This is an "abstract" class for a generic Argus nagios probe. It is meant to be extendet. Stuff
    that need to be implemented rises a NoImplementedError if not overridden.
    """

    # SSL-options switch
    __enable_https_client_authentication = False

    # Default return values for Nagios
    OK       = 0
    WARNING  = 1
    CRITICAL = 2
    UNKNOWN  = 3
    
    # Default values for the different options and Constants    
    DEFAULT_PORT = None
    DEFAULT_TIMEOUT = 20
    DEFAULT_VERBOSITY = False 
    DEFAULT_CERT_DIR = "/etc/grid-security/hostcert.pem"
    DEFAULT_KEY_DIR = "/etc/grid-security/hostkey.pem"
    DEFAULT_CA_DIR = "/etc/grid-security/certificates"
    
    # Variables 
    usage = "usage %prog [options]"
    probeName = None
    serviceName = None
    optionParser = None
    options = None
    args = None
    url = None
    
    # constructor
    def __init__( self, serviceName, clientAuth ):
        self.probeName = sys.argv[0].split("/")[-1]
        self.serviceName = serviceName

        self.optionParser = OptionParser(version="%s v.%s" % (self.probeName, Version.getVersion()))
        self.__enable_https_client_authentication = clientAuth
        
        signal.signal(signal.SIGALRM, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)
    
    # getters (and setters) for the default private variables and constants
    def getProbeName(self):
        return self.probeName
        
    def getServiceName(self):
        return self.serviceName
        
    def getDefaultPort( self ):
        return self.DEFAULT_PORT
        
    def setDefaultPort( self,defaultPort ):
        self.DEFAULT_PORT = defaultPort
        
    def getDefaultTimeout( self ):
        return self.DEFAULT_TIMEOUT
        
    def getDefaultVerbosity( self ):
        return self.DEFAULT_VERBOSITY
        
    def getURLTemplate( self ):
        return "https://%(hostname)s:%(port)s/status"
        
    def getHostname ( self ):
        if self.options.hostname:
            return self.options.hostname
        elif self.options.url:
            return urlparse(self.options.url)[1].split(':')[0]
        else:
            nagios_warning("could not determine hostname out of the given")
        
    def getDefaultCertDir( self ):
        return self.DEFAULT_CERT_DIR
        
    def getDefaultKeyDir( self ):
        return self.DEFAULT_KEY_DIR
        
    def getDefaultCaDir( self ):
        return self.DEFAULT_CA_DIR
    
    def isHTTPSClientAuthNenabled( self ):
        return self.__enable_https_client_authentication

    # return Values for Nagios
    def nagios_exit(self, exit_code, msg):
        print msg
        exit(exit_code)
        
    def nagios_ok(self,msg):
        self.nagios_exit(self.OK, msg)

    def nagios_warning(self,msg):
        self.nagios_exit(self.WARNING, msg)

    def nagios_critical(self,msg):
        self.nagios_exit(self.CRITICAL, msg)

    def nagios_unknown(self,msg):
        self.nagios_exit(self.UNKNOWN, msg)
        
    # read out the options from the command-line
    def createParser( self ):
        optionParser = self.optionParser
        optionParser.add_option("-H",
                      "--hostname",
                      dest="hostname",
                      help="The hostname of the service.")
    
        optionParser.add_option("-p",
                      "--port",
                      dest="port",
                      help="The port of the service. [default: %default]",
                      default = self.getDefaultPort())
                      
        optionParser.add_option("-u",
                      "--url",
                      dest="url",
                      help="The status endpoint URL of the service. Example: https://hostname:port/status")
    
        optionParser.add_option("-t",
                      "--timeout",
                      dest="timeout",
                      help="The TCP timeout for the HTTPS connection. [default: %default]",
                      default = self.getDefaultTimeout())
                      
        optionParser.add_option("-v",
                      "--verbose",
                      action="store_true",
                      dest="verbose",
                      help="verbose mode [default: %default]",
                      default = self.getDefaultVerbosity())
  
        if self.__enable_https_client_authentication:
            ssl_options = OptionGroup(optionParser,"SSL options", "These options are used to set the SSL certificate to be used to authenticate with the PAP service.")
        
            ssl_options.add_option("--cert",
                               dest="cert",
                               help="The SSL client certificate. [default: %default]",
                               default = self.getDefaultCertDir())
        
            ssl_options.add_option("--key",
                               dest="key",
                               help="The private key (the key must be unencrypted). [default: %default]",
                               default = self.getDefaultKeyDir())
        
            ssl_options.add_option("--capath", 
                               dest="capath", 
                               help="The directory where trust anchors are stored on the system. [default: %default]",
                               default = self.getDefaultCaDir())
            optionParser.add_option_group(ssl_options)
        
    def readOptions( self ):
        optionParser = self.optionParser
        
        (self.options, self.args) = optionParser.parse_args()
        
        if self.options.hostname and not self.options.port:
            optionParser.error("Option -H HOSTNAME requires option -p PORT and vice versa. Complete URL can be set using option -u URL")

        if self.options.url and (self.options.hostname and self.options.port):
            optionParser.error("Options -u URL and {-H HOSTNAME and -p PORT} are mutually exclusive")

        if not self.options.url and not self.options.hostname:
            optionParser.error("Specify either option -u URL or option -H HOSTNAME (and -p PORT) or read the help (-h)")

        if self.options.port and self.options.hostname:
            self.url = self.getURLTemplate() % {'hostname': self.options.hostname, 'port': self.options.port}
        else:
            self.url = self.options.url

    # set-up the signal-handlers                        
    def sig_handler(self,signum, frame):
        if signum == signal.SIGALRM:
            self.nagios_unknown("Received timeout while fetching results.")
        elif signum == signal.SIGTERM:
            self.nagios_unknown("SIGTERM received.")
