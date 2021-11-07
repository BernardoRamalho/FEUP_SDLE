import string    
import random
import time
import zmq
import sys

# Create Socket
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://localhost:5560')


S = 10

topic = sys.argv[1]

while True:
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))
    socket.send_string(topic + " : " + str(ran))

    time.sleep(1)