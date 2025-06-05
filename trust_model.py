
DEFAULT_TRUST = 0.15

def guard_security(client_country, guards, trust_map):
    scores = []
    for guard in guards:
        country = guard.get("country")

        # Obtemos o grau de confiança no país do guard
        trust = trust_map.get(country, DEFAULT_TRUST)

        # Diminuimos a Trust se o cliente e o guard estão no mesmo país
        if country == client_country:
            trust -= 0.15

        scores.append((guard, trust))
    return scores


def exit_security(client_country, dest_country, guard, exit_node, trust_map):
    # Evita países em comum entre client→guard e exit→destination
    risk = 0
    if guard.get("country") == exit_node.get("country"):
        risk += 1
    if client_country == guard.get("country"):
        risk += 1
    if dest_country == exit_node.get("country"):
        risk += 1
    trust_exit = trust_map.get(exit_node.get("country"), 0)
    return trust_exit - risk
