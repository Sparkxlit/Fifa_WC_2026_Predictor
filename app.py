import streamlit as st
import pandas as pd
from PIL import Image
import os
from Knockout_sim import simulate_full_knockout
from Knockout_sim import (
    simulate_full_knockout,
    R32,
    R16_FLOW,
    QF_FLOW,
    SF_FLOW,
    FINAL_FLOW,
    build_next_round
)
st.set_page_config(
    page_title="FIFA World Cup 2026 Predictor",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================
BASE_DIR = os.path.dirname(__file__)

df = pd.read_csv(
    os.path.join(BASE_DIR, "winner_probabilities.csv")
)

matches_df = pd.read_csv(
    os.path.join(BASE_DIR, "WC26_Grp_Performance.csv")
)
df = df.sort_values("Winner %", ascending=False).reset_index(drop=True)


def build_group_standings(df):

    standings = {}

    for group in df["group"].unique():
        group_matches = df[df["group"] == group]
        teams = pd.unique(
            group_matches[["teamA", "teamB"]].values.ravel()
    )

        table = pd.DataFrame(index=teams)
        table["M"] = 0
        table["W"] = 0
        table["D"] = 0
        table["L"] = 0
        table["Pt"] = 0
        table["GF"] = 0
        table["GA"] = 0
        table["GD"] = 0

        for _, row in group_matches.iterrows():

            # skip unfinished matches
            if pd.isna(row["scoreA"]) or pd.isna(row["scoreB"]):
                continue

            a = row["teamA"]
            b = row["teamB"]

            sa = int(row["scoreA"])
            sb = int(row["scoreB"])

            table.loc[a, "M"] += 1
            table.loc[b, "M"] += 1

            table.loc[a, "GF"] += sa
            table.loc[a, "GA"] += sb

            table.loc[b, "GF"] += sb
            table.loc[b, "GA"] += sa

            if sa > sb:
                table.loc[a, "W"] += 1
                table.loc[b, "L"] += 1
                table.loc[a, "Pt"] += 3

            elif sb > sa:
                table.loc[b, "W"] += 1
                table.loc[a, "L"] += 1
                table.loc[b, "Pt"] += 3

            else:
                table.loc[a, "D"] += 1
                table.loc[b, "D"] += 1
                table.loc[a, "Pt"] += 1
                table.loc[b, "Pt"] += 1

        table["GD"] = table["GF"] - table["GA"]

        table = table.sort_values(
            by=["Pt", "GD", "GF"],
            ascending=False
        )

        standings[group] = table.reset_index().rename(
            columns={"index": "Team"}
        )

    return standings

group_tables = build_group_standings(matches_df)

# split into 2 columns (24 each)
left_df = df.iloc[:24]
right_df = df.iloc[24:]

# =========================
# CSS
# =========================
st.markdown("""
<style>
body {
    background-color: #03132a;
}

.stApp {
    background: linear-gradient(to bottom, #021225, #071f42);
    color: white;
}

.main-title {
    text-align: center;
    font-size: 60px;
    font-weight: 900;
    color: white;
    margin-top: -30px;
}

.sub-title {
    text-align: center;
    font-size: 28px;
    color: gold;
    font-weight: bold;
}

.section-box {
    background: rgba(10,20,40,0.85);
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.15);
}

.rank-box {
    background: rgba(0,0,0,0.4);
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 8px;
}

.team-name {
    color: white;
    font-size: 22px;
    font-weight: bold;
}

.win-pct {
    color: #00ff66;
    font-size: 22px;
    font-weight: bold;
}

.sidebar .sidebar-content {
    background: #021225;
}

.stat-box {
    background: rgba(0,0,0,0.4);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
            
.stContainer {
    background: rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 18px;
}
            
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER BANNER
# =========================
banner_path = os.path.join(os.path.dirname(__file__), "banner.png")
banner = Image.open(banner_path)

st.image(banner, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
# host flags

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚽ MENU")
page = st.sidebar.radio(
    "",
    [   
        "Group Stage",
        "Winner Prediction",
        "Knockout Bracket",
        "About"
    ]
)

# =========================
# GROUP STAGE PAGE
# =========================
if page == "Group Stage":

    st.markdown("## 🌍 Group Stage")

    groups_path = os.path.join(os.path.dirname(__file__), "groups.png")
    groups_img = Image.open(groups_path)

    st.image(groups_img, use_container_width=True)

    st.markdown("---")
    st.markdown("## 📊 Live Group Standings")

    group_df = pd.read_csv("WC26_Grp_Performance.csv")
    groups = sorted(group_df["group"].unique())

    # Header
    for i in range(0, len(groups), 2):
        col1, col2 = st.columns(2, gap="small")

        for idx, col in enumerate([col1, col2]):
            if i + idx < len(groups):
                grp = groups[i + idx]
                standings_df = group_tables[grp]

                with col:
                    with st.container(border=True):
                        st.markdown(f"### Group {grp}")

                        h = st.columns([4,1,1,1,1,1,1,1,1])

                        h[0].markdown("**TEAM**")
                        h[1].markdown("**M**")
                        h[2].markdown("**W**")
                        h[3].markdown("**D**")
                        h[4].markdown("**L**")
                        h[5].markdown("**Pt**")
                        h[6].markdown("**GF**")
                        h[7].markdown("**GA**")
                        h[8].markdown("**GD**")

                        st.markdown("---")

                        for _, row in standings_df.iterrows():

                            team = row["Team"]
                            flag_path = f"flags/{team}.png"

                            cols = st.columns([4,1,1,1,1,1,1,1,1])

                            # TEAM COLUMN
                            with cols[0]:

                                c1, c2 = st.columns([1,4])

                                with c1:
                                    if os.path.exists(flag_path):
                                        st.image(flag_path, width=25)

                                with c2:
                                    st.markdown(
                                        f"<span style='color:white'>{team}</span>",
                                        unsafe_allow_html=True
                                    )

                            cols[1].markdown(f"<span style='color:white'>{row['M']}</span>", unsafe_allow_html=True)
                            cols[2].markdown(f"<span style='color:white'>{row['W']}</span>", unsafe_allow_html=True)
                            cols[3].markdown(f"<span style='color:white'>{row['D']}</span>", unsafe_allow_html=True)
                            cols[4].markdown(f"<span style='color:white'>{row['L']}</span>", unsafe_allow_html=True)
                            cols[5].markdown(f"<span style='color:white'>{row['Pt']}</span>", unsafe_allow_html=True)
                            cols[6].markdown(f"<span style='color:white'>{row['GF']}</span>", unsafe_allow_html=True)
                            cols[7].markdown(f"<span style='color:white'>{row['GA']}</span>", unsafe_allow_html=True)
                            cols[8].markdown(f"<span style='color:white'>{row['GD']}</span>", unsafe_allow_html=True)

# =========================
# WINNER PREDICTION PAGE
# =========================
elif page == "Winner Prediction":

    st.markdown("## 🏆 Winner Prediction")

    #Dynamic Simulation
    if st.button("🔄 RUN NEW SIMULATION"):
        results = simulate_full_knockout()
        st.session_state.knockout_results = results
        st.success("Simulation completed!")

    col1, col2 = st.columns(2, gap="small")

    # LEFT TABLE
    with col1:
        with st.container(border=True):

            st.markdown("""
            <div style="
            display:flex;
            justify-content:space-between;
            padding: 0 20px 15px 60px;
            font-size:22px;
            font-weight:bold;
            color:white;
            border-bottom:1px solid rgba(255,255,255,0.15);
            margin-bottom:15px;
            ">
                <div>Team</div>
                <div>Win %</div>
            </div>
            """, unsafe_allow_html=True)

            for i, row in left_df.iterrows():

                team = row["Team"]
                pct = row["Winner %"]

                flag_path = f"flags/{team}.png"

                cols = st.columns([1, 6, 2])

                with cols[0]:
                    if os.path.exists(flag_path):
                        st.image(flag_path, width=40)

                with cols[1]:
                    st.markdown(
                        f'<div class="team-name">{i+1}. {team}</div>',
                        unsafe_allow_html=True
                    )

                with cols[2]:
                    st.markdown(
                        f'<div class="win-pct">{pct:.2f}%</div>',
                        unsafe_allow_html=True
                    )

    # RIGHT TABLE
    with col2:
        with st.container(border=True):

            st.markdown("""
            <div style="
            display:flex;
            justify-content:space-between;
            padding: 0 20px 15px 60px;
            font-size:22px;
            font-weight:bold;
            color:white;
            border-bottom:1px solid rgba(255,255,255,0.15);
            margin-bottom:15px;
            ">
                <div>Team</div>
                <div>Win %</div>
            </div>
            """, unsafe_allow_html=True)

            for i, row in right_df.iterrows():

                team = row["Team"]
                pct = row["Winner %"]

                flag_path = f"flags/{team}.png"

                cols = st.columns([1, 6, 2])

                with cols[0]:
                    if os.path.exists(flag_path):
                        st.image(flag_path, width=40)

                with cols[1]:
                    st.markdown(
                        f'<div class="team-name">{i+1}. {team}</div>',
                        unsafe_allow_html=True
                    )

                with cols[2]:
                    st.markdown(
                        f'<div class="win-pct">{pct:.2f}%</div>',
                        unsafe_allow_html=True
                    )

    st.markdown("")

# =========================
# KNOCKOUT BRACKET PAGE
# =========================
elif page == "Knockout Bracket":

    st.markdown("## 🏟 FIFA Style Knockout Bracket")

    if st.button("🔄 RUN NEW SIMULATION"):
        st.session_state.knockout_results = simulate_full_knockout()

    if "knockout_results" not in st.session_state:
        st.warning("Run a simulation first.")
    else:
        results = st.session_state.knockout_results

        c1, c2, c3, c4, c5 = st.columns(5)

        # helper function
        def show_match_box(team1, team2):
            with st.container(border=True):
                for team in [team1, team2]:
                    flag_path = os.path.join(BASE_DIR, "flags", f"{team}.png")

                    # wider text column
                    cols = st.columns([1, 6])

                    with cols[0]:
                        if os.path.exists(flag_path):
                            st.image(flag_path, width=22)

                    with cols[1]:
                        st.markdown(
                            f"""
                            <div style="
                                white-space: nowrap;
                                overflow: hidden;
                                text-overflow: ellipsis;
                                font-size: 14px;
                                line-height: 28px;
                            ">
                                {team}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        # ROUND OF 32
        with c1:
            st.markdown("### Round of 32")

            r32_order = [74, 77, 73, 75, 83, 84, 81, 82, 76, 78, 79, 80, 86, 88, 85, 87]
            for match_no in r32_order:
                fixture = R32[match_no]
                team1, team2 = fixture
                show_match_box(team1, team2)
                st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ROUND OF 16
        with c2:
            st.markdown("### Round of 16")
            st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)

            r16_matches = build_next_round(R16_FLOW, results["R32"])

            r16_order = [89, 90, 93, 94, 91, 92, 95, 96]
            for match_no in r16_order:
                fixture = r16_matches[match_no]
                team1, team2 = fixture
                show_match_box(team1, team2)
                st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

        # QUARTER FINALS
        with c3:
            st.markdown("### Quarter Finals")
            st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)

            qf_matches = build_next_round(QF_FLOW, results["R16"])

            qf_order = [97, 98, 99, 100]
            for match_no in qf_order:
                fixture = qf_matches[match_no]
                team1, team2 = fixture
                show_match_box(team1, team2)
                st.markdown("<div style='height:330px'></div>", unsafe_allow_html=True)

        # SEMI FINALS
        with c4:
            st.markdown("### Semi Finals")
            st.markdown("<div style='height:370px'></div>", unsafe_allow_html=True)

            sf_matches = build_next_round(SF_FLOW, results["QF"])

            sf_order = [101, 102]
            for match_no in sf_order:
                fixture = sf_matches[match_no]
                team1, team2 = fixture
                show_match_box(team1, team2)
                st.markdown("<div style='height:760px'></div>", unsafe_allow_html=True)

        # FINAL
        with c5:
            st.markdown("### Final")
            st.markdown("<div style='height:780px'></div>", unsafe_allow_html=True)

            final_matches = build_next_round(FINAL_FLOW, results["SF"])

            for match_no, fixture in final_matches.items():
                team1, team2 = fixture
                show_match_box(team1, team2)

            st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

            champion = results["Champion"]
            champion_flag = os.path.join(BASE_DIR, "flags", f"{champion}.png")

            st.markdown("### 🏆 Champion")

            with st.container(border=True):
                cols = st.columns([1, 4])

                with cols[0]:
                    if os.path.exists(champion_flag):
                        st.image(champion_flag, width=25)

                with cols[1]:
                    st.markdown(
                        f"<h4 style='color:gold'>{champion}</h3>",
                        unsafe_allow_html=True
                    )

# Bottom stats
b1, b2, b3 = st.columns(3, gap="large")

with b1:
    with st.container(border=True, height=220):
        st.markdown("""
        <div style="
            text-align:center;
            height:180px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
        ">
            <h3>HOST COUNTRIES</h3>
            <p>USA, Mexico, Canada</p>
        </div>
        """, unsafe_allow_html=True)

with b2:
    with st.container(border=True, height=220):
        st.markdown("""
        <div style="
            text-align:center;
            height:180px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
        ">
            <h3>TEAMS</h3>
            <h1>48</h1>
            <p>The Biggest World Cup Ever!</p>
        </div>
        """, unsafe_allow_html=True)

with b3:
    with st.container(border=True, height=220):
        st.markdown("""
        <div style="
            text-align:center;
            height:180px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
        ">
            <h3>TOURNAMENT DATES</h3>
            <h4>11 June - 19 July 2026</h4>
            <p>40 Days of Football</p>
        </div>
        """, unsafe_allow_html=True)
        