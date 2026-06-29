import pandas as pd
import numpy as np
# =========================================
# FIFA WORLD CUP 2026 KNOCKOUT BRACKET
# =========================================

# ROUND OF 32
# Replace placeholders after group stage ends

R32 = {

    # Match 73
    73: ("South Africa", "Canada"),

    # Match 74
    74: ("Germany", "Paraguay"),

    # Match 75
    75: ("Netherlands", "Morocco"),

    # Match 76
    76: ("Brazil", "Japan"),

    # Match 77
    77: ("France", "Sweden"),

    # Match 78
    78: ("Ivory Coast", "Norway"),

    # Match 79
    79: ("Mexico", "Ecuador"),

    # Match 80
    80: ("England", "DR Congo"),

    # Match 81
    81: ("United States", "Bosnia and Herzegovina"),

    # Match 82
    82: ("Belgium", "Senegal"),

    # Match 83
    83: ("Portugal", "Croatia"),

    # Match 84
    84: ("Spain", "Austria"),

    # Match 85
    85: ("Switzerland", "Algeria"),

    # Match 86
    86: ("Argentina", "Cape Verde"),

    # Match 87
    87: ("Colombia", "Ghana"),

    # Match 88
    88: ("Australia", "Egypt")
}


# =========================================
# ROUND OF 16 FLOW
# =========================================

R16_FLOW = {

    # Match 89
    89: (74, 77),

    # Match 90
    90: (73, 75),

    # Match 91
    91: (76, 78),

    # Match 92
    92: (79, 80),

    # Match 93
    93: (83, 84),

    # Match 94
    94: (81, 82),

    # Match 95
    95: (86, 88),

    # Match 96
    96: (85, 87)
}


# =========================================
# QUARTER FINALS FLOW
# =========================================

QF_FLOW = {

    # Match 97
    97: (89, 90),

    # Match 98
    98: (93, 94),

    # Match 99
    99: (91, 92),

    # Match 100
    100: (95, 96)
}


# =========================================
# SEMI FINALS FLOW
# =========================================

SF_FLOW = {

    # Match 101
    101: (97, 98),

    # Match 102
    102: (99, 100)
}


# =========================================
# FINAL
# =========================================

FINAL_FLOW = {

    # Match 104
    104: (101, 102)
}

import os

BASE_DIR = os.path.dirname(__file__)

master_df = pd.read_csv(
    os.path.join(BASE_DIR, "master_team_features.csv")
)

wc_df = pd.read_csv(
    os.path.join(BASE_DIR, "WC26_Grp_Performance.csv")
)

def get_wc_form(team):

    played = []

    for _, row in wc_df.iterrows():

        if row["teamA"] == team:
            played.append({
                "gf": row["scoreA"],
                "ga": row["scoreB"],
                "pos": row["possessionA"],
                "shots": row["shotsA"],
                "sot": row["shots_on_targetA"],
                "cs": bool(row["clean_sheetA"])
            })

        elif row["teamB"] == team:
            played.append({
                "gf": row["scoreB"],
                "ga": row["scoreA"],
                "pos": row["possessionB"],
                "shots": row["shotsB"],
                "sot": row["shots_on_targetB"],
                "cs": bool(row["clean_sheetB"])
            })

    if len(played) == 0:
        return 0

    # ONLY LAST 3 MATCHES
    df = pd.DataFrame(played).tail(3)

    form_score = (
        df["gf"].mean()*4
        - df["ga"].mean()*3
        + df["pos"].mean()*0.50
        + df["shots"].mean()*0.20
        + df["sot"].mean()*0.30
        + df["cs"].mean()*2
    )

    return form_score

def simulate_match(teamA, teamB, knockout=False):

    A = master_df[master_df["team"] == teamA].iloc[0]
    B = master_df[master_df["team"] == teamB].iloc[0]

    formA = get_wc_form(teamA)
    formB = get_wc_form(teamB)

    strengthA = (
    (A["current_elo"]/2000)*0.15 +
    (A["avg_elo_last20"]/2000)*0.20 +
    A["win_rate_last20"]*0.15 +
    A["goals_for_avg_last20"]*0.10 -
    A["goals_against_avg_last20"]*0.08 +
    A["clean_sheet_rate"]*0.10 +
    A["deep_run_score"]*0.20 +
    A["knockout_win_rate"]*0.18 +
    formA*0.20
)

    strengthB = (
    (B["current_elo"]/2000)*0.10 +
    (B["avg_elo_last20"]/2000)*0.15 +
    B["win_rate_last20"]*0.15 +
    B["goals_for_avg_last20"]*0.10 -
    B["goals_against_avg_last20"]*0.08 +
    B["clean_sheet_rate"]*0.10 +
    B["deep_run_score"]*0.20 +
    B["knockout_win_rate"]*0.18 +
    formB*0.20
    )

    strengthA = max(strengthA, 0.01)
    strengthB = max(strengthB, 0.01)

    probA = strengthA / (strengthA + strengthB)
    
    goalsA = np.random.poisson(2 * probA)
    goalsB = np.random.poisson(2 * (1 - probA))

    winner = None

    if knockout:

        if goalsA == goalsB:

            # Extra time
            etA = np.random.binomial(1, probA * 0.35)
            etB = np.random.binomial(1, (1 - probA) * 0.35)

            goalsA += etA
            goalsB += etB

            if goalsA == goalsB:

                penA = A["penalty_strength"]
                penB = B["penalty_strength"]

                winner = teamA if penA >= penB else teamB

            else:
                winner = teamA if goalsA > goalsB else teamB

        else:
            winner = teamA if goalsA > goalsB else teamB

    return {
        "team_a": teamA,
        "team_b": teamB,
        "goals_a": goalsA,
        "goals_b": goalsB,
        "winner": winner
    }

def simulate_round(matches_dict, round_name):

    winners = {}

    for match_no, fixture in matches_dict.items():

        teamA, teamB = fixture

        winner = simulate_match_best_of_n(
            teamA,
            teamB,
            n=1000
        )

        winners[match_no] = winner

        print(
            f"{round_name} Match {match_no}: "
            f"{teamA} vs {teamB} "
            f"→ Winner: {winner}"
        )

    return winners


def build_next_round(flow_map, previous_winners):

    next_round = {}

    for match_no, (m1, m2) in flow_map.items():

        next_round[match_no] = (
            previous_winners[m1],
            previous_winners[m2]
        )

    return next_round


def simulate_match_best_of_n(teamA, teamB, n=1000):

    wins = {
        teamA: 0,
        teamB: 0
    }

    for _ in range(n):

        result = simulate_match(teamA, teamB, knockout=True)

        wins[result["winner"]] += 1

    winner = max(wins, key=wins.get)

    return winner

def simulate_full_knockout():

    print("\n===== ROUND OF 32 =====")
    r32 = simulate_round(R32, "R32")

    r16_matches = build_next_round(R16_FLOW, r32)

    print("\n===== ROUND OF 16 =====")
    r16 = simulate_round(r16_matches, "R16")

    qf_matches = build_next_round(QF_FLOW, r16)

    print("\n===== QUARTER FINALS =====")
    qf = simulate_round(qf_matches, "QF")

    sf_matches = build_next_round(SF_FLOW, qf)

    print("\n===== SEMI FINALS =====")
    sf = simulate_round(sf_matches, "SF")

    final_matches = build_next_round(FINAL_FLOW, sf)

    print("\n===== FINAL =====")
    final = simulate_round(final_matches, "FINAL")

    champion = list(final.values())[0]

    print(f"\n🏆 Champion: {champion}")

    return {
        "R32": r32,
        "R16": r16,
        "QF": qf,
        "SF": sf,
        "FINAL": final,
        "Champion": champion
    }
