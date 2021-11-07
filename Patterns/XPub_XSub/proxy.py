import zmq

context = zmq.Context()

frontend = context.socket(zmq.XPUB)
frontend.bind("tcp://*:5555")

backend = context.socket(zmq.XSUB)
backend.bind("tcp://*:5560")

# poller = zmq.Poller()
# poller.register(frontend, zmq.POLLIN)
# poller.register(backend, zmq.POLLIN)

zmq.proxy(frontend, backend)

frontend.close()
backend.close()
context.term()