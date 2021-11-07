import string    
import random
import time
import zmq
import sys

# Create Publisher Socket
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://localhost:5560')

topic = sys.argv[1]

# Send random string about the topic
while True:
    string_length = random.randrange(5, 25)
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = string_length))
    socket.send_string(topic + " : " + str(ran))

    time.sleep(1)