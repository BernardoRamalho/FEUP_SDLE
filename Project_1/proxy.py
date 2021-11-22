import zmq
import signal
import sys
import asyncio
import json
import time
import os
from auxClasses import Topic
from concurrent.futures import ThreadPoolExecutor

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Proxy!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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
            try:
                socks = dict(self.poller.poll())
            except KeyboardInterrupt:
                print('Closing Proxy!')
                sys.exit(0)


            # Read message from sockets
            if socks.get(self.frontend) == zmq.POLLIN:
                message = self.frontend.recv_multipart()

                self.executor.submit(self.parse_ft, message)

        # We never reach this code
        self.frontend.close()
        self.context.term()

    # Parse Messages comming from the frontend socket
    def parse_ft(self, message_bytes):
        # print("REQ Received: ")
        # print(message_bytes)
        message = message_bytes[2].decode('utf-8')
        reply = 'ERROR'
        
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

            else:
                # Create new topic
                new_topic = Topic(topic_name)

                # Add new topic to dict
                self.topics[topic_name] = new_topic

                # Add Message to Topic
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.topics[topic_name].add_message(message_content))

            reply = 'Saved'

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

        # print("Trying to REPLY:")
        # print([message_bytes[0], b'', reply.encode('utf-8')])
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

proxy = Proxy()
proxy.run()