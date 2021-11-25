import string    
import random
import zmq
import asyncio
import json
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Class Subscriber
# Subscribes and Unsubscribes to topics
# Can get messages from topics that it subscribes to
class Subscriber:
    def __init__(self, id) -> None:
        # Subscriber Basic Info
        self.id = id
        self.last_msg_received = -1
        self.file_title = 'client_' + self.id + '.txt'

        if os.path.exists(self.file_title):
            self.read_json()

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
            if os.path.exists(self.file_title):
                os.remove(self.file_title)

        else:
            print('Failed to unsubscribe to topic ' + topic)

        
    def get(self, topic):
        # Send Request for a new Message from a topic
        get_message = '\x03' + topic + ' ' + str(self.id) + ' ' + str(self.last_msg_received)
        self.proxy_socket.send(get_message.encode('utf-8'))

        print("\nSent request: " + get_message)
        # Read and Parse the response
        response_bytes = self.proxy_socket.recv_multipart()

        topic_received, topic_message, message_id = response_bytes[0].decode('utf-8').split()
        
        if topic_message == 'none':
            print("Topic " + topic + " doesn't exist.")

        if topic_received == topic:
            print('Received response: ' + topic_message)
            self.last_msg_received = message_id

            self.save_json()

            # Send Ack
            ack_message = '\x04' + topic + ' ' + str(self.id) + ' ' + str(self.last_msg_received)
            print('Sent ACK: ' + ack_message)
            self.proxy_socket.send(ack_message.encode('utf-8'))

            # Receive Ack Response
            self.proxy_socket.recv_multipart()
            print('Received ACK response')

        else:
            print('Received message from other topic:')
            print(response_bytes)

    # Save all the infomration in a JSON
    # The JSON is then read in case of a crash to retrieve all the information
    def save_json(self):
        file_title = 'client_' + self.id + '.txt'
        data = {}
        data['last_msg_received'] = self.last_msg_received
        with open(file_title, 'w') as outfile:
            json.dump(data, outfile)

        print('Data Saved')

    def read_json(self):
        with open(self.file_title) as json_file:
            data = json.load(json_file)
            self.last_msg_received = data['last_msg_received']
        print('New last message: ' + str(self.last_msg_received))

# Class Publisher
# Creates and publishes random messages about a topic given
class Publisher:
    def __init__(self, topic_name) -> None:
        # Publisher Baisc Info
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

    # Generate a random string that will be used as the message content for a certain topic
    def create_random_string(self):
        string_length = random.randrange(5, 25)
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))

        return str(ran)

# Class Proxy
# Receives messages from Subscribers and Publishers
# Messages from Publishers are saved in their designated Topic.
# Messages are taken from a designated Topic and sent to Subscribers after a get() call.
class Proxy:
    def __init__(self, time_between_saves) -> None:
        # Check if args are correct
        if not time_between_saves.isdigit():
            print("Argument given is not a digit.")
            sys.exit(1)

        time_between_saves = float(time_between_saves)

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

        if os.path.exists('proxy_info.txt'):
            self.read_json()

        # Create ThreadPoolExecutor for multi threading
        self.executor = ThreadPoolExecutor(max_workers=25)
        self.executor.submit(self.save_json, time_between_saves)

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

                # If there are no subscribers in a topic, then it can be deleted
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
        elif message[0] == '\x03': #message is '\x03topic_name sub_id last_message_received'
            topic_name, sub_id, last_message_received = message.replace(message[0], '').split()

            if topic_name in self.topics_key_view:
                # Get message from the topic
                topic = self.topics[topic_name]

                topic_message = topic.get_message(sub_id, int(last_message_received))

                # If its Null, it means the subscriber has no message to receive
                if topic_message == 'Null':
                    print("Waiting for message...")
                    time.sleep(2)
                    return self.parse_ft(message_bytes)
                    
                reply = topic_name + '  ' + topic_message
            else:
                reply = topic_name + ' none'
        
        # ACK MESSAGE
        elif message[0] == '\x04': #message is '\x04topic_name sub_id last_message_received'
            topic_name, sub_id, last_message_received = message.replace(message[0], '').split()

            if topic_name in self.topics_key_view:
                # Update Topic Values for Sub
                topic = self.topics[topic_name]

                topic.update_sub_status(sub_id, last_message_received)
                
                reply = topic_name + ' ackReceived'

        self.frontend.send_multipart([message_bytes[0], b'', reply.encode('utf-8')])
        print("Received: " + message + " --> Replied: " + reply)

    # Save all the infomration in a JSON
    # The JSON is then read in case of a crash to retrieve all the information
    def save_json(self, time_between_save):
        if len(self.topics) == 0:
            if os.path.exists('proxy_info.txt'):
                os.remove('proxy_info.txt')

            print('Nothing to Save.')

            time.sleep(time_between_save)
            self.save_json(time_between_save)

        data = {}
        data['topic'] = []
        for key in self.topics:
            topic = self.topics[key]

            data['topic'].append({
            'name': topic.name,
            'n_msg': topic.num_msg,
            'subs': topic.subs,
            'messages': topic.messages,
            'subs_next_message': topic.subs_next_message
            })

        with open('proxy_info.txt', 'w') as outfile:
            json.dump(data, outfile)

        print('Data Saved')
        time.sleep(time_between_save)
        self.save_json(time_between_save)

    def read_json(self):
        with open('proxy_info.txt') as json_file:
            data = json.load(json_file)
            for t in data['topic']:
                new_topic = Topic(t['name'], t['n_msg'], t['subs'], {int(k):v for k,v in t['messages'].items()}, t['subs_next_message'])
                self.topics[new_topic.name] = new_topic

# Class Topic
# Represents a topic created when a subscriber subscribes to a given topic.
# Hold every information necessary to maintain the integraty of the messages and the order in which they are sented/received
class Topic:
    def __init__(self, name, n_msg = 0, subs =  [], messages = {}, subs_next_message = {}) -> None:
        # Topic ID
        self.name = name
        self.num_msg = n_msg

        # Arrays/Dictionary to save information about the topic
        self.subs = subs
        self.messages = messages # Key --> message ID; Value --> Message content
        self.subs_next_message = subs_next_message # Key --> sub ID; Value --> Message ID

        # Views to help to analyse the dictionaries
        self.messages_stored_view = self.messages.keys()
        self.next_message_view = self.subs_next_message.values()

        print('Topic ' + name + ' created successfully!')

    # Adds a message to this topic
    async def add_message(self, message):
        self.messages[self.num_msg] = message
        self.num_msg += 1

    # Removes all messages that have already been sent
    async def remove_message(self):
        # No messages means nothing can be removed
        if len(self.messages_stored_view) == 0:
            return
        
        # Values that will tell if a subscriber is waiting for the oldest message avaialble
        first_message_id = min(self.messages_stored_view)
        subs_min_next_mesage_id = min(self.next_message_view)

        # If the lowest message id available is lower then the lowest message id that all subscribers are waiting
        # It can be deleted
        while first_message_id < subs_min_next_mesage_id:
            self.messages.pop(first_message_id)

            # No messages means nothing can be removed
            if len(self.messages_stored_view) == 0:
                return

            first_message_id = min(self.messages_stored_view)


    # Retrieves a message to send to a subscriber
    def get_message(self, sub_id, last_message_received):
        if sub_id not in self.subs:
            print('Subscriber not subscribed to topic ' + self.name)
            return "Error"
    
        # Get message id corresponding to the subscriber
        message_id = self.subs_next_message[sub_id]

        if not (last_message_received == -1) and (last_message_received + 1) != message_id:
            self.subs_next_message[sub_id] = last_message_received
            message_id = last_message_received + 1

        # message_id is only equal to num_msg when a subscriber as just subscribed to this topic
        if message_id == self.num_msg or self.num_msg < last_message_received:
            print("No message for subscriber.")
            return "Null"

        # Get Message
        message = self.messages[message_id]

        return message + ' ' + str(message_id)

    # Update Information relative to a specific subscriber
    def update_sub_status(self, sub_id, last_message_received):
        # Update values related to this sub
        self.subs_next_message[sub_id] = int(last_message_received) + 1

        # Check if any message can be removed
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.remove_message())

        
    # Add a subscriber to this topic
    def add_sub(self, sub_id):
        if sub_id in self.subs:
            print("Subscriber " + sub_id + " already subscribed to topic " + self.name)
            return

        self.subs.append(sub_id)
        self.subs_next_message[sub_id] = self.num_msg

    # Remove a subscriber to this topic
    def remove_sub(self, sub_id):
        if sub_id not in self.subs:
            print("Subscriber " + sub_id + " already unsubscribed to topic " + self.name)
            return

        self.subs.remove(sub_id)
        self.subs_next_message.pop(sub_id)
