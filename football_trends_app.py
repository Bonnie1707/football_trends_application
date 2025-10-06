# Football Trend Analyzer App (for personal use)
# Author: Boniface Rono

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import datetime as dt

# --- SETTINGS ---
API_KEY = "YOUR_API_FOOTBALL_KEY"  # get from https://dashboard.api-football.com/
LEAGUE_ID = 39  # English Premier League as example
SEASON = 2024

# --- PAGE CONFIG ---
st.set_page_config(page_title="Football Trend Analyzer", page_icon="⚽", layout="wide")
st.title("⚽ Football Team Trend & Prediction Dashboard")
st.caption("Powered by API-Football | For personal use only")

# --- FETCH DATA ---
st.sidebar.header("Settings")
team_name = st.sidebar.text_input("Enter Team Name (e.g., Arsenal)", "Arsenal")

url = f"https://v3.football.api-sports.io/teams?name={team_name}"
headers = {"x-apisports-key": API_KEY}

team_response = requests.get(url, headers=headers)
team_data = team_response.json()

if team_response.status_code != 200 or not team_data['response']:
    st.error("Team not found or API limit reached.")
else:
    team_id = team_data['response'][0]['team']['id']
    
    # Fetch last 10 matches for that team
    fixtures_url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season={SEASON}&last=10"
    fixtures = requests.get(fixtures_url, headers=headers).json()
    
    if fixtures['response']:
        matches = []
        for match in fixtures['response']:
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            home_goals = match['goals']['home']
            away_goals = match['goals']['away']
            date = match['fixture']['date'][:10]
            
            if team_name.lower() == home.lower():
                result = "Win" if home_goals > away_goals else ("Draw" if home_goals == away_goals else "Loss")
                goals_for = home_goals
                goals_against = away_goals
            else:
                result = "Win" if away_goals > home_goals else ("Draw" if home_goals == away_goals else "Loss")
                goals_for = away_goals
                goals_against = home_goals
            
            matches.append({
                "Date": date,
                "Opponent": away if team_name.lower() == home.lower() else home,
                "Goals For": goals_for,
                "Goals Against": goals_against,
                "Result": result
            })
        
        df = pd.DataFrame(matches).sort_values("Date")

        # --- STATS SUMMARY ---
        st.subheader(f"📊 Last 10 Matches for {team_name}")
        st.dataframe(df)

        win_rate = (df['Result'] == "Win").sum() / len(df) * 100
        avg_goals = df["Goals For"].mean()
        avg_conceded = df["Goals Against"].mean()
        st.metric("Win Rate", f"{win_rate:.1f}%")
        st.metric("Avg Goals Scored", f"{avg_goals:.2f}")
        st.metric("Avg Goals Conceded", f"{avg_conceded:.2f}")

        # --- CHARTS ---
        st.subheader("📈 Performance Trend (Like Forex)")
        fig = px.line(df, x="Date", y="Goals For", title=f"{team_name} Goal Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # --- SIMPLE PREDICTION ---
        st.subheader("🧠 Simple Prediction Model")
        trend_score = (win_rate * 0.6) + ((avg_goals - avg_conceded) * 10)
        if trend_score > 70:
            pred = "Strong Win Probability"
        elif trend_score > 50:
            pred = "Moderate Win Probability"
        else:
            pred = "Low Win Probability"
        st.success(f"Prediction: {pred}")
    else:
        st.warning("No recent fixtures found.")
