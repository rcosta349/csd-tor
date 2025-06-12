from trust_model import guard_security, exit_security
import random
from utils import is_exit_relay

def select_path(relays, alliances, client_country, dest_country, dest_ip, guard_params, exit_params):
    exits = [r for r in relays if is_exit_relay(r,dest_ip)]
    guards = relays[:]

    # Guard Selection
    guard_security(client_country, guards, alliances)
    try:
        best_guard = categorize_and_select(guards,guard_params)
    except:
        guards_sorted = sorted(guards, key=lambda g: g["trust"], reverse=True)
        best_guard = guards_sorted[0]

    #Remove guard from exists list
    exclude_fingerprints = {best_guard["fingerprint"]}
    exits = [e for e in exits if e["fingerprint"] not in exclude_fingerprints]

    # Exit Selection
    exit_security(client_country, dest_country, best_guard, exits, alliances)
    try:
        best_exit = categorize_and_select(exits,exit_params)
    except:
        exits_sorted = sorted(exits, key=lambda e: e["trust"], reverse=True)
        best_exit = exits_sorted[0]

    # Remove guard and exit of middles list
    exclude_fingerprints = {best_guard["fingerprint"], best_exit["fingerprint"]}
    middles = [m for m in relays if m["fingerprint"] not in exclude_fingerprints]

    middle = select_middle_node(middles, best_guard, best_exit)

    return {
        "guard": best_guard["fingerprint"],
        "middle": middle["fingerprint"],
        "exit": best_exit["fingerprint"]
    }


def categorize_and_select(relays, params):
    #Sort relays by descending trust score
    sorted_relays = sorted(relays, key=lambda r: r["trust"], reverse=True)
    total_bw = sum(r["bandwidth"]["measured"] for r in sorted_relays)

    def filter_by_score(threshold):
        return [r for r in sorted_relays if r["trust"] >= threshold]

    # SAFE
    safe = filter_by_score(params["safe_upper"])
    safe_subset = select_until_bandwidth(
        safe,
        total_bw,
        params.get("bandwidth_frac", 0.2),
        label="SAFE"
    )
    if safe_subset:
        return random.choices(safe_subset, weights=[r["bandwidth"]["measured"] for r in safe_subset])[0]

    # ACCEPTABLE
    acceptable = filter_by_score(params["accept_upper"])
    accept_subset = select_until_bandwidth(
        acceptable,
        total_bw,
        params.get("bandwidth_frac", 0.2),
        label="ACCEPTABLE"
    )
    if accept_subset:
        return random.choices(accept_subset, weights=[r["bandwidth"]["measured"] for r in accept_subset])[0]

    raise Exception("No relay satisfies the defined parameters.")


# it will select the top 15 relays - (max_relays = 15)
def select_until_bandwidth(relays, total_bw, threshold_frac, label="", max_relays=15):
    selected = []
    current_bw = 0
    target_bw = threshold_frac * total_bw

    for r in relays[:max_relays]:  # Only the top N
        selected.append(r)
        current_bw += r["bandwidth"]["measured"]
        if current_bw >= target_bw:
            break

    #### Analise
    avg_trust = sum(r["trust"] for r in selected) / len(selected) if selected else 0
    print(f"[{label}] Selected {len(selected)} relays, accumulated_bw: {current_bw}, target: {threshold_frac * total_bw:.0f}, avg_trust: {avg_trust:.2f}")
    ####
    return selected if current_bw >= threshold_frac * total_bw else []


def select_middle_node(middles, best_guard, best_exit, max_attempts=15):
    guard_asn = best_guard.get("asn")
    exit_asn = best_exit.get("asn")
    guard_fam = set(best_guard.get("family", []))
    exit_fam = set(best_exit.get("family", []))

    attempts = 0
    candidate = None

    while attempts < max_attempts:
        candidate = random.choice(middles)
        middle_asn = candidate.get("asn")
        middle_fam = set(candidate.get("family", []))

        asn_conflict = (middle_asn == guard_asn) or (middle_asn == exit_asn)
        fam_conflict = not middle_fam.isdisjoint(guard_fam.union(exit_fam))

        if not asn_conflict and not fam_conflict:
            print("Middle candidate does not have conflict with ASN or Family of guard or exit.")
            return candidate

        attempts += 1

    print("Unable to guarantee ASN/family diversity in the middle node. Using last candidate.")
    return candidate