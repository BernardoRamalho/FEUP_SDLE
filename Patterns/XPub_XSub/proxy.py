import zmq
import signal
import sys

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

# Create a Proxy that does the same loop and the broker from Dealer_Router Pattern
zmq.proxy(frontend, backend)

# We never reach this code
frontend.close()
backend.close()
context.term()