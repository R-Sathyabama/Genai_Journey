import streamlit as st
import pandas as pd
import os
import io
import hashlib
import shutil
from datetime import datetime, time

# --- 1. SYSTEM CONFIG & UI ---
st.set_page_config(page_title="LifeOS 2026 Pro", layout="wide", page_icon="🚀")

try:
    from streamlit_calendar import calendar 
    from streamlit_extras.metric_cards import style_metric_cards
except ImportError:
    st.error("Please run: pip install streamlit-calendar streamlit-extras")
    st.stop()

BASE_VAULT = os.path.join(os.getcwd(), "my_private_vault")
if not os.path.exists(BASE_VAULT): os.makedirs(BASE_VAULT)

# Template Setup
TEMPLATE_PATH = "template.xlsx"
if not os.path.exists(TEMPLATE_PATH):
    df_template = pd.DataFrame({
        "Time": ["08:30:00", "12:00:00", "18:00:00"], 
        "Task": ["Focus Work", "Lunch", "Review"],
        "Status": ["Pending", "In Progress", "Done"]
    })
    df_template.to_excel(TEMPLATE_PATH, index=False)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Logic Resolved: YouTube Shorts & URL Sanitizer
def get_clean_yt_url(url):
    if not url: return ""
    if "/shorts/" in url:
        url = url.replace("/shorts/", "/watch?v=")
    return url.split("&")[0] 

# --- 2. AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state.auth = False

st.sidebar.title("🔐 Secure Login")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

col_l1, col_l2 = st.sidebar.columns(2)
if col_l1.button("Login"):
    u_dir = os.path.join(BASE_VAULT, email.replace("@","_").replace(".","_"))
    if os.path.exists(os.path.join(u_dir, ".v_hash")):
        with open(os.path.join(u_dir, ".v_hash"), "r") as f:
            if f.read() == hash_password(password):
                st.session_state.auth, st.session_state.u_dir, st.session_state.email = True, u_dir, email
                st.rerun()
            else: st.sidebar.error("❌ Wrong Password")
    else: st.sidebar.error("❌ User not found.")

if col_l2.button("Sign Up"):
    u_dir = os.path.join(BASE_VAULT, email.replace("@","_").replace(".","_"))
    if not os.path.exists(u_dir):
        os.makedirs(u_dir)
        with open(os.path.join(u_dir, ".v_hash"), "w") as f: f.write(hash_password(password))
        shutil.copy(TEMPLATE_PATH, os.path.join(u_dir, "planner.xlsx"))
        st.sidebar.success("✅ Account Created! Now Login.")
    else: st.sidebar.warning("User exists.")

# --- 3. DASHBOARD ---
if st.session_state.auth:
    u_dir = st.session_state.u_dir
    menu = st.sidebar.radio("Navigation", ["📅 Activity Calendar", "📝 Smart Planner", "📺 YouTube Study", "✍️ Journal History"])

    # A. CALENDAR WITH DYNAMIC MESSAGES
    if menu == "📅 Activity Calendar":
        st.title("🗓️ Visual Activity Schedule")
        p_path = os.path.join(u_dir, "planner.xlsx")
        events = []
        if os.path.exists(p_path):
            df = pd.read_excel(p_path)
            for i, row in df.iterrows():
                status = str(row['Status'])
                color = "#ffc107" if status == "Pending" else "#17a2b8" if status == "In Progress" else "#28a745"
                events.append({"id": i, "title": f"{row['Task']}", "start": datetime.now().strftime("%Y-%m-%d"), "color": color})
        
        st.info("💡 Click a calendar event to analyze your current task state.")
        res = calendar(events=events, options={"initialView": "dayGridMonth", "selectable": True})
        
        if res.get("eventClick"):
            idx = int(res["eventClick"]["event"]["id"])
            row = df.iloc[idx]
            curr_s = row['Status']
            if curr_s == "Pending": st.warning(f"⚠️ **{row['Task']}**: You haven't started this. Modify in Smart Planner to begin!")
            elif curr_s == "In Progress": st.info(f"🔵 **{row['Task']}**: This is currently in progress. Stay focused!")
            elif curr_s == "Done": st.success(f"✅ **{row['Task']}**: Great! This task is finished.")

    # B. SMART PLANNER (UX Optimized: Single Click)
    elif menu == "📝 Smart Planner":
        st.title("📝 Smart Planner")
        p_path = os.path.join(u_dir, "planner.xlsx")
        df = pd.read_excel(p_path)
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S', errors='coerce').dt.time
        df['Time'] = df['Time'].fillna(time(0, 0))

        edited_df = st.data_editor(
            df, num_rows="dynamic", width="stretch",
            column_config={
                "Time": st.column_config.TimeColumn("Start Time", format="hh:mm a", step=60),
                "Status": st.column_config.SelectboxColumn("Status", options=["Pending", "In Progress", "Done"], required=True)
            }
        )
        if st.button("💾 Sync to Vault"):
            save_df = edited_df.copy()
            save_df['Time'] = save_df['Time'].astype(str)
            save_df.to_excel(p_path, index=False)
            st.success("✅ Synchronized!")
            st.rerun()

    # C. YOUTUBE STUDY (With Search History & Crash Fix)
    elif menu == "📺 YouTube Study":
        st.title("📺 YouTube Study Center")
        history_path = os.path.join(u_dir, "yt_history.csv")
        raw_url = st.text_input("🔗 Paste YouTube URL")
        clean_url = get_clean_yt_url(raw_url)
        
        if clean_url:
            v_col, n_col = st.columns([1.5, 1])
            with v_col: st.video(clean_url)
            with n_col:
                notes = st.text_area("Observations...", height=250)
                if st.button("💾 Save Session"):
                    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), clean_url, notes]], columns=["Date", "URL", "Note"])
                    if os.path.exists(history_path) and os.path.getsize(history_path) > 0:
                        new_data.to_csv(history_path, mode='a', header=False, index=False)
                    else:
                        new_data.to_csv(history_path, index=False)
                    st.toast("Snippet Captured!")

        st.markdown("---")
        if os.path.exists(history_path) and os.path.getsize(history_path) > 0:
            st.subheader("🔍 Search Your Video Notes")
            h_df = pd.read_csv(history_path)
            query = st.text_input("Filter notes by keyword...", placeholder="Type here...")
            
            if query:
                filtered_df = h_df[h_df['Note'].str.contains(query, case=False, na=False)]
                st.dataframe(filtered_df, width="stretch")
            else:
                st.dataframe(h_df, width="stretch")
        else:
            st.info("Start taking notes to build your history!")

    # D. JOURNAL (Date Integrity: No Future Dates)
    elif menu == "✍️ Journal History":
        st.title("✍️ Personal Journal")
        sel_date = st.date_input("Date", datetime.now().date(), max_value=datetime.now().date())
        j_path = os.path.join(u_dir, f"j_{sel_date}.txt")
        
        existing = ""
        if os.path.exists(j_path):
            with open(j_path, "r") as f: existing = f.read()
        
        entry = st.text_area(f"Thoughts for {sel_date}", value=existing, height=250)
        if st.button("📓 Save Journal"):
            with open(j_path, "w") as f: f.write(entry)
            st.success("✅ Saved.")
            st.rerun()

        st.markdown("---")
        files = sorted([f for f in os.listdir(u_dir) if f.startswith("j_")], reverse=True)
        if files:
            cols = st.columns(4) 
            for i, f_name in enumerate(files):
                with cols[i % 4]:
                    d_label = f_name.replace("j_", "").replace(".txt", "")
                    with st.expander(f"📅 {d_label}"):
                        with open(os.path.join(u_dir, f_name), "r") as f: st.write(f.read())
