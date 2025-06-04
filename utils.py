import json
import geoip2.database

def load_json_file(path):
    with open(path, "r") as f:
        return json.load(f)

def get_country(ip_address, reader):
    try:
        return reader.country(ip_address).country.iso_code
    except:
        return None
