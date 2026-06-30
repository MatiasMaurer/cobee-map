import streamlit as st
import plotly.express as px
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_geolocation import streamlit_geolocation

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
st.set_page_config(page_title="Cobee Map", layout="wide", initial_sidebar_state="expanded")

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
        background-color: #111111 !important;
        border-right: 1px solid #1f1f1f !important;
        min-width: 200px !important;
        max-width: 200px !important;
        transform: none !important;
        visibility: visible !important;
        margin-left: 0px !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    [data-testid="stSidebar"] * { color: #ffffff; }
    [data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0px !important;
        transform: none !important;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #888888 !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }

    /* Main content */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 1rem !important;
    }

    /* Tabs */
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

    /* Buttons (main content only, not sidebar) */
    .main .stFormSubmitButton button, .main .stButton button {
        background-color: #7c3aed !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: background 0.2s !important;
    }
    .main .stFormSubmitButton button:hover, .main .stButton button:hover {
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

    /* Mobile nav bar */
    #mobile-nav {
        display: none;
    }

    /* Mobile overrides */
    @media (max-width: 480px) {
        [data-testid="stSidebar"] {
            display: none !important;
            margin-left: -200px !important;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        .block-container {
            padding-bottom: 90px !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        #mobile-nav {
            display: flex !important;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 99999;
            background-color: #111111;
            border-top: 1px solid #2a2a2a;
            justify-content: space-around;
            align-items: center;
            padding: 8px 0 24px 0;
            height: 65px;
        }
        #mobile-nav a {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 3px;
            text-decoration: none;
            color: #888888;
            font-size: 0.65rem;
            font-weight: 500;
            flex: 1;
        }
        #mobile-nav a.active {
            color: #7c3aed;
        }
        #mobile-nav a span.nav-icon {
            font-size: 1.3rem;
        }
    /* Force columns to stay side by side on mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
    }
    [data-testid="column"]:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }
    [data-testid="column"]:not(:first-child) {
        flex: 0 0 auto !important;
        width: 38px !important;
    }
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
if "page" not in st.session_state:
    st.session_state.page = "Form"

params = st.query_params
if "page" in params:
    st.session_state.page = params["page"]

page = st.session_state.page

# Desktop sidebar
with st.sidebar:
    with st.sidebar:
        st.markdown("<div style='height:1px'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='color:#7c3aed; margin-bottom: 0.2rem; font-size: 2rem;'>Cobee</h1>",
                    unsafe_allow_html=True)
    st.markdown("<p style='color:#7c3aed; font-size:0.8rem; margin-bottom: 1.5rem;'>Establishment map</p>",
                unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Form", key="sb_form", use_container_width=True):
        st.session_state.page = "Form"
        st.query_params["page"] = "Form"
        st.rerun()
    if st.button("List", key="sb_list", use_container_width=True):
        st.session_state.page = "List"
        st.query_params["page"] = "List"
        st.rerun()
    if st.button("Map", key="sb_map", use_container_width=True):
        st.session_state.page = "Map"
        st.query_params["page"] = "Map"
        st.rerun()

# Mobile bottom nav
st.markdown(f"""
<div id="mobile-nav">
    <a href="?page=Form" class="{'active' if page == 'Form' else ''}">
        <span class="nav-icon">Form</span>
    </a>
    <a href="?page=List" class="{'active' if page == 'List' else ''}">
        <span class="nav-icon">List</span>
    </a>
    <a href="?page=Map" class="{'active' if page == 'Map' else ''}">
        <span class="nav-icon">Map</span>
    </a>
</div>
""", unsafe_allow_html=True)

# ---------- FORM PAGE ----------
if st.session_state.page == "Form":
    st.subheader("Establishments")
    form_tab1, form_tab2 = st.tabs(["Add establishment", "Report establishment"])

    with form_tab1:
        st.markdown(" ")

        # Geolocation outside form so it can render properly
        st.markdown("**Location**")
        use_current = st.checkbox("Use my current location")
        geo_lat = None
        geo_lon = None
        if use_current:
            location = streamlit_geolocation()
            if location and location.get("latitude") is not None:
                geo_lat = location["latitude"]
                geo_lon = location["longitude"]
                st.success(f"Current location detected: {geo_lat:.6f}, {geo_lon:.6f}")
            else:
                st.warning("Could not get location. Please enter coordinates manually below.")

        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                Name = st.text_input("Establishment name")
                Street = st.text_input("Street")
                Location = st.text_input("Region")
            with col2:
                Type = st.selectbox("Type", TYPES)
                Number = st.number_input("Number", min_value=0, step=1)
                if geo_lat is not None:
                    axisX = st.number_input("Latitude", format="%.8f", value=float(geo_lat))
                    axisY = st.number_input("Longitude", format="%.8f", value=float(geo_lon))
                else:
                    axisX = st.number_input("Latitude", format="%.8f")
                    axisY = st.number_input("Longitude", format="%.8f")
            submitted = st.form_submit_button("Add establishment", use_container_width=True)

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
                    "status": "confirmed",
                    "reports": 0,
                    "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M")
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
            names = [f"{e['Name']} — {e['Street']} {e['Number']}, {e['Location']}" for e in confirmed]
            selected = st.selectbox("Select establishment to report", names)
            reason = st.text_area("Reason (optional)")
            if st.button("Report establishment", use_container_width=True):
                for e in data:
                    full_name = f"{e['Name']} — {e['Street']} {e['Number']}, {e['Location']}"
                    if full_name == selected:
                        e["status"] = "disputed"
                        e["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(data)
                st.warning(f"⚠️ {selected} has been reported and marked as disputed.")
        else:
            st.info("No confirmed establishments to report yet.")

# ---------- LIST PAGE ----------
elif st.session_state.page == "List":
    st.subheader("All establishments")
    data = load_data()

    search = st.text_input("🔍 Search", placeholder="Search by name, street or region...")
    if search:
        data = [e for e in data if
                search.lower() in e["Name"].lower() or
                search.lower() in e["Street"].lower() or
                search.lower() in e["Location"].lower()]

    if data:
        for i, e in enumerate(data):
            if e["status"] == "confirmed":
                icon = "✅"
            elif e["status"] == "disputed":
                icon = "⚠️"
            else:
                icon = "❌"

            badge_class = BADGE_CLASS.get(e["Type"], "badge-other")

            col1, col2, col3, col4 = st.columns([7, 1, 1, 1])
            with col1:
                st.markdown(f"""
                <div class="establishment-card">
                    <span style="font-size:1.2rem">{icon}</span>
                    <div style="flex:1">
                        <div class="establishment-name">{e['Name']}</div>
                        <div class="establishment-meta">{e['Street']} · {e['Location']}<br>Last updated: {e.get("last_updated", "Never")}</div>
                    </div>
                    <span class="badge {badge_class}">{e['Type']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key=f"Edit_{i}", help="Edit"):
                    st.session_state["Editing"] = i
            with col3:
                if e["status"] in ["rejected", "disputed"]:
                    if st.button("✅", key=f"Resolve_yes_{i}", help="Restore — card works here"):
                        data[i]["status"] = "confirmed"
                        data[i]["reports"] = 0
                        data[i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        save_data(data)
                        st.rerun()
                if e["status"] in ["confirmed", "disputed"]:
                    if st.button("⚠️", key=f"Resolve_no_{i}", help="Report — card doesn't work here"):
                        reports = e.get("reports", 0) + 1
                        data[i]["reports"] = reports
                        if reports >= 2:
                            data[i]["status"] = "rejected"
                        else:
                            data[i]["status"] = "disputed"
                        data[i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        save_data(data)
                        st.rerun()
            with col4:
                if st.button("🗑️", key=f"Delete_{i}", help="Delete establishment"):
                    data.pop(i)
                    save_data(data)
                    st.rerun()

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
                    save_edit = st.form_submit_button("Save changes", use_container_width=True)

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
                    data[i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    save_data(data)
                    st.session_state["Editing"] = None
                    st.success("✅ Changes saved!")
                    st.rerun()
    else:
        st.info("No establishments added yet.")

# ---------- MAP PAGE ----------
elif st.session_state.page == "Map":
    data = load_data()
    if data:
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.multiselect("Filter by type", TYPES, default=TYPES)
        with col2:
            status_filter = st.multiselect("Filter by status", ["confirmed", "disputed", "rejected"],
                                           default=["confirmed", "disputed", "rejected"])

        filtered_data = [e for e in data if e["Type"] in type_filter and e["status"] in status_filter]
        df = pd.DataFrame(filtered_data) if filtered_data else None

        # Geolocation for map
        st.markdown("**Show my location on the map**")
        map_location = streamlit_geolocation()
        if map_location and map_location.get("latitude") is not None:
            user_lat = map_location["latitude"]
            user_lon = map_location["longitude"]
        else:
            user_lat = None
            user_lon = None

        if df is not None:
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
                hover_data={"Type": True, "Street": True, "Location": True, "axisX": False, "axisY": False,
                            "status": False},
                color="Type",
                color_discrete_map=color_map,
                zoom=12,
                height=780,
            )

            if user_lat and user_lon:
                fig.add_scattermap(
                    lat=[user_lat],
                    lon=[user_lon],
                    mode="markers",
                    marker=dict(size=18, color="#ffffff"),
                    name="You are here",
                    hovertemplate="<b>You are here</b><extra></extra>"
                )
                fig.update_layout(map=dict(
                    center=dict(lat=user_lat, lon=user_lon),
                    zoom=14
                ))

            fig.update_traces(marker=dict(size=12, opacity=1), selector=dict(type="scattermap"))
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
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No establishments match your filters.")
    else:
        st.info("No establishments to show on the map yet.")
