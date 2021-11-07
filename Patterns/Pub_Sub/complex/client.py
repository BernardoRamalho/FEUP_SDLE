import zmq
import sys
import time

context = zmq.Context()

zipcode = sys.argv[1]

socketUS = context.socket(zmq.SUB)
socketUS.connect('tcp://localhost:5555')
socketUS.setsockopt(zmq.SUBSCRIBE, zipcode.encode('utf-8'))

socketPT = context.socket(zmq.SUB)
socketPT.connect('tcp://localhost:5557')
socketPT.setsockopt(zmq.SUBSCRIBE, zipcode.encode('utf-8'))

poller = zmq.Poller()
poller.register(socketPT, zmq.POLLIN)
poller.register(socketUS, zmq.POLLIN)
sockets = [socketUS, socketPT]

while True:
    messages = zmq.select(sockets, [], [])[0]
    if(len(messages) > 0):
        for x in range(len(messages)):
            message = messages[0].recv()
            print("Received: " + message.decode('utf-8'))

    time.sleep(0.1)