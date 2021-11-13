import time
import zmq
import sys

import signal

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Subscriber!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Subscriber:
    def __init__(self, id) -> None:
        self.id = id

        # Create a Subscriber socket
        context = zmq.Context()

        self.proxy_socket = context.socket(zmq.XSUB)
        self.proxy_socket.connect('tcp://localhost:5555')


    def subscribe(self, topic):
        # Subscribe to message of the given topic
        subs_message = '\x01' + topic
        self.proxy_socket.send(subs_message.encode('utf-8'))
    
    def unsubscribe(self, topic):
        # Unsubscribe to message of the given topic
        unsub_message = '\x00' + topic
        self.proxy_socket.send(unsub_message.encode('utf-8'))

        
    #def get(self, n_msg):
        # For loop in range(n_msg)
        # Send Message to Proxy asking for message
        # Respond to proxy confirming 