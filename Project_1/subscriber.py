import time
import sys
import signal
from auxClasses import Subscriber

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Subscriber!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Script in run "subscriber.py id topic_name [n_gets] [time_between_gets]"
arguments = sys.argv[1:]

if len(arguments) > 4 or len(arguments) < 2:
    print("Numbers of arguments is not corret. Script is run as 'subscriber.py id topic_name [n_gets] [time_between_gets]'.")
    sys.exit(0)

wait = False

# Check if there is any wait time between gets
if len(arguments) == 4:
    wait = True

    # Check if user inputed a correct value
    if not arguments[3].isdigit():
        print("Error in arguments. Value was not a digit for time_between_gets. Script is run as 'subscriber.py id topic_name [n_gets] [time_between_gets]")
        sys.exit(0)

    time_to_wait = float(arguments[3])

sub = Subscriber(arguments[0])

sub.subscribe(arguments[1])

if len(arguments) == 2:
    while True:
        sub.get(arguments[1])

        if wait:
            print("Waiting before next get...")
            time.sleep(time_to_wait)
else:
    for x in range(int(arguments[2])):
        sub.get(arguments[1])

        if wait:
            print("Waiting before next get...")
            time.sleep(time_to_wait)
        

sub.unsubscribe('fruit')
