import string    
import random
import zmq
import sys
import signal
import time

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Publisher!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class Publisher:
    def __init__(self, topic_name) -> None:
        self.topic = topic_name
        self.num_put_message = 0
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
        message = self.proxy_socket.recv().decode('utf-8')
        if(message != 'Saved'):
            print(message)
            return
        
        self.num_put_message += 1
        print("Message Saved")

    def create_random_string(self):
        string_length = random.randrange(5, 25)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))

        return str(ran)

# Script is run "publisher.py topic_name n_puts"
arguments = sys.argv[1:]

if len(arguments) < 2 or len(arguments) > 3:
    print("Numbers of arguments is not corret. Script is run as 'publisher.py topic_name n_puts [time_between_puts]'.")
    sys.exit(0)

pub = Publisher(arguments[0])

wait = False

# Check if there is any wait time between gets
if len(arguments) == 3:
    wait = True

    # Check if user inputed a correct value
    if not arguments[2].isdigit():
        print("Error in arguments. Value was not a digit for time_between_puts. Script is run as 'publisher.py topic_name n_puts [time_between_puts]'.")
        sys.exit(0)

    time_to_wait = int(arguments[2])

while pub.num_put_message != int(arguments[1]):
    pub.put()
    if wait:
        print("Waiting before next put...")
        time.sleep(time_to_wait)

