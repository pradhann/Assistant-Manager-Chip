import requests
import json
import os
import pandas as pd
import logging
from datetime import datetime


class PremierLeaguePointsCalculator:
    def __init__(self):
        # Load teams dictionary
        self.teams_dict = {
            1: "Arsenal",
            2: "Aston Villa",
            3: "Bournemouth",
            4: "Brentford",
            5: "Brighton",
            6: "Chelsea",
            7: "Crystal Palace",
            8: "Everton",
            9: "Fulham",
            10: "Ipswich",
            11: "Leicester",
            12: "Liverpool",
            13: "Man City",
            14: "Man Utd",
            15: "Newcastle",
            16: "Nottingham Forest",
            17: "Southampton",
            18: "Spurs",
            19: "West Ham",
            20: "Wolves",
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s: %(message)s",
            filename="premier_league_points.log",
        )
        self.logger = logging.getLogger(__name__)

        # A default data directory for saving results
        self.data_dir = "data"

        # Initialize DataFrames
        self.match_results_df = pd.DataFrame()  # Raw match results
        self.league_positions_df = (
            pd.DataFrame()
        )  # The final event-by-event league table

    def fetch_fixtures(self):
        """
        Fetch fixtures from Fantasy Premier League API and store them in self.match_results_df
        """
        try:
            url = "https://fantasy.premierleague.com/api/fixtures/"
            response = requests.get(url)
            fixtures = response.json()

            # Transform fixtures into our required format
            results = []
            for fixture in fixtures:
                # Only include completed matches that have a non-null score
                if fixture.get("team_h_score") is not None:
                    results.append(
                        {
                            "event": fixture.get("event", 0),
                            "home": self.teams_dict.get(fixture["team_h"], "Unknown"),
                            "away": self.teams_dict.get(fixture["team_a"], "Unknown"),
                            "home_score": fixture.get("team_h_score", 0),
                            "away_score": fixture.get("team_a_score", 0),
                        }
                    )

            # Convert to DataFrame
            self.match_results_df = pd.DataFrame(results)

            # Ensure data directory exists
            os.makedirs(self.data_dir, exist_ok=True)

            # Save results to a CSV file
            file_name = "results.csv"
            file_path = os.path.join(self.data_dir, file_name)
            self.match_results_df.to_csv(file_path, index=False)
            self.logger.info(f"Saved results to {file_path}")

            # Log results
            self.logger.info(f"Fetched {len(results)} match results")

            return self.match_results_df

        except Exception as e:
            self.logger.error(f"Error fetching fixtures: {e}")
            raise

    def calculate_league_table(self):
        """
        Build a cumulative league table event by event, each time referencing
        the previous event's table to update points, goals, wins, draws, losses, etc.

        The final DataFrame (self.league_positions_df) will have:
        [event, team_name, position, points, goal_difference,
        goals_scored, goals_conceded, wins, draws, losses]

        Tie-breaking order:
        1) points (desc)
        2) goal_difference (desc)
        3) goals_scored (desc)
        If two teams share these stats exactly, they share the same position.
        """

        # 1) If we have no matches, try to fetch them
        if self.match_results_df.empty:
            self.fetch_fixtures()

        # 2) Sort matches by event
        self.match_results_df.sort_values(by="event", inplace=True)

        # 3) Identify all teams that appear in the fixture list
        all_teams = set(self.match_results_df["home"]) | set(
            self.match_results_df["away"]
        )

        # 4) Create the initial "event 0" standings (everyone at 0)
        #    This table will be updated cumulatively
        prev_event_df = pd.DataFrame(
            {
                "event": [0] * len(all_teams),
                "team_name": list(all_teams),
                "points": 0,
                "goals_scored": 0,
                "goals_conceded": 0,
                "goal_difference": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "position": 1,  # We can set them all to 1 or 0 for the initial snapshot
            }
        )

        # 5) Store the "initial" snapshot in self.league_positions_df (optional)
        self.league_positions_df = prev_event_df.copy(deep=True)

        # 6) List the unique (actual) events beyond 0
        all_events = sorted(self.match_results_df["event"].unique())

        # 7) Iterate over events in ascending order
        for ev in all_events:
            # Make a copy of the previous event's table
            current_event_df = prev_event_df.copy(deep=True)
            current_event_df["event"] = ev

            # Filter matches for this event
            ev_matches = self.match_results_df[self.match_results_df["event"] == ev]

            # For each match, update the relevant teams' stats in current_event_df
            for _, row in ev_matches.iterrows():
                home_team = row["home"]
                away_team = row["away"]
                home_score = row["home_score"]
                away_score = row["away_score"]

                # Locate rows for the home and away teams
                home_idx = current_event_df.index[
                    current_event_df["team_name"] == home_team
                ]
                away_idx = current_event_df.index[
                    current_event_df["team_name"] == away_team
                ]

                # Update goals scored/conceded
                current_event_df.loc[home_idx, "goals_scored"] += home_score
                current_event_df.loc[home_idx, "goals_conceded"] += away_score
                current_event_df.loc[away_idx, "goals_scored"] += away_score
                current_event_df.loc[away_idx, "goals_conceded"] += home_score

                # Update points & W-D-L
                if home_score > away_score:
                    # Home wins
                    current_event_df.loc[home_idx, "points"] += 3
                    current_event_df.loc[home_idx, "wins"] += 1
                    current_event_df.loc[away_idx, "losses"] += 1
                elif home_score < away_score:
                    # Away wins
                    current_event_df.loc[away_idx, "points"] += 3
                    current_event_df.loc[away_idx, "wins"] += 1
                    current_event_df.loc[home_idx, "losses"] += 1
                else:
                    # Draw
                    current_event_df.loc[home_idx, "points"] += 1
                    current_event_df.loc[away_idx, "points"] += 1
                    current_event_df.loc[home_idx, "draws"] += 1
                    current_event_df.loc[away_idx, "draws"] += 1

            # Recompute goal_difference for all teams
            current_event_df["goal_difference"] = (
                current_event_df["goals_scored"] - current_event_df["goals_conceded"]
            )

            # Sort by [points desc, goal_difference desc, goals_scored desc]
            current_event_df.sort_values(
                by=["points", "goal_difference", "goals_scored"],
                ascending=[False, False, False],
                inplace=True,
            )
            current_event_df.reset_index(drop=True, inplace=True)

            # Assign position with tie logic
            current_event_df.loc[0, "position"] = 1
            for i in range(1, len(current_event_df)):
                prev_row = current_event_df.loc[i - 1]
                curr_row = current_event_df.loc[i]
                # If there's a tie in (points, goal_diff, goals_scored), same position
                if (
                    curr_row["points"] == prev_row["points"]
                    and curr_row["goal_difference"] == prev_row["goal_difference"]
                    and curr_row["goals_scored"] == prev_row["goals_scored"]
                ):
                    current_event_df.loc[i, "position"] = current_event_df.loc[
                        i - 1, "position"
                    ]
                else:
                    current_event_df.loc[i, "position"] = i + 1

            # Append this event's table to our master league_positions_df
            # final columns in order
            final_cols = [
                "event",
                "team_name",
                "position",
                "points",
                "goal_difference",
                "goals_scored",
                "goals_conceded",
                "wins",
                "draws",
                "losses",
            ]
            # add to the final DataFrame
            self.league_positions_df = pd.concat(
                [self.league_positions_df, current_event_df[final_cols]],
                ignore_index=True,
            )

            # This updated table becomes "prev_event_df" for the next iteration
            prev_event_df = current_event_df[final_cols].copy()

        # Return the full event-by-event table
        return self.league_positions_df

    def calculate_assistant_manager_points(self):
        """
        Calculate Assistant Manager Points for each event and store them in
        self.assistant_manager_points_df.

        The logic:
        - Win = 6 points, Draw = 3 points, Loss = 0
        - +1 point per goal scored
        - +2 points for a clean sheet
        - Table bonus: if facing an opponent at least 5 positions higher
            at the start of the event:
                +10 points for a win, +5 for a draw

        We assume self.league_positions_df contains *cumulative* standings
        up to (event-1) with columns [event, team_name, position, ...].
        """

        # If there's no league table, we can't reference positions
        if self.league_positions_df.empty:
            raise ValueError(
                "league_positions_df is empty. Please calculate or fetch the league table first."
            )

        # If match_results_df is empty, fetch fixtures
        if self.match_results_df.empty:
            self.fetch_fixtures()

        # We will store all events' Assistant Manager Points in this list
        all_events_amp = []

        # Sort matches by event to process in ascending order
        self.match_results_df.sort_values("event", inplace=True)

        # Identify all unique events (e.g., 1, 2, 3, ...)
        events = sorted(self.match_results_df["event"].unique())

        for event in events:
            # -------------------------------------------------------
            # 1) Get the league table "before" this event starts
            # -------------------------------------------------------
            # Typically, that's the row where league_positions_df["event"] == event-1
            # But if event == 1 and there's no event=0 in league_positions_df,
            # we fallback to event 0 or all positions = 1.
            prev_event = event - 1
            prev_event_league_df = self.league_positions_df[
                self.league_positions_df["event"] == prev_event
            ]

            if prev_event_league_df.empty:
                # If we have *no* previous event data, assume all teams have position=1
                # or some default. We'll do a naive approach:
                unique_teams = pd.unique(self.league_positions_df["team_name"])
                prev_event_league_df = pd.DataFrame(
                    {"team_name": unique_teams, "position": 1}
                )

            # Create a dict: team_position[event-1]
            team_pos_dict = dict(
                zip(prev_event_league_df["team_name"], prev_event_league_df["position"])
            )

            # -------------------------------------------------------
            # 2) Gather all matches in this event
            # -------------------------------------------------------
            ev_matches = self.match_results_df[self.match_results_df["event"] == event]

            # A structure to hold this event's results (one row per team)
            event_points_list = []

            # We'll process each match, awarding points to home and away
            for _, row in ev_matches.iterrows():
                home_team = row["home"]
                away_team = row["away"]
                home_score = row["home_score"]
                away_score = row["away_score"]

                # ---------------------
                # HOME TEAM
                # ---------------------
                # Base (win/draw/loss) points
                if home_score > away_score:
                    win_points = 6
                    draw_points = 0
                elif home_score == away_score:
                    win_points = 0
                    draw_points = 3
                else:
                    win_points = 0
                    draw_points = 0

                # Goals, clean sheet
                goal_points = home_score
                cs_points = 2 if away_score == 0 else 0

                # Table bonus
                table_bonus = 0
                if home_team in team_pos_dict and away_team in team_pos_dict:
                    home_pos = team_pos_dict[home_team]
                    away_pos = team_pos_dict[away_team]
                    # If the home team is facing a club "at least five places higher"
                    # i.e. away_pos < home_pos by >= 5
                    # (lower number = higher place, e.g. pos=1 means top)
                    # Actually, if the away_pos is 1 and home_pos is 6 => difference = 5
                    # => table_bonus triggered
                    if (home_pos - away_pos) >= 5:
                        # If it's a home team "upset" or draw
                        if win_points == 6:
                            table_bonus = 10  # total 16
                        elif draw_points == 3:
                            table_bonus = 5  # total 8

                derived_points = (
                    win_points + draw_points + goal_points + cs_points + table_bonus
                )

                event_points_list.append(
                    {
                        "event": event,
                        "team": home_team,
                        "total_points": derived_points,
                        "total_win_points": win_points,
                        "total_draw_points": draw_points,
                        "total_goal_points": goal_points,
                        "total_cs_points": cs_points,
                        "total_table_bonus": table_bonus,
                    }
                )

                # ---------------------
                # AWAY TEAM
                # ---------------------
                if away_score > home_score:
                    win_points = 6
                    draw_points = 0
                elif away_score == home_score:
                    win_points = 0
                    draw_points = 3
                else:
                    win_points = 0
                    draw_points = 0

                goal_points = away_score
                cs_points = 2 if home_score == 0 else 0

                table_bonus = 0
                if away_team in team_pos_dict and home_team in team_pos_dict:
                    away_pos = team_pos_dict[away_team]
                    home_pos = team_pos_dict[home_team]
                    # If the away team is facing a club at least 5 places higher
                    # => (away_pos - home_pos) >= 5
                    if (away_pos - home_pos) >= 5:
                        if win_points == 6:
                            table_bonus = 10
                        elif draw_points == 3:
                            table_bonus = 5

                derived_points = (
                    win_points + draw_points + goal_points + cs_points + table_bonus
                )

                event_points_list.append(
                    {
                        "event": event,
                        "team": away_team,
                        "total_points": derived_points,
                        "total_win_points": win_points,
                        "total_draw_points": draw_points,
                        "total_goal_points": goal_points,
                        "total_cs_points": cs_points,
                        "total_table_bonus": table_bonus,
                    }
                )

            # -------------------------------------------------------
            # 3) Convert this event's data into a DataFrame and store
            # -------------------------------------------------------
            event_points_df = pd.DataFrame(event_points_list)

            # If a team had multiple matches in the same event, you might want
            # to group by team and sum. But in standard FPL logic, there's usually
            # only one match per team per gameweek. We'll assume so. If not:
            # event_points_df = event_points_df.groupby("team", as_index=False).sum(numeric_only=True)
            # event_points_df["event"] = event

            all_events_amp.append(event_points_df)

        # Finally, we concatenate the results of all events
        self.assistant_manager_points_df = pd.concat(all_events_amp, ignore_index=True)

        # (Optional) return the DataFrame
        return self.assistant_manager_points_df

    def process_league(self):
        """
        High-level entry point:
          - fetch fixtures
          - calculate league table
          - print or save the final data
        """
        self.fetch_fixtures()  # ensure we have data
        league_df = self.calculate_league_table()
        assistant_manager_df = self.calculate_assistant_manager_points()

        # (Optional) Save final league table to CSV
        out_file = os.path.join(self.data_dir, "final_league_table.csv")
        league_df.to_csv(out_file, index=False)

        # (Optional) Save assistant manager points to CSV
        out_file = os.path.join(self.data_dir, "assistant_manager_points.csv")
        assistant_manager_df.to_csv(out_file, index=False)

        print("\n===== Final League Table =====")
        print(league_df.tail(20))  # show last 20 rows just for display


def main():
    # Initialize calculator
    calculator = PremierLeaguePointsCalculator()

    # 1) Fetch fixtures & build the league table
    calculator.process_league()


if __name__ == "__main__":
    main()
