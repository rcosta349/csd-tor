import json
from collections import defaultdict

def build_pairwise_trust_map(alliances):
    trust_map = defaultdict(dict)

    for alliance in alliances:
        countries = alliance["countries"]
        trust = alliance["trust"]
        for a in countries:
            for b in countries:
                if a != b:
                    trust_map[a][b] = max(trust_map[a].get(b, 0), trust)
    return trust_map

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
