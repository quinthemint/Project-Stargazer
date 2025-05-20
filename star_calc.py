import math
from datetime import datetime
import pytz
from pyDatalog import pyDatalog

def initialize_datalog():
    pyDatalog.clear()

    pyDatalog.create_terms('X, Y, Z, Star, Constellation, constellation, star, is_in_constellation')

    + constellation('orion')
    + constellation('lyra')
    + constellation('centaurus')
    + constellation('carina')

    # common name, bayer designation, constellation, ra, dec
    + star('betelgeuse', '58Alp Ori', 'orion', '05 55 10.3', '+07 24 25')
    + star('rigel', '19Bet Ori', 'orion', '05 14 32.3', '-08 12 06')
    + star('bellatrix', '24Gam Ori', 'orion', '05 25 07.9', '+06 20 59')
    + star('mintaka', '34Del Ori', 'orion', '05 32 00.4', '-00 17 57')
    + star('alnilam', '46Eps Ori', 'orion', '05 36 12.8', '-01 12 06')
    + star('alnitak', '50Zet Ori', 'orion', '05 40 45.5', '-01 56 33')
    + star('saiph', '53Kap Ori', 'orion', '05 47 45.4', '-09 40 11')
    + star('meissa', '39Lam Ori', 'orion', '05 35 08.3', '+09 56 03')

    + star('vega', '3Alp Lyr', 'lyra', '18 36 56.3', '+38 47 01')
    + star('sheliak', '12Bet Lyr', 'lyra', '18 50 04.8', '+33 21 46')
    + star('sulafat', '14Gam Lyr', 'lyra', '18 58 56.6', '+32 41 22')
    + star('delta lyrae', '10Del1 Lyr', 'lyra', '18 53 24.6', '+36 58 45')
    + star('epsilon lyrae', '4Eps1 Lyr', 'lyra', '18 44 20.3', '+39 40 12')
    + star('zeta lyrae', '9Zet Lyr', 'lyra', '18 58 56.7', '+37 36 19')
    + star('eta lyrae', '8Eta Lyr', 'lyra', '18 54 36.7', '+39 40 12')

    + star('rigil kentaurus', '21Alp Cen', 'centaurus', '14 39 36.5', '-60 50 02')
    + star('toliman', '21Alp1 Cen', 'centaurus', '14 39 36.1', '-60 50 08')
    + star('proxima centauri', 'V645 Cen', 'centaurus', '14 29 42.9', '-62 40 46')
    + star('hadar', '17Bet Cen', 'centaurus', '14 03 49.4', '-60 22 23')
    + star('muhlifain', '34Gam Cen', 'centaurus', '14 43 03.6', '-48 57 45')
    + star('epsilon centauri', '35Eps Cen', 'centaurus', '14 45 14.6', '-53 28 26')
    + star('theta centauri', '3The Cen', 'centaurus', '13 55 32.4', '-48 13 00')
    + star('iota centauri', '1Iot Cen', 'centaurus', '13 50 41.8', '-36 16 36')

# utils for user info and reading llm json input

class UserInfo:
    def __init__(self, longitude=0, latitude=0, time=None):
        self.longitude = longitude
        self.latitude = latitude
        self.time = time or datetime.now(pytz.UTC)

    def set_info(self, user_long, user_lat, user_time):
        self.longitude = user_long
        self.latitude = user_lat
        self.time = user_time

user_info = UserInfo()

class Query:
    def __init__(self, constellation=None, star=None, ASKCONVIS=0, ASKSTAVIS=0, ASKSTAPAR=0, ASKCONCHI=0):
        self.constellation = constellation
        self.star = star
        self.ASKCONVIS = ASKCONVIS
        self.ASKSTAVIS = ASKSTAVIS
        self.ASKSTAPAR = ASKSTAPAR
        self.ASKCONCHI = ASKCONCHI

    def update_from_json(self, json_data):
        key_map = {
            'constellation': 'constellation',
            'star': 'star',
            'askconvis': 'ASKCONVIS',
            'askstavis': 'ASKSTAVIS',
            'askstapar': 'ASKSTAPAR',
            'askconchi': 'ASKCONCHI'
        }

        for raw_key, value in json_data.items():
            key = raw_key.strip().lower()
            if key in key_map:
                setattr(self, key_map[key], value)
    
    def handle_query(self):
        initialize_datalog()
        if self.ASKSTAVIS:
            if self.star is not None:
                return is_star_visible(self.star)

def calculate_lst(longitude, time):
    # Julian date for the given time
    jd = (time - datetime(2000, 1, 1, 12, tzinfo=pytz.UTC)).total_seconds() / 86400.0 + 2451545.0
    t = (jd - 2451545.0) / 36525.0
    gst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2 - t**3 / 38710000.0
    gst %= 360
    lst = (gst + longitude) % 360
    return lst

def hms_to_degrees(ra_hms, dec_dms):
    # Split the RA and Dec into components
    ra_h, ra_m, ra_s = map(float, ra_hms.split())
    dec_d, dec_m, dec_s = map(float, dec_dms.split())
    
    # Convert RA to decimal degrees
    ra_deg = 15 * (ra_h + ra_m / 60 + ra_s / 3600)
    
    # Convert Dec to decimal degrees (accounting for negative values)
    if dec_d < 0:
        dec_deg = dec_d - dec_m / 60 - dec_s / 3600
    else:
        dec_deg = dec_d + dec_m / 60 + dec_s / 3600
    
    return ra_deg, dec_deg

def calculate_star_visibility(ra, dec, longitude, latitude, time):
    # Convert to degrees
    ra, dec = hms_to_degrees(ra, dec)

    # Calculate the LST for the given location and time
    lst = calculate_lst(longitude, time)
    
    # Calculate the hour angle (HA)
    ha = (lst - ra) % 360
    if ha > 180:  # Ensure HA is in the range [-180, 180]
        ha -= 360
    
    # Convert to radians for the altitude calculation
    ha_rad = math.radians(ha)
    dec_rad = math.radians(dec)
    lat_rad = math.radians(latitude)
    
    # Calculate altitude
    alt = math.degrees(math.asin(
        math.sin(dec_rad) * math.sin(lat_rad) +
        math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    ))

    alt_rad = math.asin(math.sin(dec_rad) * math.sin(lat_rad) +
                        math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad))
    alt = math.degrees(alt_rad)

    # Calculate Azimuth
    sin_az = -math.cos(dec_rad) * math.sin(ha_rad) / math.cos(alt_rad)
    cos_az = (math.sin(dec_rad) - math.sin(alt_rad) * math.sin(lat_rad)) / (math.cos(alt_rad) * math.cos(lat_rad))
    
    az = math.degrees(math.atan2(sin_az, cos_az))
    az = (az + 360) % 360  # Ensure Azimuth is in the range [0, 360]
    
    # Return true if the altitude is above the horizon
    return alt > 0, alt, az

def is_star_visible(star_name):
    # Query the database for the star by name
    result = pyDatalog.ask(f"star('{star_name}', Bayer, Constellation, RA, Dec)")
    
    if not result:
        print(f"Star '{star_name}' not found in the database.")
        return None

    # Extract the first (and should be only) result
    bayer, constellation, ra, dec = result.answers[0]

    # Calculate visibility
    is_visible, alt, az = calculate_star_visibility(ra, dec, user_info.longitude, user_info.latitude, user_info.time)

    # Return result as a dictionary or tuple
    return {
        'name': star_name,
        'bayer': bayer,
        'constellation': constellation,
        'visible': is_visible,
        'altitude': alt,
        'azimuth': az
    }

# Case: what constellation does ____ star belong to?
# star_name = ''
# is_in_constellation(Star, Constellation) <= star(Star, X, Constellation, Y, Z)
# result = is_in_constellation('vega', X)
# print(", ".join([x[0] for x in result]))

'''
Questions that can be answered:
- is ____ star visible?
- is ____ constellation visible?
- what stars are in ____ constellation?
- what constellation does ____ star belong to?
'''