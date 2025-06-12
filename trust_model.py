from utils import is_in_family

DEFAULT_TRUST = 0.5

def guard_security(client_country, guards, alliances):
    for guard_relay in guards:
        guard_country = guard_relay.get("country")
        trust = DEFAULT_TRUST

        # TODO compare destination/guard
        for alliance in alliances:
            countries = alliance["countries"]

            if client_country in countries and guard_country in countries:
                trust = alliance["trust"]
                break

        if client_country == guard_country:
            trust *= 0.2

        guard_relay["trust"] = trust

def exit_security(client_country, dest_country, guard, exits, alliances):

    for exit_relay in exits:
        exit_country = exit_relay.get("country")
        trust = DEFAULT_TRUST

        # TODO compare exit/guard and exit/destination
        for alliance in alliances:
            countries = alliance["countries"]
            if client_country in countries and exit_country in countries:
                trust = alliance["trust"]
                break

        if is_in_family(guard["fingerprint"], exit_relay):
            trust *= 0.1

        if exit_relay.get("asn") == guard.get("asn"):
            trust *= 0.2

        if exit_country == guard.get("country"):
            trust *= 0.4

        if exit_country == dest_country:
            trust *= 0.5

        if exit_country == client_country:
            trust *= 0.4

        exit_relay["trust"] = trust
