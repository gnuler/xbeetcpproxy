
import serial, time

from xbee import digimesh

def print_data(data):
        print data



serial_port = serial.Serial('/dev/ttyUSB0', 9600)
xbee = digimesh.DigiMesh(serial_port, escaped=True, callback=print_data)
#xbee = digimesh.DigiMesh(serial_port, escaped=True, callback=print_data)

#xbee.send("at", frame='V', command='ID', parameter=None)
xbee.send("at", frame='A', command='ND', parameter=None)



#xbee.send("tx", frame='A', dest_addr = "0000ffff", data="ACT1ON123\n")




time.sleep(5)


xbee.halt()
serial_port.close()


