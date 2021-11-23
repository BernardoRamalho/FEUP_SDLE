import signal
import sys
from auxClasses import Proxy

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Proxy!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Script is run "proxy.py time_between_save"
arguments = sys.argv[1:]

proxy = Proxy(arguments[0])
proxy.run()