import signal
import time
import zmq
import random

# Create Publisher Socket
context = zmq.Context()
socketUS = context.socket(zmq.PUB)
socketUS.bind('tcp://*:5557')

# Send random messages to random zipcodes
while True:
    zipcode = random.randrange(1, 100000)
    temperature = random.randrange(-10, 40)
    humidity = random.randrange(10, 60)

    socketUS.send_string('{0} {1} {2}'.format(zipcode, temperature, humidity))