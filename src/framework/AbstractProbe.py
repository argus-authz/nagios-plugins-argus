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

from optparse import OptionParser, OptionGroup
from string import Template
from sys import stderr, exit
import signal
import inspect
 
__version__ = "1.0.0"

class ArgusAbstractProbe( object ):
    """
    This is an "abstract" class for a generic Argus nagios probe. It is meant to be extendet. Stuff
    that need to be implemented rises a NoImplementedError if not overridden.
    """

    # SSL-options switch
    __enable_https_client_authentication = False
    
    # needs external file switch
    __enable_pickle_file_support = False

    # Default return values for Nagios
    OK       = 0
    WARNING  = 1
    CRITICAL = 2
    UNKNOWN  = 3
    
    # Default values for the different options and Constants    
    DEFAULT_PORT = "port"
    DEFAULT_TIMEOUT = 20
    DEFAULT_VERBOSITY = False
    PICKLE_DIR = "../../../../var/lib/grid-monitoring/" 
    DEFAULT_CERT_DIR = "/etc/grid-security/hostcert.pem"
    DEFAULT_KEY_DIR = "/etc/grid-security/hostkey.pem"
    DEFAULT_CA_DIR = "/etc/grid-security/certificates"
    
    # Variables
    __pickle_file = "pickleFile" 
    __url_template = "https://${hostname}:${port}/status"
    usage = "usage %prog [options]"
    optionParser = ""
    options = ""
    args = ""
    url = ""
    
    
    # constructor
    def __init__( self, clientAuth ):
        self.optionParser = OptionParser(version="%s v.%s" % (inspect.getfile(inspect.currentframe()), __version__))
        __enable_https_client_authentication = clientAuth
    
    # getters (and setters) for the default private variables and constants  
    def getDefaultPort( self ):
        return 8154
        #raise NotImplementedError( "Should have overridden the DEFAULT_PORT" )
        
    def getDefaultTimeout( self ):
        return self.DEFAULT_TIMEOUT
        
    def getDefaultVerbosity( self ):
        return self.DEFAULT_VERBOSITY
        
    def getDefaultPickleDir( self ):
        return self.PICKLE_DIR
    
    def getPickleFile( self ):
        return pfile
        #raise NotImplementedError( "Should have overridden the pickle_file" )
        
    def setPickleFile( self, pickle_file ):
        self.__pickle_file = pickle_file
        
    def getURLTemplate( self ):
        return self.__url_template
        
    def getDefaultCertDir( self ):
        return self.DEFAULT_CERT_DIR
        
    def getDefaultKeyDir( self ):
        return self.DEFAULT_KEY_DIR
        
    def getDefaultCaDir( self ):
        return self.DEFAULT_CA_DIR

    # return Values for Nagios
    def nagios_exit(self, exit_code, msg):
        print msg
        exit(exit_code)

    def nagios_ok(self, msg):
        self.nagios_exit(self.OK, msg)

    def nagios_critical(self, msg):
        self.nagios_exit(self.CRITICAL, msg)

    def nagios_unknown(self, msg):
        self.nagios_exit(self.UNKNOWN, msg)
        
    # read out the options from the command-line
    def readOptions( self ):
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
                      help="The status endpoint URL of the service. Example: https://hostname:8150/status")
    
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
                      
#       memory_options = OptionGroup(optionParser, "Memory options", "These options are used to set the nagios-limits for the memory.")
#         memory_options.add_option("-w", 
#                           "--warning",
#                           dest = "mem_warn",
#                           help = "Memory usage warning threshold in MB. (default=%default).", 
#                           default = self.getWarningMemoryTreshold())
#     
#         memory_options.add_option("-c",
#                           "--critical",
#                           dest = "mem_crit",
#                           help = "Memory usage critical threshold in MB. (default=%default).", 
#                           default = self.getCriticalMemoryTreshold())
#         optionParser.add_option_group(memory_options)
        
        if self.__enable_pickle_file_support:
            store_options = OptionGroup(optionParser, "Storage options", "These options are used to change the default storage path for the needed temporary files")
            store_options.add_option("--tempfile",
                              dest = "temp_file_path",
                              help = "Storage path for the needed temporary files. [default=%default]",
                              default = self.getDefaultPickleDir())
            optionParser.add_option_group(store_options)
  
        if self.__enable_https_client_authentication:
            ssl_options = OptionGroup(optionParser,"SSL options", "These options are used to set the SSL certificate to be used to authenticate with the PAP service.")
        
            ssl_options.add_option("-c",
                               "--cert",
                               dest="cert",
                               help="The SSL client certificate. [default: %default]",
                               default = self.getDefaultCertDir())
        
            ssl_options.add_option("-k",
                                "--key",
                               dest="key",
                               help="The private key (the key must be unencrypted). [default: %default]",
                               default = self.getDefaultKeyDir())
        
            ssl_options.add_option("--capath", 
                               dest="capath", 
                               help="The directory where trust anchors are stored on the system. [default: %default]",
                               default = self.getDefaultCaDir())
        
            optionParser.add_option_group(ssl_options)
    
        (self.options, self.args) = optionParser.parse_args()
        
        
        if self.options.hostname and not self.options.port:
            optionParser.error("Option -H HOSTNAME requires option -p PORT and vice versa. Complete URL can be set using option -u URL")

        if self.options.url and (self.options.hostname and self.options.port):
            self.nagios_unknown("Options -u URL and {-H HOSTNAME and -p PORT} are mutually exclusive")

        if not self.options.url and not self.options.hostname and not self.options.url:
            self.nagios_unknown("Specify either option -u URL or options -H HOSTNAME and -p PORT or read the help (-h)")

        if self.options.port and self.options.hostname:
            optdict = {'hostname': self.options.hostname,
                       'port': self.options.port}
            self.url = Template(self.__url_template).safe_substitute(optdict)
        else:
            self.url = self.options.url
            
            
            
    def sig_handler(signum, frame):
        if signum == signal.SIGALRM:
            nagios_unknown("Received timeout while fetching results.")
        elif signum == signal.SIGTERM:
            nagios_unknown("SIGTERM received.")
            
def main():
    handler = ArgusAbstractProbe()
    
    signal.signal(signal.SIGALRM, handler.sig_handler)
    signal.signal(signal.SIGTERM, handler.sig_handler)
    
    handler.readOptions()
    
            
if __name__ == '__main__':
    main()