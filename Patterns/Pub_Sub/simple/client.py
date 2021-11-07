import zmq

# Create Subscriber socket
context = zmq.Context()

socket = context.socket(zmq.SUB)
socket.connect('tcp://localhost:5555')
socket.setsockopt(zmq.SUBSCRIBE, b'status')

# Receive messages from the publisher
while True:
    message = socket.recv_multipart()
    print(f'Received: {message}')