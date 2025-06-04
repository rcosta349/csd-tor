from trust_model import guard_security,exit_security
import random


def select_path(relays, trust_map, client_country, dest_country, guard_params, exit_params):
    guards = [r for r in relays if "Guard" in r["flags"]]
    exits = [r for r in relays if "Exit" in r["flags"]]
    middles = [r for r in relays if "Guard" not in r["flags"] and "Exit" not in r["flags"]]

    guard_scores = guard_security(client_country, guards, trust_map)
    exit_scores = [(e, exit_security(client_country, dest_country, g[0], e, trust_map)) for g in guard_scores for e in exits]

    # Escolher o melhor guard, exit e random middle
    best_guard = max(guard_scores, key=lambda x: x[1])[0]
    best_exit = max(exit_scores, key=lambda x: x[1])[0]
    middle = random.choice(middles)

    return {
        "guard": best_guard["fingerprint"],
        "middle": middle["fingerprint"],
        "exit": best_exit["fingerprint"]
    }
