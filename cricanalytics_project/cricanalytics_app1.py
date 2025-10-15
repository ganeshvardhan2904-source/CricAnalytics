import streamlit as st
import pandas as pd
import yaml
import os
import plotly.express as px
import numpy as np

# ----------------------------------
# Load and parse YAML match data
# ----------------------------------
def load_match_data(folder_path):
    all_data = []
    for file in os.listdir(folder_path):
        if file.endswith((".yaml", ".yml")):
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f)
                if not data or "innings" not in data:
                    continue

                for inning in data["innings"]:
                    for team, details in inning.items():
                        deliveries = details.get("deliveries", [])
                        for d in deliveries:
                            for ball, info in d.items():
                                all_data.append({
                                    "match": file,
                                    "inning": team,
                                    "ball": ball,
                                    "batsman": str(info.get("batsman", "")),
                                    "bowler": str(info.get("bowler", "")),
                                    "runs": info.get("runs", {}).get("batsman", 0),
                                    "extras": info.get("runs", {}).get("extras", 0),
                                    "total": info.get("runs", {}).get("total", 0),
                                    "wicket": 1 if "wicket" in info else 0,
                                })
            except Exception as e:
                st.warning(f"Could not load {file}: {e}")
    return pd.DataFrame(all_data)


# ----------------------------------
# Compute basic batting statistics
# ----------------------------------
def compute_batting_stats(df):
    if df.empty:
        return pd.DataFrame()

    stats = df.groupby("batsman", dropna=True).agg(
        Runs=("runs", "sum"),
        Balls=("ball", "count"),
        Outs=("wicket", "sum")
    ).reset_index()

    stats["Strike Rate"] = (stats["Runs"] / stats["Balls"] * 100).round(2)
    stats["Average"] = (stats["Runs"] / stats["Outs"].replace(0, np.nan)).round(2)
    return stats


# ----------------------------------
# Compute impact and consistency metrics
# ----------------------------------
def compute_impact_analysis(df):
    if df.empty:
        return pd.DataFrame()

    match_totals = df.groupby("match")["total"].sum().reset_index(name="Match Total")
    player_runs = df.groupby(["match", "batsman"])["runs"].sum().reset_index()

    merged = pd.merge(player_runs, match_totals, on="match")
    merged["Run Contribution %"] = (merged["runs"] / merged["Match Total"] * 100).round(2)

    impact = merged.groupby("batsman").agg(
        Avg_Contribution_Percentage=("Run Contribution %", "mean"),
        Max_Contribution_Percentage=("Run Contribution %", "max"),
        Matches=("match", "nunique")
    ).reset_index()

    impact["Consistency Index"] = (
        impact["Avg_Contribution_Percentage"] / impact["Max_Contribution_Percentage"]
    ).round(2)

    return impact.sort_values(by="Avg_Contribution_Percentage", ascending=False)


# ----------------------------------
# Streamlit App
# ----------------------------------
st.set_page_config(page_title="CricAnalytics", layout="wide")
st.title("CricAnalytics: Player Performance Dashboard")

folder = st.text_input("Enter the folder path with YAML match files:", "./data")

if folder and os.path.isdir(folder):
    df = load_match_data(folder)

    if df.empty:
        st.error("No valid match data found in the folder.")
    else:
        st.success(f"Loaded {len(df)} deliveries from {df['match'].nunique()} matches.")

        # --- Batting statistics ---
        st.header("Batting Statistics")
        stats = compute_batting_stats(df)
        st.dataframe(stats, use_container_width=True)

        # --- Player comparison ---
        st.subheader("Player Comparison")
        players = stats["batsman"].astype(str).unique().tolist()

        if len(players) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                p1 = st.selectbox("Select Player 1", players, index=0)
            with col2:
                p2 = st.selectbox("Select Player 2", players, index=1)

            if p1 != p2:
                s1 = stats[stats["batsman"] == p1].iloc[0]
                s2 = stats[stats["batsman"] == p2].iloc[0]

                comp = pd.DataFrame({
                    "Metric": ["Runs", "Balls", "Strike Rate", "Average"],
                    p1: [s1["Runs"], s1["Balls"], s1["Strike Rate"], s1["Average"]],
                    p2: [s2["Runs"], s2["Balls"], s2["Strike Rate"], s2["Average"]],
                })

                st.dataframe(comp, use_container_width=True)
                fig = px.bar(
                    comp,
                    x="Metric",
                    y=[p1, p2],
                    barmode="group",
                    title=f"{p1} vs {p2} Performance Comparison",
                    text_auto=True
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- Filtered Impact Analysis for selected players ---
                st.header("Impact and Consistency Map (Selected Players Only)")
                impact_df = compute_impact_analysis(df)
                filtered_impact = impact_df[impact_df["batsman"].isin([p1, p2])]

                if not filtered_impact.empty:
                    st.dataframe(filtered_impact, use_container_width=True)
                    fig2 = px.scatter(
                        filtered_impact,
                        x="Avg_Contribution_Percentage",
                        y="Consistency Index",
                        size="Matches",
                        color="batsman",
                        hover_name="batsman",
                        title="Player Impact and Consistency Map (Average Contribution %)",
                        labels={
                            "Avg_Contribution_Percentage": "Average Contribution (%)",
                            "Consistency Index": "Consistency Index",
                            "Matches": "Matches Played",
                            "batsman": "Player"
                        }
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No impact data available for the selected players.")
            else:
                st.info("Please select two different players to compare.")
        else:
            st.info("At least two players are required for comparison.")
else:
    st.info("Enter a valid folder path containing YAML match files.")
