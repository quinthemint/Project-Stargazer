from pyvo import registry  # Access astronomical databases version >=1.6
from astropy.coordinates import SkyCoord # Coordinates manipulation
import astropy.units as u
from astroquery.simbad import Simbad
import re

IAU_CONSTELLATION_MAP = {
    "And": "Andromeda", "Ant": "Antlia", "Aps": "Apus", "Aql": "Aquila", "Aqr": "Aquarius", "Ara": "Ara",
    "Ari": "Aries", "Aur": "Auriga", "Boo": "Boötes", "Cae": "Caelum", "Cam": "Camelopardalis",
    "Cnc": "Cancer", "CVn": "Canes Venatici", "CMa": "Canis Major", "CMi": "Canis Minor",
    "Cap": "Capricornus", "Car": "Carina", "Cas": "Cassiopeia", "Cen": "Centaurus", "Cep": "Cepheus",
    "Cet": "Cetus", "Cha": "Chamaeleon", "Cir": "Circinus", "Col": "Columba", "Com": "Coma Berenices",
    "CrA": "Corona Australis", "CrB": "Corona Borealis", "Crv": "Corvus", "Crt": "Crater", "Cru": "Crux",
    "Cyg": "Cygnus", "Del": "Delphinus", "Dor": "Dorado", "Dra": "Draco", "Equ": "Equuleus",
    "Eri": "Eridanus", "For": "Fornax", "Gem": "Gemini", "Gru": "Grus", "Her": "Hercules", "Hor": "Horologium",
    "Hya": "Hydra", "Hyi": "Hydrus", "Ind": "Indus", "Lac": "Lacerta", "Leo": "Leo", "Lep": "Lepus",
    "Lib": "Libra", "LMi": "Leo Minor", "Lup": "Lupus", "Lyn": "Lynx", "Lyr": "Lyra", "Men": "Mensa",
    "Mic": "Microscopium", "Mon": "Monoceros", "Mus": "Musca", "Nor": "Norma", "Oct": "Octans", "Oph": "Ophiuchus",
    "Ori": "Orion", "Pav": "Pavo", "Peg": "Pegasus", "Per": "Perseus", "Phe": "Phoenix", "Pic": "Pictor",
    "PsA": "Pisces Austrinus", "Psc": "Pisces", "Pup": "Puppis", "Pyx": "Pyxis", "Ret": "Reticulum",
    "Sge": "Sagitta", "Sgr": "Sagittarius", "Sco": "Scorpius", "Scl": "Sculptor", "Sct": "Scutum",
    "Ser": "Serpens", "Sex": "Sextans", "Tau": "Taurus", "Tel": "Telescopium", "TrA": "Triangulum Australe",
    "Tri": "Triangulum", "Tuc": "Tucana", "UMa": "Ursa Major", "UMi": "Ursa Minor", "Vel": "Vela",
    "Vir": "Virgo", "Vol": "Volans", "Vul": "Vulpecula"
}

# RETRIEVE STAR RECORDS
CATALOGUE = "V/50" # the catalogue name in VizieR

# each resource in the VO has an identifier, called ivoid. For vizier catalogs,
# the VO ids can be constructed like this:
catalogue_ivoid = f"ivo://CDS.VizieR/{CATALOGUE}"
# the actual query to the registry
voresource = registry.search(ivoid=catalogue_ivoid)[0]

# We can print metadata information about the catalogue
# voresource.describe(verbose=True)

tables = voresource.get_tables()
print(f"In this catalogue, we have {len(tables)} tables.")
for table_name, table in tables.items():
    print(f"{table_name}: {table.description}")

# We can also extract the tables names for later use
tables_names = list(tables.keys())
tables_names

voresource.access_modes()

# get the first table of the catalogue
first_table_name = tables_names[0]

# execute a synchronous ADQL query
tap_service = voresource.get_service("tap")
tap_records = tap_service.search(
    f'''
    SELECT Name, RAJ2000, DEJ2000
    FROM "{first_table_name}"
    '''
)

custom_simbad = Simbad()
custom_simbad.add_votable_fields('main_id', 'ids')

def get_common_name(bsc_name):
    try:
        result = custom_simbad.query_object(bsc_name)
        if result is None:
            print(f"No result for '{bsc_name}'")
            return None

        print(f"Columns returned: {result.colnames}")

        # Find 'ids' field case-insensitive
        ids_field = None
        for col in result.colnames:
            if col.lower() == 'ids':
                ids_field = col
                break

        if ids_field is None:
            print("No 'ids' field found in result.")
            return None

        ids_data = result[ids_field][0]

        # Decode bytes if necessary
        if isinstance(ids_data, bytes):
            ids_str = ids_data.decode('utf-8')
        else:
            ids_str = ids_data

        print(f"ids string: {ids_str}")

        # Split full string by pipe '|'
        groups = ids_str.split('|')

        # Look for any token starting with "NAME " and return the name
        for group in groups:
            tokens = [t.strip() for t in group.split(';')]
            for token in tokens:
                if token.startswith("NAME "):
                    common_name = token[5:].strip()  # Remove "NAME " prefix
                    return common_name

        # If no common name found, fallback to main_id
        main_id = result['main_id'][0]
        if isinstance(main_id, bytes):
            main_id = main_id.decode('utf-8')
        return main_id

    except Exception as e:
        print(f"Error resolving '{bsc_name}': {e}")
        return None
    

def get_constellation(bsc_name):
    # Remove leading digits
    i = 0
    while i < len(bsc_name) and bsc_name[i].isdigit():
        i += 1
    name_part = bsc_name[i:].strip()

    # Extract last 3 characters (IAU constellation code)
    if len(name_part) >= 3:
        const_code = name_part[-3:]
        return IAU_CONSTELLATION_MAP[const_code]


def parse_bayer_designation(name):
    # Match patterns like "Kap2Scl", "AlpAnd", "Bet1Ori", etc.
    match = re.match(r"([A-Za-z]{3})(\d?)([A-Z][a-z]{2})$", name)
    if not match:
        # Remove leading digits (Flamsteed number)
        i = 0
        while i < len(name) and name[i].isdigit():
            i += 1
        designation = name[i:].strip()

        if len(designation) > 3:
            designation = designation[:3] + ' ' + designation[3:]
        designation = ' '.join(designation.split())

        return designation
    
    greek, number, constellation = match.groups()
    return f"{greek}{number} {constellation}".strip()


# Output file
output_path = "star_facts.dlpy"


# Define the record → fact string function
def record_to_fact(record):
    bayer_flam = record.get('BayerFlam', record.get('Name', '')).strip()

    ra_deg = record.get('RA_ICRS') or record.get('RAJ2000')
    dec_deg = record.get('DE_ICRS') or record.get('DEJ2000')

    if ra_deg is None or dec_deg is None:
        return None

    coord = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)
    ra_str = coord.ra.to_string(unit=u.hour, sep=' ', precision=1, pad=True)
    dec_str = coord.dec.to_string(sep=' ', precision=1, alwayssign=True, pad=True)

    parse = parse_bayer_designation(bayer_flam)
    proper_name = get_common_name(parse)
    constellation = get_constellation(parse)

    if bayer_flam != '':
        return f"+ star('{proper_name}', '{bayer_flam}', '{constellation}', '{ra_str}', '{dec_str}')"

# Write all facts to the output file
with open(output_path, "w", encoding="utf-8") as f:
    for record in tap_records:
        fact = record_to_fact(record)
        if fact:
            f.write(fact + "\n")


print(f"✅ Saved star facts to {output_path}")
