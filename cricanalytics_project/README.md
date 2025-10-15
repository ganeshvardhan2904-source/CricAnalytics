# CricAnalytics – Cricket Player Performance Dashboard

**Author:** Ganesh Vardhan D  
**Tech Stack:** Python, Streamlit, Pandas, Plotly, PyYAML, NumPy  

##  Overview
CricAnalytics is a cricket data analytics web app that processes YAML-formatted match files and visualizes player performance metrics such as strike rate, batting average, and consistency index.

The dashboard also provides **player-to-player comparisons** and **impact analysis** using match contribution percentages.

## ⚙️ Features
- Load multiple YAML cricket match files
- Compute key batting metrics (Runs, Strike Rate, Average)
- Player comparison charts (bar visualization)
- Impact and Consistency Map (% contribution)
- Interactive, responsive Streamlit dashboard

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/CricAnalytics.git
   cd CricAnalytics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

4. Open the browser at the link shown in the terminal.

## Example Output
| Metric | Player A | Player B |
|---------|-----------|----------|
| Runs | 45 | 38 |
| Strike Rate | 130.2 | 121.4 |

## Future Work
- Add bowler analytics and economy rates  
- Integrate AI-based performance prediction  
- Include team-level summary dashboard

---

**💡 Built by a cricket enthusiast and aspiring AIML engineer – bridging sports and data analytics.**
