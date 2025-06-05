from trust_model import guard_security, exit_security
import random
from utils import is_guard_relay, is_exit_relay, is_middle_relay

def select_path(relays, trust_map, client_country, dest_country, guard_params, exit_params):
    guards = [r for r in relays if is_guard_relay(r)]
    exits = [r for r in relays if is_exit_relay(r)]
    middles = [r for r in relays if is_middle_relay(r)]

    print(f"Total guards: {len(guards)}, exits: {len(exits)}, middles: {len(middles)}")

    # Guard selection
    guard_scores = guard_security(client_country, guards, trust_map)
    try:
        best_guard = categorize_and_select(guard_scores, guard_params)
    except Exception as e:
        print("Guard selection falhou: fallback para melhor score")
        best_guard = sorted(guard_scores, key=lambda x: x[1], reverse=True)[0][0]

    # Exit selection com base no guard
    exit_scores = [(e, exit_security(client_country, dest_country, best_guard, e, trust_map)) for e in exits]
    try:
        # Escolhher a melhor saida
        best_exit = categorize_and_select(exit_scores, exit_params)
    except Exception as e:
        print("Exit selection falhou: fallback para melhor score")
        best_exit = sorted(exit_scores, key=lambda x: x[1], reverse=True)[0][0]

    # Middle aleatório
    # TODO: melhorar a escolha do middle
    middle = random.choice(middles)

    return {
        "guard": best_guard["fingerprint"],
        "middle": middle["fingerprint"],
        "exit": best_exit["fingerprint"]
    }


def categorize_and_select(relay_scores, params):
    sorted_relays = sorted(relay_scores, key=lambda x: x[1], reverse=True)
    total_bw = sum(r["bandwidth"]["measured"] for r, _ in sorted_relays)

    def filter_by_score(threshold):
        return [(r, s) for r, s in sorted_relays if s >= threshold]

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
