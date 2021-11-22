import string    
import random
import zmq
import asyncio
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor

# Class Subscriber
# Subscribes and Unsubscribes to topics
# Can get messages from topics that it subscribes to
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

        topic_received, topic_message = response_bytes[0].decode('utf-8').split()
        
        if topic_message == 'none':
            print('No messae of that topic.')
            # Deve este get nao contar como um verdadeiro get?

        if topic_received == topic:
            print('Client ' + str(self.id) + ' received: ' + topic_message)
        else:
            print('Received message from other topic:')
            print(response_bytes)
        
# Class Publisher
# Creates and publishes random messages about a topic given
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

# Class Proxy
# Receives messages from Subscribers and Publishers
# Messages from Publishers are saved in their designated Topic.
# Messages are taken from a designated Topic and sent to Subscribers after a get() call.
class Proxy:
    def __init__(self) -> None:
        # Create XPUB and XSUB sockets
        context = zmq.Context()

        self.frontend = context.socket(zmq.ROUTER)
        self.frontend.bind("tcp://*:5555")

        # Create Poller to handle the messages
        self.poller = zmq.Poller()
        self.poller.register(self.frontend, zmq.POLLIN)

        # Create Dict to save topics
        self.topics = {} # Key --> topic name; Value --> topic object
        self.topics_key_view = self.topics.keys() # It will help check if a topic exists

        # Create ThreadPoolExecutor for multi threading
        self.executor = ThreadPoolExecutor(max_workers=25)
        self.executor.submit(self.save_json)

    # Main loop of the proxy
    def run(self):
        while True:
            # Wait for sockets to receive messages
            socks = dict(self.poller.poll())
            

            # Read message from sockets
            if socks.get(self.frontend) == zmq.POLLIN:
                message = self.frontend.recv_multipart()

                self.executor.submit(self.parse_ft, message)

        # We never reach this code
        self.frontend.close()
        self.context.term()

    # Parse Messages comming from the frontend socket
    def parse_ft(self, message_bytes):
        message = message_bytes[2].decode('utf-8')
        reply = 'ERROR: Incorret Message Format. Message received: ' + message
        
        # SUB MESSAGE
        if message[0] == '\x01': # message is '\x01topic_name sub_id'
            topic_name, sub_id = message.replace(message[0], '').split()
            
            if topic_name in self.topics_key_view:
                # If topic already exits, just add a new sub
                self.topics[topic_name].add_sub(sub_id)
            else:
                # Create new topic
                new_topic = Topic(topic_name)
                new_topic.add_sub(sub_id)

                # Add new topic to dict
                self.topics[topic_name] = new_topic
            
            reply = 'subscribed ' + topic_name

        # UNSUB MESSAGE
        elif message[0] == '\x00': # message is '\x00topic_name sub_id'
            topic_name, sub_id = message.replace(message[0], '').split()
            
            if topic_name in self.topics_key_view:
                self.topics[topic_name].remove_sub(sub_id)

                if len(self.topics[topic_name].subs) == 0:
                    del self.topics[topic_name]
                    print("Topic " + topic_name + " deleted because no client subscribed to it.")
            
            reply = 'unsubscribed ' + topic_name

        # PUT MESSAGE
        elif message[0] == '\x02': # message is '\x02topic_name message' 
            topic_name, message_content = message.replace(message[0], '').split()

            if topic_name in self.topics_key_view:
                # Add Message to Topic
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.topics[topic_name].add_message(message_content))

                reply = 'Saved'
            
            else:
                reply = 'ERROR: No subscriber exists for topic ' + topic_name + '.'

        # GET MESSAGE
        elif message[0] == '\x03': #message is '\x03topic_name sub_id'
            topic_name, sub_id = message.replace(message[0], '').split()

            if topic_name in self.topics_key_view:
                topic = self.topics[topic_name]
 
                topic_message = topic.get_message(sub_id)

                if topic_message == 'Null':
                    print("Waiting for message...")
                    time.sleep(2)
                    self.parse_ft(message_bytes)
                    
                reply = topic_name + '  ' + topic_message
            else:
                reply = topic_name + ' none'

        self.frontend.send_multipart([message_bytes[0], b'', reply.encode('utf-8')])


    # Parse Messages comming from the backend socket
    # Messages from the backend are in the form of 'topic_name : message_content'
    def save_json(self):
        if len(self.topics) == 0:
            if os.path.exists('data.txt'):
                os.remove('data.txt')

            print('Nothing to Save.')
            time.sleep(10)
            self.save_json()

        data = {}
        data['topic'] = []
        for key in self.topics:
            topic = self.topics[key]

            data['topic'].append({
            'name': topic.name,
            'n_msg': topic.num_msg,
            'subs': topic.subs,
            'messages': topic.messages,
            'subs_last_message': topic.subs_last_message
            })

        with open('data.txt', 'w') as outfile:
            json.dump(data, outfile)

        print('Data Saved')
        time.sleep(10)
        self.save_json()

# Class Topic
# Represents a topic created when a subscriber subscribes to a given topic.
# Hold every information necessary to maintain the integraty of the messages and the order in which they are sented/received
class Topic:
    def __init__(self, name) -> None:
        # Topic ID
        self.name = name
        self.num_msg = 0

        # Arrays/Dictionary to save information about the topic
        self.subs = []
        self.messages = {} # Key --> message ID; Value --> Message content
        self.subs_last_message = {} # Key --> sub ID; Value --> Message ID

        # Views to help to analyse the dictionaries
        self.messages_stored_view = self.messages.keys()
        self.last_message_view = self.subs_last_message.values()

        print('Topic ' + name + ' created successfully!')

    # Adds a message to this topic
    async def add_message(self, message):
        self.messages[self.num_msg] = message
        self.num_msg += 1

    # Removes all messages that have already been sent
    def remove_message(self):
        if len(self.messages_stored_view) == 0:
            return

        first_message_id = min(self.messages_stored_view)
        subs_last_mesage_id = min(self.last_message_view)

        if first_message_id < subs_last_mesage_id:
            self.messages.pop(first_message_id)
            return self.remove_message()

    # Retrieves a message to send to a subscriber
    def get_message(self, sub_id):
        if sub_id not in self.subs:
            print('Subscriber not subscribed to topic ' + self.name)
            return "Error"

        message_id = self.subs_last_message[sub_id]

        if message_id == self.num_msg:
            print("No message for subscriber.")
            return "Null"

        self.subs_last_message[sub_id] = message_id + 1
        message = self.messages[message_id]

        self.remove_message()
        return message


    # Add a subscriber to this topic
    def add_sub(self, sub_id):
        if sub_id in self.subs:
            print("Subscriber " + sub_id + " already subscribed to topic " + self.name)
            return

        self.subs.append(sub_id)
        self.subs_last_message[sub_id] = self.num_msg

    # Remove a subscriber to this topic
    def remove_sub(self, sub_id):
        if sub_id not in self.subs:
            print("Subscriber " + sub_id + " already unsubscribed to topic " + self.name)
            return

        self.subs.remove(sub_id)
        self.subs_last_message.pop(sub_id)

    def print_info(self):
        print(self.messages)
        print(self.subs)