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
    def __init__(self, topic_name) -> None:
        self.topic = topic_name

        # Create Publisher Socket
        context = zmq.Context()
        self.proxy_socket = context.socket(zmq.REQ)
        self.proxy_socket.connect('tcp://localhost:5555')

    def put(self):
        # Send Message
        put_message = '\x02' + self.topic + ' ' + self.create_random_string()

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

# Script is run "publisher.py topic_name n_puts"
arguments = sys.argv[1:]

if len(arguments) != 2:
    print("Numbers of arguments is not corret. Script is run as 'publisher.py topic_name n_puts'.")
    sys.exit(0)

pub = Publisher(arguments[0])

for i in range(int(arguments[1])):
    pub.put()

