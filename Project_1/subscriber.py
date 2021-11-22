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

        self.proxy_socket = context.socket(zmq.REQ)
        self.proxy_socket.connect('tcp://localhost:5555')

    def subscribe(self, topic):
        # Subscribe to message of the given topic
        subs_message = '\x01' + topic + ' ' + str(self.id)
        self.proxy_socket.send(subs_message.encode('utf-8'))

        # Receive Confirmation
        response = self.proxy_socket.recv()

        if(response.decode('utf-8') == 'subscribed ' + topic):
            print('Client ' + str(self.id) + ' subscribed to topic ' + topic)
        else:
            print('Failed to subscribe to topic ' + topic)

    
    def unsubscribe(self, topic):
        # Unsubscribe to message of the given topic
        unsub_message = '\x00' + topic + ' ' + str(self.id)
        self.proxy_socket.send(unsub_message.encode('utf-8'))

        # Receive Confirmation
        response = self.proxy_socket.recv()

        if(response.decode('utf-8') == 'unsubscribed ' + topic):
            print('Client ' + str(self.id) + ' unsubscribed to topic ' + topic)

        else:
            print('Failed to unsubscribe to topic ' + topic)

        
    def get(self, topic):
        # Send Request for a new Message froma topic
        get_message = '\x03' + topic + ' ' + str(self.id)
        self.proxy_socket.send(get_message.encode('utf-8'))

        # Read and Parse the response
        response_bytes = self.proxy_socket.recv_multipart()
        print(response_bytes)
        topic_received, topic_message = response_bytes[0].decode('utf-8').split()
        
        if topic_message == 'none':
            print('No messae of that topic.')
            # Deve este get nao contar como um verdadeiro get?

        if topic_received == topic:
            print('Client ' + str(self.id) + ' received: ' + topic_message)
        else:
            print('Received message from other topic:')
            print(response_bytes)
        

# Script in run "subscriber.py id topic_name n_gets time_between_gets"
arguments = sys.argv[1:]

if len(arguments) > 4 or len(arguments) < 2:
    print("Numbers of arguments is not corret. Script is run as 'subscriber.py id topic_name n_gets'. n_gets is optional.")
    sys.exit(0)

# Check if there is any wait time between gets
wait = False

if len(arguments) == 4:
    wait = True
    time_to_wait = int(arguments[3])

sub = Subscriber(arguments[0])

sub.subscribe(arguments[1])

if len(arguments) == 2:
    while True:
        sub.get(arguments[1])

        if wait:
            print("Waiting before next get...")
            time.sleep(time_to_wait)
else:
    for x in range(int(arguments[2])):
        sub.get(arguments[1])

        if wait:
            print("Waiting before next get...")
            time.sleep(time_to_wait)
        

sub.unsubscribe('fruit')
