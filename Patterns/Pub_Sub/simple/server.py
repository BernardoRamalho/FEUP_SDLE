import signal
import time
import zmq


context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:5555')

for i in range(5):
    socket.send(b'status 5')
    socket.send(b'All is well')
    time.sleep(1)