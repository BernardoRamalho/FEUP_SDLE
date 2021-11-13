import time
import zmq
import sys

import signal

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Subscriber!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create a Subscriber socket
context = zmq.Context()

socket = context.socket(zmq.XSUB)
socket.connect('tcp://localhost:5555')

# Subscribe to message of the given topic
topic = '\x01' + sys.argv[1]
socket.send(topic.encode('utf-8'))

# Receive messages about the topic subscribed
while True:
    message = socket.recv_multipart()
    print(bytes.join(b'', message).decode("utf-8"))
    time.sleep(1)