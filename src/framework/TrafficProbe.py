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
import pickle
import time
import os
from os import path, makedirs
from Probe import ArgusProbe
from AbstractProbe import ArgusAbstractProbe
from optparse import OptionParser, OptionGroup

class ArgusTrafficProbe( ArgusProbe ):

    __pickle_dir = None
    __pickle_file = None

    def __init__( self, serviceName, clientAuth ):
        super(ArgusTrafficProbe, self).__init__(serviceName, clientAuth)
        namespace = self.getProbeName().split(".")[0]
        self.__pickle_dir = "../../../../var/lib/grid-monitoring/%s" % namespace
        self.__pickle_file = "%s.pickle" % self.getProbeName()
        
    def createParser( self ):
        super(ArgusTrafficProbe, self).createParser()
        optionParser = self.optionParser
        store_options = OptionGroup(optionParser, "Storage options", 
                                    "These options are used to change the default storage path for the needed temporary files")
        store_options.add_option("--tempdir",
                          dest = "temp_dir",
                          help = "Storage path for the needed temporary file. [default=%default]",
                          default = self.getPickleDir())
        store_options.add_option("--tempfile",
                          dest = "temp_file",
                          help = "Name for the needed temporary file. [default=%default]",
                          default = self.getPickleFile())
        optionParser.add_option_group(store_options)
        
        self.optionParser = optionParser
        
    def getPicklePath( self ):
        pickle_path = self.getPickleDir() + os.sep + self.getPickleFile()
        return pickle_path
        
    def getPickleFile( self ):
        return self.__pickle_file
        
    def setPickleFile( self,pickleFile ):
        self.__pickle_file = pickleFile
        
    def getPickleDir( self ):
        return self.__pickle_dir
        
    def setPickleDir( self, pickleDir ):
        self.__pickle_dir = pickleDir
        
    def saveCurrentState( self, state ):
        if not path.exists(self.getPickleDir()):
            try:
                makedirs(self.getPickleDir(), 0750)
            except Exception, e:
                self.nagios_warning("could not create temp-directory (%s): %s" 
                                    % (self.getPickleDir(), e))
        try:
            pickle.dump( state, open( self.getPicklePath(), "wb" ) )
        except Exception, e:
            self.nagios_warning("could not dump current state to temporary file (%s): %s" 
                                % (self.getPicklePath(), e))
        
    def getLastState( self ):
        try:
            return pickle.load( open( self.getPicklePath(), "rb" ) )
        except Exception, e:
            self.nagios_warning("could not read last state to temporary file (%s): %s" 
                                % (self.getPicklePath(), e))
    
    def update( self,status ):
        if path.exists(self.getPicklePath()):
            last_state = self.getLastState()
        else:
            last_state = {"TotalRequests" : 0, 
                          "TotalCompletedRequests" : 0, 
                          "TotalErroneousRequests" : 0, 
                          "Time" : time.time()}
            self.saveCurrentState(last_state)
        current_state = {"TotalRequests" : status['TotalRequests'], 
                         "TotalCompletedRequests" : status['TotalCompletedRequests'], 
                         "TotalErroneousRequests" : status['TotalRequestErrors'], 
                         "Time" : time.time()} # time is in seconds
        self.saveCurrentState(current_state)
        timeDiff = current_state['Time']-last_state['Time']
        requestsInPeriod = float(int(current_state['TotalRequests'])
                                -int(last_state['TotalRequests']))
        requestsPerSecond = requestsInPeriod / timeDiff
        completedRequestsInPeriod = float(int(current_state['TotalCompletedRequests'])
                                         -int(last_state['TotalCompletedRequests']))
        completedRequestsPerSecond = completedRequestsInPeriod / timeDiff
        erroneousRequestsInPeriod = float(int(current_state['TotalErroneousRequests'])
                                         -int(last_state['TotalErroneousRequests']))
        erroneousRequestsPerSecond = erroneousRequestsInPeriod / timeDiff
        return {"RequestsInPeriod" : round(requestsInPeriod), 
                "RequestsPerSecond" : round(requestsPerSecond,2), 
                "CompletedRequestsInPeriod" : round(completedRequestsInPeriod), 
                "CompletedRequestsPerSecond" : round(completedRequestsPerSecond,2), 
                "ErroneousRequestsInPeriod" : round(erroneousRequestsInPeriod), 
                "ErroneousRequestsPerSecond": round(erroneousRequestsPerSecond,2)}
        
    def check( self ):
        status = ArgusProbe.getStatus( self ) 
        self.setPickleDir(self.options.temp_dir)
        self.setPickleFile(self.options.temp_file)
        if not status['Service'] == self.getServiceName():
            self.nagios_critical("the answering service is not a %s" % self.getServiceName())
        diff = self.update(status)
        perfdata = " | RequestsPerSecond=%.2f; CompletedRequestsPerSecond=%.2f; ErroneousRequestsPerSecond=%.2f;" %\
                   (diff['RequestsPerSecond'], diff['CompletedRequestsPerSecond'], diff['ErroneousRequestsPerSecond'])
# Version with added absolute numbers of request in given time-interval:
#         perfdata = " | RequestsPerSecond=" + str(diff['RequestsPerSecond']) + \
#                      "; RequestsInPeriod=" + str(diff['RequestsInPeriod']) + \
#                      "; CompletedRequestsPerSecond=" + str(diff['CompletedRequestsPerSecond']) + \
#                      "; CompletedRequestsInPeriod=" + str(diff['CompletedRequestsInPeriod']) + \
#                      "; ErroneousRequestsPerSecond=" + str(diff['ErroneousRequestsPerSecond']) + \
#                      "; ErroneousRequestsInPeriod=" + str(diff['ErroneousRequestsInPeriod']) + ";"
        self.nagios_ok(status['Service'] + " " + status['ServiceVersion'] + 
                       ": Requests since last restart " + status['TotalRequests'] + perfdata)