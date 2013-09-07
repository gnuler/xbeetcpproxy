from communicator import *


class BaseDevice:


	# When sending commands the format is:
	# 	COMMANDXXX\r\n
	# Where COMMAND is the actual command
	# and XXX is the seq number
	BASE_COMMAND_SEND_FORMAT = "%s%03d\r\n"

	def __init__(self, name, addr, communicator=None):
		self._name = name
		self._addr = addr
		self._seq = 1
		self._communicator = communicator

		self._pendingCommands = {}


	def setCommunicator(self, communicator):
		self._communicator = communicator


	def getAddr(self):
		return self._addr


	def processIncommingMsg(self, data):
		return


	def _getNextSeq(self):
		self._seq += 1

		if self._seq == 1000:
			self._seq = 1
		return self._seq



	def _sendCommand(self, command):

		data = self.BASE_COMMAND_SEND_FORMAT % (command, self._getNextSeq())

		msg = Message(self.getAddr(), data, self._handler)
		self._communicator.sendMessage(msg)



	def _handler(self, msg, status):
		print "default handler, implement!"


class ActDevice(BaseDevice):


	def act(self, port, status):
		if status:
			command = "ACT%dON" % port
		else:
			command = "ACT%dOF" % port
		self._sendCommand(command)


	def queryStatus(self):
		self._sendCommand("STATUS")


	def _handler(self, msg, status):
		print "Status changed to %s" % msg.getStatusName()

	def processIncommingMsg(self, data):
		print "We received data! : %s" % data



