import signal
import time
import zmq
import random


context = zmq.Context()
socketPT = context.socket(zmq.PUB)
socketPT.bind('tcp://*:5555')

while True:
    zipcode = random.randrange(1, 10000)
    temperature = random.randrange(-10, 40)
    humidity = random.randrange(10, 60)

    socketPT.send_string('{0} {1} {2}'.format(zipcode, temperature, humidity))

    time.sleep(0.1)