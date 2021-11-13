import zmq
import signal
import sys
import time

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Proxy!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Create XPUB and XSUB sockets
context = zmq.Context()

frontend = context.socket(zmq.XPUB)
frontend.bind("tcp://*:5555")

backend = context.socket(zmq.XSUB)
backend.bind("tcp://*:5560")

# Create Poller to handle the messages
poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

while True:
    # Wait for sockets to receive messages
    socks = dict(poller.poll())

    # Send messages to the other socket
    if socks.get(frontend) == zmq.POLLIN:
        message = frontend.recv_multipart()
        print("FT:")
        print(bytes.join(b'', message))
        backend.send_multipart(message)

    if socks.get(backend) == zmq.POLLIN:
        message = backend.recv_multipart()
        print("BK:")
        print(bytes.join(b'', message))
        frontend.send_multipart(message)

    time.sleep(0.1)

# We never reach this code
frontend.close()
backend.close()
context.term()