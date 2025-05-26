import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import json
import os
import io

def local_css(dark_mode):
    # Base CSS, uses CSS variables for colors and styles
    css = f"""
    <style>
        :root {{
            --primary-color: {'#5AA9E6' if dark_mode else '#4A90E2'};
            --primary-color-hover: {'#3B7DD8' if dark_mode else '#357ABD'};
            --secondary-color: {'#718096' if dark_mode else '#A0AEC0'};
            --background-color: {'#1E293B' if dark_mode else '#FFFFFF'};
            --text-color: {'#F8FAFC' if dark_mode else '#222222'};
        }}

        .main .block-container {{
            max-width: 900px;
            padding: 2rem 3rem;
            background: var(--background-color);
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            color: var(--text-color);
        }}

        .stTextInput>div>div>input, .stNumberInput>div>div>input {{
            border-radius: 10px !important;
            padding: 0.6rem 1rem;
            font-size: 1rem;
            border: 1.5px solid var(--secondary-color);
            background-color: var(--background-color);
            color: var(--text-color);
            transition: border-color 0.3s, background-color 0.3s, color 0.3s;
        }}

        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {{
            border-color: var(--primary-color);
            outline: none;
            background-color: var(--background-color);
            color: var(--text-color);
        }}

        div.stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border-radius: 15px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: background-color 0.3s;
            border: none;
            cursor: pointer;
        }}

        div.stButton > button:hover {{
            background-color: var(--primary-color-hover);
        }}

        h1, h2, h3 {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 700;
            color: var(--text-color);
        }}

        textarea {{
            border-radius: 10px !important;
            padding: 0.8rem !important;
            border: 1.5px solid var(--secondary-color) !important;
            font-size: 1rem !important;
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
            transition: background-color 0.3s, color 0.3s;
        }}

        .stDataFrame > div {{
            border-radius: 15px;
            overflow-x: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            background-color: var(--background-color);
            color: var(--text-color);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Function to save project data to JSON
def save_project_to_json(filename, project_name, start_date, phases, notes):
    data = {
        "project_name": project_name,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "phases": phases,
        "notes": notes
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Function to load project data from JSON
def load_project_from_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
    data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d")
    return data

# Function to list local project files
def list_local_projects():
    return [f for f in os.listdir() if f.endswith(".json") and f.startswith("project_")]

# Function to export to Excel bytes
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Timeline')
    processed_data = output.getvalue()
    return processed_data


# Add theme toggle in sidebar
theme_choice = st.sidebar.selectbox("Choose Theme", options=["Light Mode", "Dark Mode"])
dark_mode = theme_choice == "Dark Mode"
local_css(dark_mode)

st.title("📊 Custom Project Timeline Generator (Offline Edition)")

st.sidebar.header("🛠️ Project Configuration")

# Load existing project
project_files = list_local_projects()
selected_project = st.sidebar.selectbox("📂 Load Existing Project", [""] + project_files)

if selected_project and st.sidebar.button("📥 Load Project"):
    loaded_data = load_project_from_json(selected_project)
    st.session_state.project_name = loaded_data["project_name"]
    st.session_state.start_date = loaded_data["start_date"]
    st.session_state.phases = loaded_data["phases"]
    st.session_state.notes = loaded_data.get("notes", "")
    st.experimental_rerun()

# New project button
if st.sidebar.button("🆕 Start New Project"):
    st.session_state.project_name = ""
    st.session_state.start_date = datetime.today()
    st.session_state.phases = []
    st.session_state.notes = ""
    st.experimental_rerun()

# Default session values
if "project_name" not in st.session_state:
    st.session_state.project_name = "Demo Project"
if "start_date" not in st.session_state:
    st.session_state.start_date = datetime.today()
if "phases" not in st.session_state or not st.session_state.phases:
    st.session_state.phases = [
        {"Phase": "Requirements & Planning", "Duration (weeks)": 2},
        {"Phase": "Design", "Duration (weeks)": 3},
        {"Phase": "Development Sprint 1", "Duration (weeks)": 2},
        {"Phase": "Testing & QA", "Duration (weeks)": 3},
        {"Phase": "Deployment & Launch", "Duration (weeks)": 1}
    ]
if "notes" not in st.session_state:
    st.session_state.notes = ""

# Project details inputs
with st.sidebar.expander("Project Details", expanded=True):
    st.session_state.project_name = st.text_input("Project Name", st.session_state.project_name)
    st.session_state.start_date = st.date_input("Project Start Date", st.session_state.start_date)

# Add new phase section
with st.sidebar.expander("Add New Phase", expanded=True):
    new_phase_name = st.text_input("Phase Name", key="new_phase_name")
    new_phase_duration = st.number_input("Duration (weeks)", min_value=1, max_value=52, value=2, key="new_phase_duration")

    if st.button("➕ Add Phase"):
        if new_phase_name.strip():
            st.session_state.phases.append({
                "Phase": new_phase_name.strip(),
                "Duration (weeks)": new_phase_duration
            })
            st.sidebar.success(f"Added '{new_phase_name.strip()}'")
            st.experimental_rerun()
        else:
            st.sidebar.error("Phase name cannot be empty.")

# Notes Section (wider and styled)
st.subheader("📝 Project Notes")
st.session_state.notes = st.text_area("Notes (optional)", st.session_state.notes, height=150)

# Phases list with edit & remove buttons
if st.session_state.phases:
    st.subheader("📌 Project Phases")
    for idx, phase in enumerate(st.session_state.phases):
        cols = st.columns([4, 2, 1])
        new_name = cols[0].text_input(f"Phase {idx+1} Name", phase["Phase"], key=f"name_{idx}")
        new_duration = cols[1].number_input("Weeks", min_value=1, max_value=52, value=phase["Duration (weeks)"], key=f"duration_{idx}")
        if cols[2].button("❌", key=f"remove_{idx}"):
            st.session_state.phases.pop(idx)
            st.experimental_rerun()
        if new_name != phase["Phase"] or new_duration != phase["Duration (weeks)"]:
            st.session_state.phases[idx] = {"Phase": new_name, "Duration (weeks)": new_duration}

# Save project button
if st.button("💾 Save Project"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"project_{timestamp}.json"
    save_project_to_json(filename, st.session_state.project_name, st.session_state.start_date, st.session_state.phases, st.session_state.notes)
    st.success(f"Project saved as {filename}")

# Generate timeline and plot
if st.button("📅 Generate Timeline"):
    if not st.session_state.phases:
        st.warning("Please add at least one phase to generate the timeline.")
    else:
        current_start = datetime.combine(st.session_state.start_date, datetime.min.time())
        timeline = []

        for phase in st.session_state.phases:
            phase_start = current_start
            phase_end = phase_start + timedelta(weeks=phase["Duration (weeks)"])
            timeline.append({
                "Phase": phase["Phase"],
                "Start Date": phase_start,
                "End Date": phase_end,
                "Duration (weeks)": phase["Duration (weeks)"]
            })
            current_start = phase_end

        timeline_df = pd.DataFrame(timeline)

        st.subheader(f"📑 {st.session_state.project_name} Timeline")
        st.dataframe(timeline_df.style.set_properties(**{'background-color': '#f0f0f0', 'color': '#222'}))

        # Progress bar with % label
        total_weeks = sum(p["Duration (weeks)"] for p in st.session_state.phases)
        completed_weeks = 0  # You can customize this with actual progress input
        progress = (completed_weeks / total_weeks) if total_weeks else 0
        st.progress(progress)
        st.caption(f"Progress: {progress*100:.1f}% (Customizable in future)")

        # Plot Gantt chart
        fig = px.timeline(
            timeline_df,
            x_start="Start Date",
            x_end="End Date",
            y="Phase",
            color="Phase",
            title=f"{st.session_state.project_name} Timeline Gantt Chart",
            hover_data=["Duration (weeks)"]
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(showlegend=False, template="plotly_white")

        st.plotly_chart(fig, use_container_width=True)

        # Download CSV and Excel
        csv = timeline_df.to_csv(index=False).encode('utf-8')
        excel_data = to_excel(timeline_df)

        col1, col2 = st.columns(2)
        col1.download_button("📥 Download CSV", data=csv, file_name=f"{st.session_state.project_name}_timeline.csv", mime="text/csv")
        col2.download_button("📥 Download Excel", data=excel_data, file_name=f"{st.session_state.project_name}_timeline.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Save timeline to JSON option
        json_str = timeline_df.to_json(date_format="iso", orient="records")
        st.download_button("📥 Download Timeline JSON", json_str, file_name=f"{st.session_state.project_name}_timeline.json", mime="application/json")
