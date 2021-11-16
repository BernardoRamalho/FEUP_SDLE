import string    
import random
import zmq
import sys
import signal

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Publisher!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Publisher:
    def __init__(self) -> None:
        # Create Publisher Socket
        context = zmq.Context()
        self.proxy_socket = context.socket(zmq.PUB)
        self.proxy_socket.connect('tcp://localhost:5560')

    def put(self, topic):
        string_length = random.randrange(5, 25)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))
        self.proxy_socket.send_string(topic + " : " + str(ran))