from pydantic import BaseModel

class Coordinates(BaseModel):
    longitude: float
    latitude: float
    speed: float
    fix_status: int
    track: float
    time_of_acquisition: str



    '''
    "lon": self.gps_module.longitude,
    "lat": self.gps_module.latitude,
    "speed": self.gps_module.speed,
    "fix_status": self.gps_module.fix_status,
    "track": self.gps_module.track,
    "time_of_acquisition": datetime.now(timezone.utc).isoformat()'''