from utils import load_json_file, get_country
from path_selection import select_path
import geoip2.database
import json

def main():
    relays = load_json_file("data/tor_consensus.json")
    config = load_json_file("data/Project2ClientInput.json")
    alliances = config["alliances"]
    trust_map = {c: v for group in alliances for c, v in group.items()}
    client_ip = config["client"]
    dest_ip = config["destination"]

    # GeoIP setup
    reader = geoip2.database.Reader("GeoLite2-Country.mmdb")
    client_country = get_country(client_ip, reader)
    dest_country = get_country(dest_ip, reader)

    # Atribuir país aos relays
    for r in relays:
        r["country"] = get_country(r["ip"], reader)

    path = select_path(relays, trust_map, client_country, dest_country, {}, {})

    with open("output/selected_path.json", "w") as f:
        json.dump(path, f, indent=2)

if __name__ == "__main__":
    main()
