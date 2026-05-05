import threading
import time
from Coordinates import Coordinates

class AtReader():

    def __init__(self):
        self.coordinates = Coordinates()
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()
        self._connected_to_gps = False



