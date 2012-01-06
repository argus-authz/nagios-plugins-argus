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
from os import path, makedirs
from Probe import ArgusProbe
from AbstractProbe import ArgusAbstractProbe

__version__ = "1.0.0"

class ArgusTrafficProbe( ArgusProbe ):

    __pickle_dir = "../../../../var/lib/grid-monitoring/"
    __pickle_file = "lastState.p"

    def __init__( self, clientAuth, CURRENT_PROBE ):
        self.CURRENT_PROBE = CURRENT_PROBE
        self.__pickle_dir = "../../../../var/lib/grid-monitoring/%s/" % CURRENT_PROBE
        super(ArgusTrafficProbe, self).__init__(clientAuth)
        
    def getPickleFile( self ):
        return self.__pickle_file
        
    def setPickleFile( self,pickleFile ):
        self.__pickle_file = pickleFile
        
    def getPickleDir( self ):
        return self.__pickle_dir
        
    def setPickleDir( self, pickleDir ):
        self.__pickle_dir = pickleDir
        
    def readOptions( self ):
        self.setPickleOptions(True)
        super(ArgusTrafficProbe, self).readOptions()
        
    def saveCurrentState( self, state ):
        if not path.exists(self.__pickle_dir):
            try:
                makedirs(self.__pickle_dir, 0750)
            except Exception, e:
                ArgusAbstractProbe.nagios_warning("could not create temp-directory (%s): " % self.__pickle_dir + e)
        try:
            pickle.dump( state, open( self.__pickle_dir + self.__pickle_file, "wb" ) )
        except Exception, e:
            tempFile = self.__pickle_dir + self.__pickle_file
            ArgusAbstractProbe.nagios_warning("could not dump current state to temporary file (%s): " % tempfile + e)
        
    def getLastState( self ):
        try:
            return pickle.load( open( self.__pickle_dir + self.__pickle_file, "rb" ) )
        except Exception, e:
            ArgusAbstractProbe.nagios_warning("could not read last state to temporary file (%s): " + e % self.__pickle_dir + self.__pickle_file)
    
    def update( self,status ):
        if path.exists(self.__pickle_dir + self.__pickle_file):
            last_state = self.getLastState()
        else:
            last_state = {"TotalRequests" : 0, "TotalCompletedRequests" : 0, "Time" : time.time()}
            self.saveCurrentState(last_state)
        current_state = {"TotalRequests" : status['TotalRequests'], "TotalCompletedRequests" : status['TotalCompletedRequests'], "Time" : time.time()}
        self.saveCurrentState(current_state)
        timeDiff = current_state['Time']-last_state['Time']
        requestsPerSecond = (int(current_state['TotalRequests'])-int(last_state['TotalRequests'])) / timeDiff
        totalRequestsPerSecond = (int(current_state['TotalCompletedRequests'])-int(last_state['TotalCompletedRequests'])) / timeDiff
        return {"RequestsPerSecond" : requestsPerSecond, "CompletedRequestsPerSecond" : totalRequestsPerSecond}
        
    def getStatus( self, CURRENT_SERVICE ):
        d = ArgusProbe.getStatus( self )
        self.setPickleDir(self.options.temp_dir)
        self.setPickleFile(self.options.temp_file)
        if not d['Service'] == CURRENT_SERVICE:
            ArgusAbstractProbe.nagios_critical("the answering service is not a %s" % CURRENT_SERVICE)
        diff = self.update(d)
        perfdata = " | RequestsPerSecond= " + str(diff['RequestsPerSecond']) + "Requests/Sec CompletedRequestsPerSecond=" + str(diff['CompletedRequestsPerSecond']) + "Requests/Sec"
        ArgusAbstractProbe.nagios_ok(d['Service'] + " " + d['ServiceVersion'] + ": Requests since last restart " + d['TotalRequests'] + perfdata)