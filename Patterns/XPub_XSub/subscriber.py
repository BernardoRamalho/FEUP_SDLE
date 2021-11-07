import time
import zmq
import sys

context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')
topic = sys.argv[1]
socket.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))

while True:
    message = socket.recv_multipart()
    print(f'{message}')
    time.sleep(1)