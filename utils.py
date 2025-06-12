import json
from collections import defaultdict
import ipaddress

def is_in_family(fingerprint, relay):
    family_set = set(relay.get("family", []))
    return f"${fingerprint}" in family_set

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


def is_exit_relay(relay, destination_ip, destination_port=8080):
    try:
        dest_ip = ipaddress.ip_address(destination_ip)
    except ValueError:
        return False  # IP inválido

    rules = relay.get("exit", "").lower().split(",")

    for rule in rules:
        rule = rule.strip()
        if not rule:
            continue

        try:
            action, rest = rule.split(" ", 1)
            ip_range, port_range = rest.split(":")
        except ValueError:
            continue  # Regra mal formada, ignora

        # Verificação de IP
        if ip_range == "*":
            ip_ok = True
        else:
            try:
                ip_net = ipaddress.ip_network(ip_range, strict=False)
                ip_ok = dest_ip in ip_net
            except ValueError:
                ip_ok = False

        # Verificação de porta
        if port_range == "*":
            port_ok = True
        elif "-" in port_range:
            try:
                start, end = map(int, port_range.split("-"))
                port_ok = start <= destination_port <= end
            except ValueError:
                port_ok = False
        else:
            try:
                port_ok = int(port_range) == destination_port
            except ValueError:
                port_ok = False

        # Aplica a primeira regra que bate nos dois
        if ip_ok and port_ok:
            return action == "accept"

    # Se nenhuma regra aplicável foi encontrada
    return False

def is_guard_relay(relay, threshold=5_000_000):
    return relay["bandwidth"]["measured"] >= threshold

def is_middle_relay(relay):
    return not is_exit_relay(relay) and not is_guard_relay(relay)
