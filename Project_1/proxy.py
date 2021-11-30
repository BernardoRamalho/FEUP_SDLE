import signal
import sys
from auxClasses import Proxy

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Proxy!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Script is run "proxy.py time_between_save"
if len(sys.argv) != 2:
    print("Wrong arguments give. Script is run 'proxy.py time_between_save'")
    sys.exit(0)

arguments = sys.argv[1:]

if not arguments[0].isdigit():
    print("Argument given is not a digit. Script is run 'proxy.py time_between_save'")
    sys.exit(0)

proxy = Proxy(arguments[0])
proxy.run()