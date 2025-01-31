import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="Assistant Manager Points Tracker", page_icon="⚽", layout="wide"
)

# Define file paths
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
POINTS_FILE = os.path.join(BASE_DIR, "data", "assistant_manager_points.csv")
RESULTS_FILE = os.path.join(BASE_DIR, "data", "results.csv")

# Team logos (using Wikipedia SVG links)
TEAM_LOGOS = {
    "Man Utd": "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg",
    "Liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
    "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
    "Chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/9/9a/Aston_Villa_FC_new_crest.svg",
    "Crystal Palace": "https://upload.wikimedia.org/wikipedia/en/a/a2/Crystal_Palace_FC_logo_%282022%29.svg",
    "Brentford": "https://upload.wikimedia.org/wikipedia/en/2/2a/Brentford_FC_crest.svg",
    "Leicester": "https://upload.wikimedia.org/wikipedia/en/2/2d/Leicester_City_crest.svg",
    "Spurs": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
    "Nottingham Forest": "https://upload.wikimedia.org/wikipedia/en/e/e5/Nottingham_Forest_F.C._logo.svg",
    "Man City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
    "Newcastle": "https://upload.wikimedia.org/wikipedia/en/5/56/Newcastle_United_Logo.svg",
    "Brighton": "https://upload.wikimedia.org/wikipedia/en/f/fd/Brighton_%26_Hove_Albion_logo.svg",
    "Fulham": "https://upload.wikimedia.org/wikipedia/en/e/eb/Fulham_FC_%28shield%29.svg",
    "Bournemouth": "https://upload.wikimedia.org/wikipedia/en/e/e5/AFC_Bournemouth_%282013%29.svg",
    "Ipswich": "https://upload.wikimedia.org/wikipedia/en/4/43/Ipswich_Town.svg",
    "West Ham": "https://upload.wikimedia.org/wikipedia/en/c/c2/West_Ham_United_FC_logo.svg",
    "Everton": "https://upload.wikimedia.org/wikipedia/en/7/7c/Everton_FC_logo.svg",
    "Wolves": "https://upload.wikimedia.org/wikipedia/en/f/fc/Wolverhampton_Wanderers.svg",
    "Southampton": "https://upload.wikimedia.org/wikipedia/en/c/c9/FC_Southampton.svg",
}

# Manager & price data
TEAM_MANAGER_DATA = {
    "Arsenal": ("Mikel Arteta", "£1.5m"),
    "Chelsea": ("Enzo Maresca", "£1.5m"),
    "Liverpool": ("Arne Slot", "£1.5m"),
    "Man City": ("Pep Guardiola", "£1.5m"),
    "Newcastle": ("Eddie Howe", "£1.5m"),
    "Bournemouth": ("Andoni Iraola", "£1.1m"),
    "Brighton": ("Fabian Hurzeler", "£1.1m"),
    "Fulham": ("Marco Silva", "£1.1m"),
    "Nottingham Forest": ("Nuno Espirito Santo", "£1.1m"),
    "Spurs": ("Ange Postecoglou", "£1.1m"),
    "Aston Villa": ("Unai Emery", "£0.8m"),
    "Brentford": ("Thomas Frank", "£0.8m"),
    "Crystal Palace": ("Oliver Glasner", "£0.8m"),
    "Man Utd": ("Ruben Amorim", "£0.8m"),
    "Wolves": ("Vitor Pereira", "£0.8m"),
    "Everton": ("David Moyes", "£0.5m"),
    "Ipswich": ("Kieran McKenna", "£0.5m"),
    "Leicester": ("Ruud van Nistelrooy", "£0.5m"),
    "Southampton": ("Ivan Juric", "£0.5m"),
    "West Ham": ("Graham Potter", "£0.5m"),
}

# Custom CSS for a dark theme (including new “.stat-cards-container” and “.stat-card” classes)
st.markdown(
    """
<style>

/* Global dark background and light text */
html, body, [class*="css"] {
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
    font-size: 15px !important;
    background-color: #1e1e1e !important; 
    color: #eaeaea !important;
}

.block-container {
    padding: 1rem 2rem;
}

/* Headings in white */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

/* Container for summary stat cards */
.stat-cards-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 20px;
}

/* Individual stat card */
.stat-card {
    background-color: #2b2b2b;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    width: 220px;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    text-align: center;
}

.stat-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.stat-title {
    font-weight: bold;
    margin-bottom: 3px;
    color: #fff;
}

.stat-value {
    font-size: 18px;
    font-weight: 500;
    color: #eaeaea;
}

/* Team row container */
.team-row {
    display: flex;
    align-items: center;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 5px;
    background-color: #2b2b2b;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    color: #eaeaea !important;
}

.team-row:nth-child(even) {
    background-color: #3a3a3a;
}

.team-row div {
    text-align: center;
    flex: 1;
}

/* The first column left-aligned for the team name + logo */
.team-row div:first-child {
    text-align: left !important;
    display: flex;
    align-items: center;
}

/* Header row styling */
.header-row {
    font-weight: bold;
    background-color: #444444 !important; 
    color: #ffffff !important;
    margin-bottom: 10px;
    border-radius: 6px;
}

.header-row div {
    padding: 10px 0 !important;
}

/* Team logo adjustments */
.team-logo {
    width: 40px;
    height: 40px;
    object-fit: contain;
    margin-right: 10px;
    vertical-align: middle;
}

/* Match result container */
.match-result {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #2b2b2b;
    padding: 10px 20px;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    margin-bottom: 10px;
    gap: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.4);
    color: #eaeaea !important;
}

.home-team {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex: 1;
    gap: 5px;
}

.away-team {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex: 1;
    gap: 5px;
}

/* Score style */
.match-score {
    font-size: 1.2em;
    font-weight: bold;
    color: #ffffff;
    width: 80px;
    text-align: center;
}

/* DataFrame styling override for dark background */
[data-testid="stDataFrame"] {
    background-color: #2b2b2b !important;
    color: #eaeaea !important;
    border: 1px solid #3a3a3a !important;
}

.css-1nh1x9a svg { 
    display: none; /* Hide row index icon in dataframes */
}

/* Responsive design for mobile */
@media (max-width: 768px) {
    .stat-cards-container {
        flex-direction: column;
        align-items: center;
    }
    .stat-card {
        width: 100%; /* Full width for smaller screens */
    }
    .team-row, .match-result {
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
    }
    .match-score {
        width: auto;
        text-align: left;
    }
    .block-container {
        padding: 1rem;
    }
    h1, h2, h3 {
        font-size: 1.5rem;
    }
}

    .scrollable-container {
        overflow-x: auto; /* Enable horizontal scrolling */
        white-space: nowrap; /* Prevent wrapping of content */
    }

    .team-row, .header-row {
        display: flex;
        flex-wrap: nowrap; /* Prevent wrapping within rows */
    }

    .team-logo {
        width: 40px;
        height: 40px;
        object-fit: contain;
        margin-right: 10px;
        vertical-align: middle;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_points_data():
    return pd.read_csv(POINTS_FILE)


@st.cache_data
def load_results_data():
    return pd.read_csv(RESULTS_FILE)


def get_team_logo(team_name):
    return TEAM_LOGOS.get(team_name, "https://via.placeholder.com/50")


def get_manager_and_price(team_name):
    return TEAM_MANAGER_DATA.get(team_name, ("N/A", "N/A"))


def display_match_result(match):
    home_logo = get_team_logo(match["home"])
    away_logo = get_team_logo(match["away"])

    st.markdown(
        f"""
    <div class="match-result">
        <div class="home-team">
            <img src="{home_logo}" class="team-logo" alt="{match['home']} logo">
            <span>{match['home']}</span>
        </div>
        <div class="match-score">
            {match['home_score']} - {match['away_score']}
        </div>
        <div class="away-team">
            <span>{match['away']}</span>
            <img src="{away_logo}" class="team-logo" alt="{match['away']} logo">
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def get_league_position(points_df, selected_team):
    """
    Simple helper to determine the league position based on total_points.
    Ranks teams by descending total_points.
    """
    df = points_df.groupby("team")["total_points"].sum().reset_index()
    df.columns = ["Team", "TotalPoints"]
    df = df.sort_values("TotalPoints", ascending=False).reset_index(drop=True)
    # Create a dictionary {team_name -> rank}
    rank_dict = {row["Team"]: idx + 1 for idx, row in df.iterrows()}
    return rank_dict.get(selected_team, "N/A")


def main():
    st.title("🏆 Assistant Manager Points Tracker")

    # Sidebar for navigation
    page = st.sidebar.radio(
        "Navigate", ["Overall View", "Gameweek Points", "Team History", "About"], index=0
    )

    # Load data
    points_df = load_points_data()
    results_df = load_results_data()

    if page == "Overall View":
        st.subheader("Total Points by Club")

        # Calculate total points and other statistics for each team
        team_stats = (
            points_df.groupby("team")
            .agg({"total_points": "sum", "event": "count", "total_table_bonus": "sum"})
            .reset_index()
        )

        team_stats.columns = [
            "Team",
            "Total Points",
            "Games Played",
            "Total Table Bonus",
        ]
        team_stats["Avg Points"] = (
            team_stats["Total Points"] / team_stats["Games Played"]
        )
        team_stats = team_stats.sort_values("Total Points", ascending=False)
        team_stats["Logo"] = team_stats["Team"].apply(get_team_logo)

        # Header row
        st.markdown(
            """
         <div class="scrollable-container">
        <div class="team-row header-row">
            <div>Team</div>
            <div>Manager</div>
            <div>Price</div>
            <div>Total Points</div>
            <div>Games Played</div>
            <div>Avg Points</div>
            <div>Total Table Bonus</div>
        </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Display team rows
        # Display team rows inside the scrollable container
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        for _, row in team_stats.iterrows():
            manager, price = get_manager_and_price(row["Team"])
            st.markdown(
                f"""
            <div class="team-row">
                <div>
                    <img src="{row['Logo']}" class="team-logo">
                    {row['Team']}
                </div>
                <div>{manager}</div>
                <div>{price}</div>
                <div>{int(row['Total Points'])}</div>
                <div>{int(row['Games Played'])}</div>
                <div>{row['Avg Points']:.1f}</div>
                <div>{int(row['Total Table Bonus'])}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    elif page == "Gameweek Points":
        # 1. Collect all events and allow multi-selection
        all_events = sorted(points_df["event"].unique())

        # Set default selection to [1], if 1 exists in all_events
        default_selection = all_events[-1]

        selected_events = st.multiselect(
            "Select Gameweek(s)", all_events, default=default_selection
        )

        # 2. Stop if no events selected
        if not selected_events:
            st.warning("No Gameweek selected. Please pick at least one gameweek.")
            st.stop()

        # 3. Filter the points dataframe to only the selected events
        selected_event_points = points_df[
            points_df["event"].isin(selected_events)
        ].copy()
        selected_event_points["Total Points"] = selected_event_points["total_points"]

        # 4. Group by team and sum across all selected events
        aggregated_points = (
            selected_event_points.groupby("team", as_index=False)
            .agg(
                {
                    "total_points": "sum",
                    "total_win_points": "sum",
                    "total_goal_points": "sum",
                    "total_cs_points": "sum",
                    "total_table_bonus": "sum",
                }
            )
            .rename(columns={"total_points": "Total Points"})
        )

        # 5. Display a table of aggregated points
        event_list_str = ", ".join(map(str, selected_events))
        st.subheader(f"Assistant Points for Gameweek(s) {event_list_str}")
        st.dataframe(
            aggregated_points[
                [
                    "team",
                    "Total Points",
                    "total_win_points",
                    "total_goal_points",
                    "total_cs_points",
                    "total_table_bonus",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )

        # 6. Display match results event by event
        for ev in sorted(selected_events):
            st.subheader(f"Match Results for Gameweek {ev}")
            matches_for_this_event = results_df[results_df["event"] == ev]
            for _, match in matches_for_this_event.iterrows():
                display_match_result(match)

    elif page == "Team History":
        # 1. Choose Team
        teams = sorted(points_df["team"].unique())
        selected_team = st.selectbox("Select Team", teams)

        # 2. Filter and preprocess the team data
        team_history = points_df[points_df["team"] == selected_team].copy()
        team_history["Total Points"] = team_history["total_points"]

        # 3. Calculate key aggregates
        sum_total_points = team_history["total_points"].sum()
        games_played = len(team_history)
        average_points = sum_total_points / games_played if games_played else 0

        sum_win_points = team_history["total_win_points"].sum()  # e.g. for win
        sum_draw_points = team_history["total_draw_points"].sum()  # e.g. for draw
        sum_match_points = sum_win_points + sum_draw_points
        sum_goal_points = team_history["total_goal_points"].sum()
        sum_clean_sheet_points = team_history["total_cs_points"].sum()
        sum_table_bonus_points = team_history["total_table_bonus"].sum()

        current_league_position = get_league_position(points_df, selected_team)

        # 4. Display Team Header (logo + name)
        logo_url = get_team_logo(selected_team)
        st.markdown(
            f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="{logo_url}" style="width: 50px; height: 50px; margin-right: 15px; object-fit: contain;">
            <h2 style="margin: 0; color: #ffffff;">{selected_team}</h2>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # 5. Metrics Layout (two rows)
        # -- First row of 4 metrics --
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Points", sum_total_points)
        col2.metric("Avg Points", f"{average_points:.1f}")
        col3.metric("Games Played", games_played)
        col4.metric("Chip Position", current_league_position)

        # -- Second row of 4 metrics --
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Match Points", sum_match_points)
        col6.metric("Goal Points", sum_goal_points)
        col7.metric("Clean Sheet Points", sum_clean_sheet_points)
        col8.metric("Table Bonus", sum_table_bonus_points)

        # 6. Points History Table
        st.subheader(f"Points History for {selected_team}")
        team_history_display = team_history[
            [
                "event",
                "Total Points",
                "total_win_points",  # Win Points
                "total_draw_points",  # Draw Points
                "total_goal_points",  # Goal Points
                "total_cs_points",  # Clean Sheet
                "total_table_bonus",  # Table Bonus
            ]
        ].reset_index(drop=True)
        st.dataframe(team_history_display, hide_index=True, use_container_width=True)

        # 7. Match Results
        st.subheader(f"Match Results for {selected_team}")
        team_matches = results_df[
            (results_df["home"] == selected_team)
            | (results_df["away"] == selected_team)
        ]

        for _, match in team_matches.iterrows():
            display_match_result(match)

    elif page == "About":
        st.subheader("About Assistant Manager Points Tracker")
        st.markdown(
            """
        This application helps track assistant manager points across different events in the league.
        
        **Features:**
        - View overall points by club (including manager & price)
        - View points for each event
        - Explore a team's points history (now displayed using Streamlit's metric widgets!)
        - See match results
        
        **Points are calculated based on:**
        - Win Points
        - Goal Points
        - Clean Sheet Points
        - Table Bonus Points
        """
        )


if __name__ == "__main__":
    main()
