import zmq
import sys
import time

context = zmq.Context()

# Zipcode will be used to filter the messages accepted
zipcode = sys.argv[1]

# Create Socket to receive messages for US zipcodes
socketUS = context.socket(zmq.SUB)
socketUS.connect('tcp://localhost:5557')
socketUS.setsockopt(zmq.SUBSCRIBE, zipcode.encode('utf-8'))

# Create Socket to receive messages for PT zipcodes
socketPT = context.socket(zmq.SUB)
socketPT.connect('tcp://localhost:5555')
socketPT.setsockopt(zmq.SUBSCRIBE, zipcode.encode('utf-8'))

# Create a Poller to handle multiple sockets at once
poller = zmq.Poller()
poller.register(socketPT, zmq.POLLIN)
poller.register(socketUS, zmq.POLLIN)


while True:
    # Wait for sockets to receive messages
    socks = dict(poller.poll())

    # Read Messages from the Sockets
    if socks.get(socketUS) == zmq.POLLIN:
        message = socketUS.recv_multipart()
        print("US Zipcode: " + bytes.join(b'', message).decode("utf-8"))

    if socks.get(socketPT) == zmq.POLLIN:
        message = socketPT.recv_multipart()
        print("PT Zipcode: " + bytes.join(b'', message).decode("utf-8"))

    time.sleep(0.1)