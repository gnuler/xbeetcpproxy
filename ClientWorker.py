#!/usr/bin/env python

import serial, time
from xbee import digimesh
import socket   #for sockets
import select
import sys  #for exit
from daemon import *
from communicator import *
import logging
import logging.handlers
import time
import signal


HOST = 'localhost'
PORT =1883



#Protocol
CONTROL              = 0x0
DATA                 = 0x1

CTRL_CONNECT_REQ     = 0x10
CTRL_CONNECT_SUCCESS = 0x11
CTRL_CONNECT_FAIL    = 0x12

CTRL_DISCONNECT      = 0x30
CTRL_DEBUG           = 0x40

#This class should handle messages from a single xbee node, identified
# by it's address.

class ClientWorker(threading.Thread):
    
    def __init__(self, address, communicator):


        threading.Thread.__init__(self)

        # Xbee address
        self._address = address

        # Global xbee communicator
        self._communicator = communicator

        # TCP connection to the mqtt broker
        self._connection = None


        self._stop = threading.Event()
       
        self.logger = logging.getLogger('MeshLogger')

    def stop(self):
        self._stop.set()
        self._connection == None

    def stopped(self):
        return self._stop.isSet()


    def _createConnection(self):


        #if self._connection:
        #    print "Connection already exists, ignoring request"
        #    return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            self.logger.critical("Could not create socket!")
            self._connection == None
            return False


        try:
            remote_ip = socket.gethostbyname( HOST )
        except socket.error:
            self.logger.critical("Hostname could not be resolved. Exiting")
            self._connection == None
            return False

        self.logger.debug('\tIp address of ' + HOST + ' is ' + remote_ip)

        try:
            s.connect((remote_ip , PORT))
            self.logger.debug('\tSocket Connected to ' + HOST + ' on ip ' + remote_ip)
        except:
            self.logger.critical('Connection refused')
            self._connection == None
            return False

        self._connection = s
        return True


    def _handleCommandMessage(self, data):
        
        opcode = ord(data[0])

        if opcode == CTRL_CONNECT_REQ:
            self.logger.debug("We received a CONNECT request")
            # TODO: verify this and return an error if fails?

            # If there is an open connection we close it first
            # We could be out of sync if we try to reuse the same one
            if self._connection:
                self._connection.close()


            if self._createConnection():
                self.logger.debug("Connect succeeded, sending CTRL_CONNECT_SUCCESS")
                ackMsg = Message(self._address, chr(CONTROL)+chr(CTRL_CONNECT_SUCCESS))
            else:
                self.logger.debug("Connect failed, sending CTRL_CONNECT_FAIL")
                ackMsg = Message(self._address, chr(CONTROL)+chr(CTRL_CONNECT_FAIL))
                self._connection == None

            self._communicator.sendMessage(ackMsg)


        elif opcode == CTRL_DISCONNECT:
            self.logger.debug("\t is a disconnect")
            if self._connection != None:
                self._connection.close()
                self._connection = None

        elif opcode == CTRL_DEBUG:
            self.logger.debug("\t is a debug message")
            size = ord(data[1])
            msg = data[2:]
            self.logger.debug("\tMSG size=%d: %s, %s" % (size, msg, msg.encode("hex")))


        else:
            self.logger.critical("Received an unknown command")


    def _informDisconnection(self):
            self.logger.debug("Informing about the disconnection to the BEE")
            disconnectionMsg = Message(self._address, chr(CONTROL)+chr(CTRL_DISCONNECT))
            self._communicator.sendMessage(disconnectionMsg)
            self.stop()

    def _handleDataMessage(self, data):

        self.logger.debug("XBEE->MQTT %s (%s) " % (data, data.encode("hex")) )

        #if not self._connection:
        #    print "\tNot connected, cant send the message to the tcp client."
        #    self._informDisconnection()
        #    self._connection == None
        #    return
      
        try:
            self._connection.send(data)
        except:
            self.logger.critical("Fail at sending to the tcp client, we should send a disconnected alert?")
            self._connection == None
            self._informDisconnection()


    def handleMessage(self, data):

		# Command
        if data[0] == '\x00':
            self.logger.debug("We got a command message")
            self._handleCommandMessage(data[1:])

        elif data[0] == '\x01':
            self.logger.debug("We got a data message")
            self._handleDataMessage(data[1:])

        else:
            sellf.logger.critical("We got an unkown message type:" + data.encode("hex"))


    def _handleTCPData(self):

        data = self._connection.recv(1000)

        if (len(data) == 0) :
            self._connection = None
            self._informDisconnection()
            return

        ###############################
        #DEBUG, TODO, remove this
        #if data=="disco\n":
        #    self._informDisconnection()
        ##############################

        self.logger.debug("Sending data to the BEE")
        self.logger.debug("MQTT->XBEE %s (%s) " % (data, data.encode("hex")))

        msg = Message(self._address, chr(DATA) + data);
        self._communicator.sendMessage(msg)
        return


   
    def run(self):

        while not self.stopped():

            self.logger.debug("In the dev looppp")


            #time.sleep(1)
            if self._connection == None:
                time.sleep(0.5)
                continue

            try:
                ready_to_read, ready_to_write, in_error = \
                    select.select([self._connection],[],[])

                if (len(ready_to_read)==1):
                    self._handleTCPData()
            except:
               # self._informDisconnection()

                self.logger.critical("""
                $$$$$$$$$$$$$$$$$$$$$$$
                Fail at sending, we should send a disconnected alert?
                $$$$$$$$$$$$$$$$$$$$$$$
                """)




