import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os

# ---------- DATA ----------
DATA_FILE = "establishments.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- CONFIG ----------
st.set_page_config(page_title="Cobee Map", layout="wide")

TYPES = ["Supermarket", "Restaurant", "Transit", "Coffee Shop", "Tabacs", "Other"]

BADGE_CLASS = {
    "Supermarket": "badge-supermarket",
    "Restaurant": "badge-restaurant",
    "Transit": "badge-transit",
    "Coffee Shop": "badge-coffee",
    "Tabacs": "badge-tabacs",
    "Other": "badge-other",
}

# ---------- STYLING ----------
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0f0f0f; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #1f1f1f;
    }
    [data-testid="stSidebar"] * { color: #ffffff; }

    /* Sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio label {
        display: flex;
        align-items: center;
        padding: 14px 16px !important;
        border-radius: 8px;
        cursor: pointer;
        font-size: 3rem !important;
        line-height: 4 !important;
        font-weight: 500 !important;
        color: #888888 !important;
        transition: all 0.15s;
        margin-bottom: 8px;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #1a1a1a;
        color: #ffffff !important;
    
    }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background-color: #7c3aed;
        color: #ffffff !important;
    }

    /* Hide radio dots */
    [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
        display: none;
    }

    /* Main content */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 1rem !important;
    }

    /* Tabs (for sub-tabs in form) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #888888;
        font-weight: 500;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #7c3aed !important;
        color: #ffffff !important;
        border-bottom: 2px solid #7c3aed !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #7c3aed !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
    }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }

    /* Labels */
    label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #aaaaaa !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
    }

    /* Headings */
    h1, h2, h3 { color: #ffffff !important; }

    /* Buttons */
    .stFormSubmitButton button, .stButton button {
        background-color: #7c3aed !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: background 0.2s !important;
    }
    .stFormSubmitButton button:hover, .stButton button:hover {
        background-color: #6d28d9 !important;
    }

    /* List cards */
    .establishment-card {
        background-color: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .establishment-name {
        color: #ffffff;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .establishment-meta {
        color: #666666;
        font-size: 0.8rem;
        margin-top: 2px;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .badge-supermarket { background: rgba(16,185,129,0.15); color: #10b981; }
    .badge-restaurant  { background: rgba(245,158,11,0.15);  color: #f59e0b; }
    .badge-transit     { background: rgba(239,68,68,0.15);   color: #ef4444; }
    .badge-coffee      { background: rgba(59,130,246,0.15);  color: #3b82f6; }
    .badge-tabacs      { background: rgba(168,85,247,0.15);  color: #a855f7; }
    .badge-other       { background: rgba(107,114,128,0.15); color: #6b7280; }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
# ---------- NAVIGATION ----------
if "page" not in st.session_state:
    st.session_state.page = "📋  Form"

# Desktop sidebar
with st.sidebar:
    st.markdown("<h1 style='color:#7c3aed; margin-bottom: 0.2rem; font-size: 2rem;'>📍 Cobee</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#7c3aed; font-size:0.8rem; margin-bottom: 1.5rem;'>Establishment map</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("📋  Form", use_container_width=True, key="sb_form"):
        st.session_state.page = "📋  Form"
    if st.button("📄  List", use_container_width=True, key="sb_list"):
        st.session_state.page = "📄  List"
    if st.button("🗺️  Map", use_container_width=True, key="sb_map"):
        st.session_state.page = "🗺️  Map"

# Mobile bottom nav
st.markdown("""
<style>
    .mobile-nav {
        display: none;
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { display: none !important; }
        .block-container { padding-bottom: 100px !important; }
        .mobile-nav {
            display: flex;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background-color: #111111;
            border-top: 1px solid #2a2a2a;
            justify-content: space-around;
            padding: 8px 0 24px 0;
        }
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📋\nForm", key="mob_form", use_container_width=True):
        st.session_state.page = "📋  Form"
with col2:
    if st.button("📄\nList", key="mob_list", use_container_width=True):
        st.session_state.page = "📄  List"
with col3:
    if st.button("🗺️\nMap", key="mob_map", use_container_width=True):
        st.session_state.page = "🗺️  Map"

page = st.session_state.page

# ---------- FORM PAGE ----------
if st.session_state.page == "📋  Form":
    st.subheader("Establishments")
    form_tab1, form_tab2 = st.tabs(["Add establishment", "Report establishment"])

    with form_tab1:
        st.markdown(" ")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                Name = st.text_input("Establishment name")
                Street = st.text_input("Street")
                Location = st.text_input("Region")
            with col2:
                Type = st.selectbox("Type", TYPES)
                Number = st.number_input("Number", min_value=0, step=1)
                axisX = st.number_input("Latitude", format="%.8f")
                axisY = st.number_input("Longitude", format="%.8f")
            submitted = st.form_submit_button("Add establishment", width='stretch')

        if submitted:
            if Name and Street and Location:
                data = load_data()
                data.append({
                    "Name": Name,
                    "Type": Type,
                    "Street": Street,
                    "Number": int(Number),
                    "Location": Location,
                    "axisX": axisX,
                    "axisY": axisY,
                    "status": "confirmed"
                })
                save_data(data)
                st.success(f"✅ {Name} added successfully!")
            else:
                st.error("Please fill in name, street and city.")

    with form_tab2:
        st.markdown(" ")
        data = load_data()
        confirmed = [e for e in data if e["status"] == "confirmed"]
        if confirmed:
            names = [e["Name"] for e in confirmed]
            selected = st.selectbox("Select establishment to report", names)
            reason = st.text_area("Reason (optional)")
            if st.button("Report establishment", width='stretch'):
                for e in data:
                    if e["Name"] == selected:
                        e["status"] = "disputed"
                save_data(data)
                st.warning(f"⚠️ {selected} has been reported and marked as disputed.")
        else:
            st.info("No confirmed establishments to report yet.")

# ---------- LIST PAGE ----------
elif st.session_state.page == "📄  List":
    st.subheader("All establishments")
    data = load_data()

    if data:
        for i, e in enumerate(data):
            if e["status"] == "confirmed":
                icon = "✅"
            elif e["status"] == "disputed":
                icon = "⚠️"
            else:
                icon = "❌"

            badge_class = BADGE_CLASS.get(e["Type"], "badge-other")

            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"""
                <div class="establishment-card">
                    <span style="font-size:1.2rem">{icon}</span>
                    <div style="flex:1">
                        <div class="establishment-name">{e['Name']}</div>
                        <div class="establishment-meta">{e['Street']} · {e['Location']}</div>
                    </div>
                    <span class="badge {badge_class}">{e['Type']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key=f"Edit_{i}", help="Edit"):
                    st.session_state["Editing"] = i

            if st.session_state.get("Editing") == i:
                with st.form(f"Edit_form_{i}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        new_nombre = st.text_input("Name", value=e["Name"])
                        new_calle = st.text_input("Street", value=e["Street"])
                        new_localidad = st.text_input("Region", value=e["Location"])
                    with ec2:
                        new_tipo = st.selectbox("Type", TYPES, index=TYPES.index(e["Type"]))
                        new_numero = st.number_input("Number", min_value=0, step=1, value=e["Number"])
                        new_ejeX = st.number_input("Latitude", format="%.8f", value=e["axisX"])
                        new_ejeY = st.number_input("Longitude", format="%.8f", value=e["axisY"])
                    save_edit = st.form_submit_button("Save changes", width='stretch')

                if save_edit:
                    data[i].update({
                        "Name": new_nombre,
                        "Type": new_tipo,
                        "Street": new_calle,
                        "Number": int(new_numero),
                        "Location": new_localidad,
                        "axisX": new_ejeX,
                        "axisY": new_ejeY,
                    })
                    save_data(data)
                    st.session_state["Editing"] = None
                    st.success("✅ Changes saved!")
                    st.rerun()
    else:
        st.info("No establishments added yet.")

# ---------- MAP PAGE ----------
elif st.session_state.page == "🗺️  Map":
    data = load_data()
    if data:
        df = pd.DataFrame(data)

        color_map = {
            "Supermarket": "#10b981",
            "Restaurant": "#f59e0b",
            "Transit": "#ef4444",
            "Coffee Shop": "#3b82f6",
            "Tabacs": "#a855f7",
            "Other": "#6b7280"
        }

        fig = px.scatter_map(
            df,
            lat="axisX",
            lon="axisY",
            hover_name="Name",
            hover_data={"Type": True, "Street": True, "Location": True, "axisX": False, "axisY": False, "status": False},
            color="Type",
            color_discrete_map=color_map,
            zoom=12,
            height=850,
        )
        fig.update_traces(marker=dict(size=12, opacity=1))
        fig.update_layout(
            map_style="carto-darkmatter",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            legend=dict(
                bgcolor="rgba(20,20,20,0.85)",
                bordercolor="#2a2a2a",
                borderwidth=1,
                font=dict(color="#ffffff", size=12),
            )
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No establishments to show on the map yet.")