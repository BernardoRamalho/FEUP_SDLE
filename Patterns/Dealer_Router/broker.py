import zmq
import time

context = zmq.Context()

frontend = context.socket(zmq.ROUTER)
frontend.bind("tcp://*:5555")

backend = context.socket(zmq.DEALER)
backend.bind("tcp://*:5560")

poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

while True:
    socks = dict(poller.poll())

    if socks.get(frontend) == zmq.POLLIN:
        message = frontend.recv_multipart()
        backend.send_multipart(message)

    if socks.get(backend) == zmq.POLLIN:
        message = backend.recv_multipart()
        frontend.send_multipart(message)


    time.sleep(0.1)
