import string    
import random
import time
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
        self.proxy_socket = context.socket(zmq.XPUB) # TODO: testar XPUB
        self.proxy_socket.connect('tcp://localhost:5560')

    def put(self, topic):
        # Send Message
        message = self.create_random_string()
        self.proxy_socket.send_string(topic + " : " + message)
        print("Sent: " + topic + " : " + message)

        # Wait for Confirmation
        message = self.proxy_socket.recv_multipart()
        if(message[0].decode('utf-8') != 'Saved'):
            print("Message not delivered")

    def create_random_string(self):
        string_length = random.randrange(5, 25)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))

        return str(ran)

pub = Publisher()
for i in range(10):
    pub.put('fruit')
    time.sleep(0.1)