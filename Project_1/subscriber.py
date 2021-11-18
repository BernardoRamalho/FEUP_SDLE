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
        message = str(self.id) + ' ' + topic
        self.proxy_socket.send(message.encode('utf-8'))
        response = self.proxy_socket.recv_multipart()
        print('Client ' + str(self.id) + ' received: ' + response[0].decode('utf-8'))
        #message = str(self.id) + ' received'

sub = Subscriber(1)
sub.subscribe('fruit')
time.sleep(10)
sub.unsubscribe('fruit')

# while True:
#     #sub.get('fruit')
#     time.sleep(0.1)