from utils import load_json_file, get_country
from path_selection import select_path
import geoip2.database
import json

GUARD_PARAMS = {
    'safe_upper': 0.95,
    'safe_lower': 2.0,
    'accept_upper': 0.5,
    'accept_lower': 5.0,
    'bandwidth_frac': 0.2
}

EXIT_PARAMS = {
    'safe_upper': 0.95,
    'safe_lower': 2.0,
    'accept_upper': 0.1,
    'accept_lower': 10.0,
    'bandwidth_frac': 0.2
}

def main():
    relays = load_json_file("data/tor_consensus.json")
    config = load_json_file("data/Project2ClientInput.json")
    alliances = config["Alliances"]
    trust_map = {c: v for group in alliances for c, v in group.items()}
    client_ip = config["Client"]
    dest_ip = config["Destination"]

    # GeoIP setup
    reader = geoip2.database.Reader("GeoLite2-Country.mmdb")
    client_country = get_country(client_ip, reader)
    dest_country = get_country(dest_ip, reader)

    # Atribuir país aos relays
    for r in relays:
        r["country"] = get_country(r["ip"], reader)

    path = select_path(relays, trust_map, client_country, dest_country, GUARD_PARAMS, EXIT_PARAMS)

    with open("output/selected_path.json", "w") as f:
        json.dump(path, f, indent=2)

if __name__ == "__main__":
    main()
