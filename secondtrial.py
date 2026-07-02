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


def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000  # Earth radius in meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def format_distance(meters):
    if meters < 1000:
        return f"{int(meters)} m"
    return f"{meters / 1000:.1f} km"


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
    .card-top{
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        gap:16px;
    }
    .card-left{
        flex:1;
        min-width:0;
    }
    .card-left .establishment-name{
        margin-bottom:6px;
    }
    .card-left .establishment-meta{
        margin-top:3px;
    }
    .card-top .badge{
        white-space:nowrap;
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

    /* Nearby tab action buttons */
    .main .stButton button {
        min-height: 42px !important;
    }

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
        .establishment-card{
            margin-bottom:6px;
        }
        .card-top{
            flex-direction:column;
            gap:10px;
        }
        .card-top .badge{
            align-self:flex-start;
        }
        div[data-testid="stHorizontalBlock"]{
            gap:8px;
            margin-bottom:18px;
        }
        div[data-testid="stHorizontalBlock"] > div{
            flex:1;
        }
        html,
        body,
        .stApp{
            overflow-x:hidden;
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
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"

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
    if st.button("Home", key="sb_home", use_container_width=True):
        st.session_state.page = "Home"
        st.query_params["page"] = "Home"
        st.rerun()
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
    <a href="?page=Home" class="{'active' if page == 'Home' else ''}">
        <span class="nav-icon">Home</span>
    </a>
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

# ---------- HOME PAGE ----------
if st.session_state.page == "Home":
    data = load_data()
    confirmed_count = len([e for e in data if e["status"] == "confirmed"])
    disputed_count = len([e for e in data if e["status"] == "disputed"])

    st.markdown("""
    <div style="max-width: 600px; margin: 2rem auto 0 auto;">
        <h1 style="color:#ffffff; font-size:2.2rem; font-weight:700; margin-bottom:0.3rem;">Cobee Map</h1>
        <p style="color:#888888; font-size:1rem; margin-bottom:2rem;">
            A crowdsourced map of establishments that accept the Cobee card.
            Add places you know, report ones that no longer work, and help
            your colleagues find where to spend their Cobee balance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex; gap:12px; margin-bottom:2rem; max-width:600px; margin-left:auto; margin-right:auto;">
        <div style="flex:1; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:16px; text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#10b981;">{confirmed_count}</div>
            <div style="color:#666666; font-size:0.8rem; margin-top:4px;">Confirmed</div>
        </div>
        <div style="flex:1; background:#1a1a1a; border:1px solid #2a2a2a; border-radius:12px; padding:16px; text-align:center;">
            <div style="font-size:1.8rem; font-weight:700; color:#f59e0b;">{disputed_count}</div>
            <div style="color:#666666; font-size:0.8rem; margin-top:4px;">Disputed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="max-width:600px; margin:0 auto 1.5rem auto;">
        <p style="color:#aaaaaa; font-size:0.85rem; margin-bottom:1rem;">Where do you want to go?</p>
    </div>
    """, unsafe_allow_html=True)

    h1, h2, h3 = st.columns(3)
    with h1:
        if st.button("Add a place", key="home_form", use_container_width=True):
            st.session_state.page = "Form"
            st.query_params["page"] = "Form"
            st.rerun()
    with h2:
        if st.button("Browse the list", key="home_list", use_container_width=True):
            st.session_state.page = "List"
            st.query_params["page"] = "List"
            st.rerun()
    with h3:
        if st.button("Open the map", key="home_map", use_container_width=True):
            st.session_state.page = "Map"
            st.query_params["page"] = "Map"
            st.rerun()

# ---------- FORM PAGE ----------
elif st.session_state.page == "Form":
    st.subheader("Establishments")
    form_tab1, form_tab2 = st.tabs(["Add establishment", "Report establishment"])

    with form_tab1:
        st.markdown(" ")

        st.markdown("**Location**")

        if "form_geo_active" not in st.session_state:
            st.session_state["form_geo_active"] = False

        geo_lat = st.session_state.get("form_geo_lat")
        geo_lon = st.session_state.get("form_geo_lon")

        if geo_lat is not None:
            st.success(f"Current location detected: {geo_lat:.6f}, {geo_lon:.6f}")

        if st.button("Use my current location", key="form_geo_trigger", use_container_width=True):
            st.session_state["form_geo_active"] = True
        st.caption("Tap the button above, then tap the location button that appears to confirm.")

        form_geo_slot = st.empty()
        if st.session_state["form_geo_active"]:
            with form_geo_slot.container():
                location = streamlit_geolocation()
                if location and location.get("latitude") is not None:
                    st.session_state["form_geo_lat"] = location["latitude"]
                    st.session_state["form_geo_lon"] = location["longitude"]
                    st.session_state["form_geo_active"] = False
                    st.rerun()

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
            is_favorite = st.checkbox("Add to Favorites")
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
                    "favorite": is_favorite,
                    "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                save_data(data)
                st.success(f"{Name} added successfully!")
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
                st.warning(f"{selected} has been reported and marked as disputed.")
        else:
            st.info("No confirmed establishments to report yet.")

# ---------- LIST PAGE ----------
elif st.session_state.page == "List":
    st.subheader("All establishments")
    data = load_data()

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        search = st.text_input("Search", placeholder="Search by name, street or region...")
    with filter_col2:
        fav_filter = st.selectbox("Favorites", ["All", "Favorites only"], key="list_fav_filter")

    full_data = load_data()

    display_data = full_data.copy()

    if search:
        display_data = [e for e in display_data if
                        search.lower() in e["Name"].lower() or
                        search.lower() in e["Street"].lower() or
                        search.lower() in e["Location"].lower()]

    if fav_filter == "Favorites only":
        display_data = [e for e in display_data if e.get("favorite", False)]

    if display_data:
        for i, e in enumerate(display_data):
            if e["status"] == "confirmed":
                icon = "✅"
            elif e["status"] == "disputed":
                icon = "⚠️"
            else:
                icon = "❌"

            badge_class = BADGE_CLASS.get(e["Type"], "badge-other")

            st.markdown(f"""
            <div class="establishment-card">
                <div class="card-top">
                    <div class="card-left">
                        <div class="establishment-name">
                            {icon} {e['Name']}
                        </div>
                        <div class="establishment-meta">
                            {e['Street']} · {e['Location']}
                        </div>
                        <div class="establishment-meta">
                            Updated {e.get("last_updated", "Never")}
                        </div>
                    </div>
                    <span class="badge {badge_class}">
                        {e['Type']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Find the real index in full_data for safe saving
            real_i = next((j for j, d in enumerate(full_data) if d["Name"] == e["Name"] and d["Street"] == e["Street"]),
                          None)

            action1, action2, action3, action4 = st.columns(4)
            with action1:
                if st.button("Edit", key=f"Edit_{i}", use_container_width=True):
                    st.session_state["Editing"] = i
            with action2:
                if e["status"] in ["rejected", "disputed"]:
                    if st.button("Restore", key=f"Resolve_yes_{i}", use_container_width=True):
                        full_data[real_i]["status"] = "confirmed"
                        full_data[real_i]["reports"] = 0
                        full_data[real_i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        save_data(full_data)
                        st.rerun()
                else:
                    if st.button("Report", key=f"Resolve_no_{i}", use_container_width=True):
                        reports = e.get("reports", 0) + 1
                        full_data[real_i]["reports"] = reports
                        if reports >= 2:
                            full_data[real_i]["status"] = "rejected"
                        else:
                            full_data[real_i]["status"] = "disputed"
                        full_data[real_i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                        save_data(full_data)
                        st.rerun()
            with action3:
                heart = "❤️" if e.get("favorite", False) else "🤍"
                if st.button(heart, key=f"Fav_{i}", use_container_width=True):
                    full_data[real_i]["favorite"] = not e.get("favorite", False)
                    save_data(full_data)
                    st.rerun()
            with action4:
                if st.button("Delete", key=f"Delete_{i}", use_container_width=True):
                    st.session_state[f"confirm_delete_{i}"] = True

            if st.session_state.get(f"confirm_delete_{i}"):
                st.warning(f"Are you sure you want to delete **{e['Name']}**?")
                confirm1, confirm2 = st.columns(2)
                with confirm1:
                    if st.button("Yes, delete", key=f"confirm_yes_{i}", use_container_width=True):
                        full_data.pop(real_i)
                        save_data(full_data)
                        st.session_state[f"confirm_delete_{i}"] = False
                        st.rerun()
                with confirm2:
                    if st.button("Cancel", key=f"confirm_no_{i}", use_container_width=True):
                        st.session_state[f"confirm_delete_{i}"] = False
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
                    full_data[real_i].update({
                        "Name": new_nombre,
                        "Type": new_tipo,
                        "Street": new_calle,
                        "Number": int(new_numero),
                        "Location": new_localidad,
                        "axisX": new_ejeX,
                        "axisY": new_ejeY,
                    })
                    full_data[real_i]["last_updated"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    save_data(full_data)
                    st.session_state["Editing"] = None
                    st.success("Changes saved!")
                    st.rerun()
    else:
        st.info("No establishments added yet.")

# ---------- MAP PAGE ----------
elif st.session_state.page == "Map":
    map_tab, nearby_tab = st.tabs(["Map", "Nearby"])

    with map_tab:
        data = load_data()
        if data:
            col1, col2, col3 = st.columns(3)
            with col1:
                type_filter = st.multiselect("Filter by type", TYPES, default=TYPES)
            with col2:
                status_filter = st.multiselect("Filter by status", ["confirmed", "disputed", "rejected"],
                                               default=["confirmed", "disputed", "rejected"])
            with col3:
                map_fav_filter = st.selectbox("Favorites", ["All", "Favorites only"], key="map_fav_filter")

            filtered_data = [e for e in data if e["Type"] in type_filter and e["status"] in status_filter]
            if map_fav_filter == "Favorites only":
                filtered_data = [e for e in filtered_data if e.get("favorite", False)]

            df = pd.DataFrame(filtered_data) if filtered_data else None

            # Geolocation for map
            st.markdown("**Show my location on the map**")

            if "map_geo_active" not in st.session_state:
                st.session_state["map_geo_active"] = False

            user_lat = st.session_state.get("map_geo_lat")
            user_lon = st.session_state.get("map_geo_lon")

            if st.button("Show my location", key="map_geo_trigger", use_container_width=True):
                st.session_state["map_geo_active"] = True
            st.caption("Tap the button above, then tap the location button that appears to confirm.")

            map_geo_slot = st.empty()
            if st.session_state["map_geo_active"]:
                with map_geo_slot.container():
                    map_location = streamlit_geolocation()
                    if map_location and map_location.get("latitude") is not None:
                        st.session_state["map_geo_lat"] = map_location["latitude"]
                        st.session_state["map_geo_lon"] = map_location["longitude"]
                        st.session_state["map_geo_active"] = False
                        st.rerun()

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

    with nearby_tab:
        data = load_data()
        confirmed_only = [e for e in data if e["status"] == "confirmed"]

        st.markdown("**Find establishments near you**")

        if "nearby_lat" not in st.session_state:
            st.session_state["nearby_lat"] = None
            st.session_state["nearby_lon"] = None
        if "nearby_geo_active" not in st.session_state:
            st.session_state["nearby_geo_active"] = False

        button_label = "Refresh Location" if st.session_state["nearby_lat"] else "Find Nearby Establishments"

        if st.button(button_label, key="nearby_geo_trigger", use_container_width=True):
            st.session_state["nearby_geo_active"] = True
        st.caption("Tap the button above, then tap the location button that appears to confirm.")

        nearby_geo_slot = st.empty()
        if st.session_state["nearby_geo_active"]:
            with nearby_geo_slot.container():
                nearby_location = streamlit_geolocation()
                if nearby_location and nearby_location.get("latitude") is not None:
                    st.session_state["nearby_lat"] = nearby_location["latitude"]
                    st.session_state["nearby_lon"] = nearby_location["longitude"]
                    st.session_state["nearby_geo_active"] = False
                    st.rerun()

        if st.session_state["nearby_lat"] is not None:
            ulat = st.session_state["nearby_lat"]
            ulon = st.session_state["nearby_lon"]

            nearby_col1, nearby_col2 = st.columns(2)
            with nearby_col1:
                nearby_type_filter = st.multiselect(
                    "Filter by type",
                    TYPES,
                    default=TYPES,
                    key="nearby_type_filter"
                )
            with nearby_col2:
                nearby_fav_filter = st.selectbox("Favorites", ["All", "Favorites only"], key="nearby_fav_filter")

            filtered_confirmed = [e for e in confirmed_only if e["Type"] in nearby_type_filter]
            if nearby_fav_filter == "Favorites only":
                filtered_confirmed = [e for e in filtered_confirmed if e.get("favorite", False)]

            if filtered_confirmed:
                for e in filtered_confirmed:
                    e["_distance"] = haversine_distance(ulat, ulon, e["axisX"], e["axisY"])

                nearest = sorted(filtered_confirmed, key=lambda x: x["_distance"])[:10]

                for idx, e in enumerate(nearest):
                    badge_class = BADGE_CLASS.get(e["Type"], "badge-other")
                    dist_text = format_distance(e["_distance"])

                    st.markdown(f"""
                    <div class="establishment-card">
                        <div class="card-top">
                            <div class="card-left">
                                <div class="establishment-name">
                                    {e['Name']}
                                </div>
                                <div class="establishment-meta">
                                    {e['Street']} · {e['Location']}
                                </div>
                                <div class="establishment-meta">
                                    {dist_text} away · Updated {e.get("last_updated", "Never")}
                                </div>
                            </div>
                            <span class="badge {badge_class}">
                                {e['Type']}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    nav_url = f"https://www.google.com/maps/dir/?api=1&destination={e['axisX']},{e['axisY']}&travelmode=walking"

                    st.markdown(f"""
                    <a href="{nav_url}" target="_blank" style="text-decoration:none;">
                        <div style="
                            background-color:#7c3aed;
                            color:#ffffff;
                            text-align:center;
                            border-radius:8px;
                            padding:10px 0;
                            font-weight:600;
                            font-size:0.95rem;
                            margin-bottom:18px;
                        ">
                            Navigate
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
            else:
                st.info("No confirmed establishments match your filter.")
        else:
            st.info("Tap the button above to allow location access and find establishments near you.")
