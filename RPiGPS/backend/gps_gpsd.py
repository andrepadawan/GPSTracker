#Modules
import time
import gps
import threading
import logging
from Coordinates import Coordinates


logger = logging.getLogger("gps_gpsd")
logging.basicConfig(format="%(asctime)s — %(name)s — %(levelname)s — %(message)s",
    level=logging.INFO)
class GpsReader: 

    def __init__(self):

        self.coord : Coordinates | None = None
        self._coord_available: False
        # Management variable: lock, threading and event management
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()
        self._connected_to_gps = False
    
    def start(self):

        #Checking no other gps thread is alive, if positive return -> no effect
        if self._thread is not None and self._thread.is_alive():
            return
        
        #Clearing the way for a new thread 
        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self.gps_loop, 
            name = "gps_thread",
            daemon = True)
        
        self._thread.start()
        logger.info("Thread GPS avviato")
        

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)
        
        logger.info("Thread GPS terminato")

    def write_coordinates(self, report):
        #Acquiring lock in order to write correctly without concurrency issues
        with self._lock:
            #For the sake of this project no other information is necessary
            self.coord = Coordinates(report["lon"], report["lat"],
                                     report["speed"], report["fix"],
                                     report["track"], report["time"])
            self._coord_available = True #this is needed in case a call to get_coordinates is made before
            #actually having the values

            logger.info(f"Coordinates: {self.coord.toString()}")

    def get_coordinates(self) -> Coordinates:
        if self._coord_available:
            with self._lock:
                return self.coord

    def gps_loop(self):

        """
        What should I do here?
        - study code in order to manage dropped connections (try: catch blocks)
        - thread should continuously cycle to get the position (inner cycle perhaps)
        - 
        """

        #Continuing connecting until stop event (external)
        while not self._stop_event.is_set():

            #establishing a connection with gpsd daemon
            session = gps.gps(mode=gps.WATCH_ENABLE)
            self._connected_to_gps = True

            #trying to connect
            try:
                #while connected, update as many times TPV report
                while 0 == session.read():
                    
                    #generating my report
                    report = session.next()
                    self.evaluate_report(report)

            #except falls here in case of dropped connection
            except StopIteration:
                self._connected_to_gps = False
                logger.warning("Connessione persa. Riconnetto...")
            
            except ConnectionRefusedError:
                logger.warning("Connessione rifiutata")

            except Exception as e:
                self._connected_to_gps = False
                logger.warning(f"Errore generico: {e}")

            self._stop_event.wait(3)
                    
    def evaluate_report(self, report):

        #Checking if we have a valid TPV
        if report["class"] == "TPV":

            #Valid TPV report! Now let's see if we have enough satellites
            if report["mode"] >= gps.MODE_2D:

                self.write_coordinates(report)
        else:
            return
