from auxClasses import Publisher
import sys
import signal
import time

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Publisher!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Script is run "publisher.py topic_name n_puts"
arguments = sys.argv[1:]

if len(arguments) < 2 or len(arguments) > 3:
    print("Numbers of arguments is not corret. Script is run as 'publisher.py topic_name n_puts [time_between_puts]'.")
    sys.exit(0)

pub = Publisher(arguments[0])

wait = False

# Check if there is any wait time between gets
if len(arguments) == 3:
    wait = True

    # Check if user inputed a correct value
    if not arguments[2].isdigit():
        print("Error in arguments. Value was not a digit for time_between_puts. Script is run as 'publisher.py topic_name n_puts [time_between_puts]'.")
        sys.exit(0)

    time_to_wait = int(arguments[2])

while pub.num_put_message != int(arguments[1]):
    pub.put()
    if wait:
        print("Waiting before next put...")
        time.sleep(time_to_wait)

