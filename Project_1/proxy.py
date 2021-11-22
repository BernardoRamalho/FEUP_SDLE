import signal
import sys
from auxClasses import Proxy

# Signal Handler for Ctrl+C
def signal_handler(sig, frame):
    print('Closing Proxy!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

proxy = Proxy()
proxy.run()