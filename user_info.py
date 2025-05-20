from datetime import datetime
import pytz

class UserInfo:
    def __init__(self, longitude=0, latitude=0, time=None):
        self.longitude = longitude
        self.latitude = latitude
        self.time = time or datetime.now(pytz.UTC)

    def set_info(self, user_long, user_lat, user_time):
        self.longitude = float(user_long)
        self.latitude = float(user_lat)
        if user_time:
            self.time = datetime.fromisoformat(user_time)