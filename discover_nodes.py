import serial, time

from xbee import digimesh

def print_data(data):
        print data



serial_port = serial.Serial('/dev/ttyUSB0', 9600)
xbee = digimesh.DigiMesh(serial_port, escaped=True)
#xbee = digimesh.DigiMesh(serial_port, escaped=True, callback=print_data)

#xbee.send("at", frame='V', command='ID', parameter=None)
#xbee.send("at", frame='V', command='DH', parameter=None)
xbee.send("at", frame_id='A', command='ND', parameter=None)



#xbee.send("at", frame_id='V', command='ID')
#xbee.send('at', frame_id='A', command='DH')

# Wait for response
response = xbee.wait_read_frame()
print response



#xbee.send("tx", frame='A', dest_addr = "0000ffff", data="ACT1ON123\n")






xbee.halt()
serial_port.close()

