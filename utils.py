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

def is_exit_relay(relay):
    return "accept" in relay.get("exit", "").lower()

def is_guard_relay(relay, threshold=5_000_000):
    return relay["bandwidth"]["measured"] >= threshold

def is_middle_relay(relay):
    return not is_exit_relay(relay) and not is_guard_relay(relay)
