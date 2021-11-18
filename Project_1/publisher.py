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
        self.proxy_socket = context.socket(zmq.REQ)
        self.proxy_socket.connect('tcp://localhost:5555')

    def put(self, topic):
        # Send Message
        put_message = '\x02' + topic + ' ' + self.create_random_string()

        self.proxy_socket.send(put_message.encode('utf-8'))
        print("Sent: " + put_message)

        # Wait for Confirmation
        message = self.proxy_socket.recv()
        if(message.decode('utf-8') != 'Saved'):
            print("Message not delivered")
            return
        print("Message Saved")

    def create_random_string(self):
        string_length = random.randrange(5, 25)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))

        return str(ran)

pub = Publisher()
for i in range(10):
    pub.put('fruit')
    time.sleep(0.1)