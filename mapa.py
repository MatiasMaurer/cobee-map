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

# ---------- APP ----------
st.set_page_config(page_title="Cobee Map", layout="wide")
st.title("Cobee Establishments")

tab1, tab2, tab3 = st.tabs(["📋 Form", "📄 List", "🗺️ Map"])

# ---------- FORM TAB ----------
with tab1:
    form_tab1, form_tab2 = st.tabs(["Add establishment", "Report establishment"])

    with form_tab1:
        st.subheader("Add a new establishment")
        with st.form("add_form"):
            Name = st.text_input("Establishment name")
            Type = st.selectbox("Type", ["Supermarket", "Restaurant", "Transit", "Coffee Shop", "Tabacs", "Other"])
            Street = st.text_input("Street")
            Number = st.number_input("Number", min_value=0, step=1)
            Location = st.text_input("Region")
            axisX = st.number_input("Latitude", format="%.8f")
            axisY = st.number_input("Longitude", format="%.8f")
            submitted = st.form_submit_button("Add establishment")

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
        st.subheader("Report an establishment")
        data = load_data()
        confirmed = [e for e in data if e["status"] == "confirmed"]
        if confirmed:
            names = [e["Name"] for e in confirmed]
            selected = st.selectbox("Select establishment to report", names)
            reason = st.text_area("Reason (optional)")
            if st.button("Report establishment"):
                for e in data:
                    if e["Name"] == selected:
                        e["status"] = "disputed"
                save_data(data)
                st.warning(f"⚠️ {selected} has been reported and marked as disputed.")
        else:
            st.info("No confirmed establishments to report yet.")

# ---------- LIST TAB ----------
with tab2:
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

            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"{icon} **{e['Name']}** — {e['Type']} — {e['Street']}, {e['Location']}")
            with col2:
                if st.button("✏️ Edit", key=f"Edit_{i}"):
                    st.session_state["Editing"] = i

            if st.session_state.get("Editing") == i:
                with st.form(f"Edit_form_{i}"):
                    new_nombre = st.text_input("Name", value=e["Name"])
                    new_tipo = st.selectbox("Type", ["Supermarket", "Restaurant", "Transit", "Coffee Shop", "Tabacs", "Other"], index=["Supermarket", "Restaurant", "Transit", "Coffee Shop", "Tabacs", "Other"].index(e["Type"]))
                    new_calle = st.text_input("Street", value=e["Street"])
                    new_numero = st.number_input("Number", min_value=0, step=1, value=e["Number"])
                    new_localidad = st.text_input("Region", value=e["Location"])
                    new_ejeX = st.number_input("Latitude", format="%.8f", value=e["axisX"])
                    new_ejeY = st.number_input("Longitude", format="%.8f", value=e["axisY"])
                    save_edit = st.form_submit_button("Save changes")

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
# ---------- MAP TAB ----------
with tab3:
    data = load_data()
    if data:
        df = pd.DataFrame(data)

        color_map = {"Supermarket": "green", "Restaurant": "orange", "Transit": "red", "Coffee Shop": "Blue", "Tabacs": "pink", "Other": "Yellow"}
        df["color"] = df["Type"].map(color_map)

        fig = px.scatter_map(
            df,
            lat="axisX",
            lon="axisY",
            hover_name="Name",
            hover_data={"Type": True, "Street": True, "Location": True, "axisX": False, "axisY": False, "color": False, "status": False},
            color="Type",
            color_discrete_map=color_map,
            zoom=12,
            height=700,
        )
        fig.update_traces(marker=dict(size=14, opacity=0.9))
        fig.update_layout(
            map_style="carto-darkmatter",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No establishments to show on the map yet.")


