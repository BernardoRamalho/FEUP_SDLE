import time
import zmq
import sys

# Create a Subscriber socket
context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')

# Subscribe to message of the given topic
topic = sys.argv[1]
socket.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))

# Receive messages about the topic subscribed
while True:
    message = socket.recv_multipart()
    print(bytes.join(b'', message).decode("utf-8"))
    time.sleep(1)