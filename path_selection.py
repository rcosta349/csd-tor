from trust_model import guard_security, exit_security
import random
from utils import is_exit_relay

def select_path(relays, alliances, client_country, dest_country, guard_params, exit_params):
    exits = [r for r in relays if is_exit_relay(r)]
    guards = relays[:]
    middles = relays[:]

    #print(f"Total guards: {len(guards)}, exits: {len(exits)}, middles: {len(middles)}")

    # Guard Selection
    guard_security(client_country, guards, alliances)
    guards_sorted = sorted(guards, key=lambda g: g["trust"], reverse=True)
    # TODO organize with categorize_and_select
    best_guard = guards_sorted[0]


    # Exit Selection
    exit_security(client_country, dest_country, best_guard, exits, alliances)
    exits_sorted = sorted(exits, key=lambda e: e["trust"], reverse=True)
    # TODO organize with categorize_and_select
    best_exit = exits_sorted[0]


    # Remove guard and exit of middles list
    exclude_fingerprints = {best_guard["fingerprint"], best_exit["fingerprint"]}
    middles = [m for m in middles if m["fingerprint"] not in exclude_fingerprints]

    # Random Middle
    # TODO improve middle selection (maybe not necessary)
    middle = random.choice(middles)

    return {
        "guard": best_guard["fingerprint"],
        "middle": middle["fingerprint"],
        "exit": best_exit["fingerprint"]
    }


def categorize_and_select(relays, params):
    sorted_relays = sorted(relays, key=lambda r: r["trust"], reverse=True)
    total_bw = sum(r["bandwidth"]["measured"] for r in sorted_relays)

    def filter_by_score(threshold):
        return [r for r in sorted_relays if r["trust"] >= threshold]

    # SAFE
    safe = filter_by_score(params["safe_upper"])
    safe_subset = select_until_bandwidth(safe, total_bw, params["bandwidth_frac"], label="SAFE")
    if safe_subset:
        return random.choices(safe_subset, weights=[r["bandwidth"]["measured"] for r in safe_subset])[0]

    # ACCEPTABLE
    acceptable = filter_by_score(params["accept_upper"])
    accept_subset = select_until_bandwidth(acceptable, total_bw, params["bandwidth_frac"], label="ACCEPTABLE")
    if accept_subset:
        return random.choices(accept_subset, weights=[r["bandwidth"]["measured"] for r in accept_subset])[0]

    raise Exception("Nenhum relay satisfaz os parâmetros.")


def select_until_bandwidth(relay_scores, total_bw, threshold_frac, label=""):
    selected = []
    current_bw = 0

    for r, _ in relay_scores:
        selected.append(r)
        current_bw += r["bandwidth"]["measured"]
        if current_bw >= threshold_frac * total_bw:
            break

    print(f"[{label}] Selected {len(selected)} relays, accumulated_bw: {current_bw}, target: {threshold_frac * total_bw}")
    return selected if current_bw >= threshold_frac * total_bw else []
