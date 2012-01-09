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

    __pickle_dir = ""
    __pickle_file = ""
    __pickle_path = ""

    def __init__( self, serviceName, clientAuth ):
        self.__pickle_dir = "../../../../var/lib/grid-monitoring/%s/" % self.getProbeName()
        super(ArgusTrafficProbe, self).__init__(serviceName, clientAuth)
        self.__pickle_file = "%s_lastState.pickle" % self.getProbeName()
        self.__pickle_path = self.getPickleDir() + self.getPickleFile()
        
    def getPicklePath( self ):
        return self.__pickle_path
        
    def getPickleFile( self ):
        return self.__pickle_file
        
    def setPickleFile( self,pickleFile ):
        self.__pickle_file = pickleFile
        self.__pickle_path = self.getPickleDir() + pickleFile
        
    def getPickleDir( self ):
        return self.__pickle_dir
        
    def setPickleDir( self, pickleDir ):
        if not pickleDir[-1] == '/':
                self.__pickle_dir = pickleDir + "/"
        self.__pickle_dir = pickleDir
        
    def readOptions( self ):
        self.setPickleOptions(True)
        super(ArgusTrafficProbe, self).readOptions()
        
    def saveCurrentState( self, state ):
        if not path.exists(self.getPickleDir()):
            try:
                makedirs(self.getPickleDir(), 0750)
            except Exception, e:
                self.nagios_warning("could not create temp-directory (%s): " % self.getPickleDir() + e)
        try:
            pickle.dump( state, open( self.getPicklePath(), "wb" ) )
        except Exception, e:
            self.nagios_warning("could not dump current state to temporary file (%s): %s" % (self.getPicklePath(), e))
        
    def getLastState( self ):
        try:
            return pickle.load( open( self.getPicklePath(), "rb" ) )
        except Exception, e:
            self.nagios_warning("could not read last state to temporary file (%s): " + e % self.getPicklePath())
    
    def update( self,status ):
        if path.exists(self.getPicklePath()):
            last_state = self.getLastState()
        else:
            last_state = {"TotalRequests" : 0, "TotalCompletedRequests" : 0, "Time" : time.time()}
            self.saveCurrentState(last_state)
        current_state = {"TotalRequests" : status['TotalRequests'], "TotalCompletedRequests" : status['TotalCompletedRequests'], "Time" : time.time()} # time is in seconds
        self.saveCurrentState(current_state)
        timeDiff = int(current_state['Time']-last_state['Time'])
        requestsPerSecond = (int(current_state['TotalRequests'])-int(last_state['TotalRequests'])) / timeDiff
        totalRequestsPerSecond = (int(current_state['TotalCompletedRequests'])-int(last_state['TotalCompletedRequests'])) / timeDiff
        return {"RequestsPerSecond" : requestsPerSecond, "CompletedRequestsPerSecond" : totalRequestsPerSecond}
        
    def check( self ):
        status = ArgusProbe.getStatus( self )
        self.setPickleDir(self.options.temp_dir)
        self.setPickleFile(self.options.temp_file)
        if not status['Service'] == self.getServiceName():
            self.nagios_critical("the answering service is not a %s" % self.getServiceName())
        diff = self.update(status)
        perfdata = " | RequestsPerSecond=" + str(diff['RequestsPerSecond']) + " CompletedRequestsPerSecond=" + str(diff['CompletedRequestsPerSecond'])
        self.nagios_ok(status['Service'] + " " + status['ServiceVersion'] + ": Requests since last restart " + status['TotalRequests'] + perfdata)