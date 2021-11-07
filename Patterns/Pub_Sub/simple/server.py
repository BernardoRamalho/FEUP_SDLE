import time
import zmq

# Create Publisher Socket
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind('tcp://*:5555')

# Send 5 messages to the subscribers
for i in range(5):
    socket.send(b'status 5')
    socket.send(b'All is well')
    time.sleep(1)