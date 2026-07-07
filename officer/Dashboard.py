import base64
import json
import os
import textwrap

import ee
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from shapely.geometry import Point, shape

from utils.supabase_db import db

DISPLAY_DEPARTMENT = "Department Of Agriculture"
GEE_PROJECT_ID = "intelligence-paddy-system"
GEOJSON_PATH = "assets/Kedah_PBT_2015.geojson"
DISTRICT_FIELD = "name"
DASHBOARD_BACKGROUND = "assets/Background3.jpg"
PADDY_FIELDS_PATH = "assets/paddy_fields.geojson"

DISTRICT_OPTIONS = {
    "Alor Setar": "Majlis Bandaraya Alor Setar",
    "Pendang": "Majlis Daerah Pendang",
    "Kubang Pasu": "Majlis Daerah Kubang Pasu",
    "Padang Terap": "Majlis Daerah Padang Terap",
    "Yan": "Majlis Daerah Yan",
}

AREA_ALIASES = {
    "Alor Setar": ["Alor Setar", "Kota Setar", "Majlis Bandaraya Alor Setar"],
    "Pendang": ["Pendang", "Majlis Daerah Pendang"],
    "Kubang Pasu": ["Kubang Pasu", "Majlis Daerah Kubang Pasu"],
    "Padang Terap": ["Padang Terap", "Majlis Daerah Padang Terap"],
    "Yan": ["Yan", "Majlis Daerah Yan"],
}


# =========================================
# FETCH FARMERS WITH LOCATION
# =========================================
def fetch_farmers_with_location():
    try:
        response = (
            db.service_client.table("farmers")
            .select("id, farmer_id, full_name, region, area, latitude, longitude")
            .execute()
        )
        return response.data or []
    except Exception as e:
        print("fetch farmers error:", e)
        return []


# =========================================
# FETCH DETECTION LOCATIONS
# =========================================
def fetch_detection_locations():
    try:
        response = (
            db.service_client.table("detection_history")
            .select("id, report_id, farmer_id, farmer_name, disease, region, area, detection_latitude, detection_longitude")
            .execute()
        )
        return response.data or []
    except Exception as e:
        print("fetch detection locations error:", e)
        return []


# =========================================
# UPDATE FARMER LOCATION
# =========================================
def update_farmer_location(farmer_id, lat, lon):
    try:
        db.service_client.table("farmers").update({
            "latitude": lat,
            "longitude": lon
        }).eq("id", farmer_id).execute()
        return True
    except Exception as e:
        print("update error:", e)
        return False


# =========================================
# DELETE FARMER LOCATION
# =========================================
def delete_farmer_location(farmer_id):
    try:
        db.service_client.table("farmers").update({
            "latitude": None,
            "longitude": None
        }).eq("id", farmer_id).execute()
        return True
    except Exception as e:
        print("delete location error:", e)
        return False


# =====================================================
# BACKGROUND
# =====================================================
def set_dashboard_background(image_path=DASHBOARD_BACKGROUND):
    if not image_path or not os.path.exists(image_path):
        return

    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        print(f"set_dashboard_background error: {e}")


# =====================================================
# LOG ACTIVITY FUNCTION
# =====================================================
def log_officer_activity(officer_id, officer_name, action, description):
    try:
        db.service_client.table("activity_logs_officer").insert({
            "officer_id": officer_id,
            "officer_name": officer_name,
            "action": action,
            "description": description
        }).execute()
    except Exception as e:
        print(f"Log error: {e}")


# =====================================================
# SAFE LOGOUT FUNCTION
# =====================================================
def handle_logout():
    try:
        officer_id = st.session_state.get("officer_id")
        officer_name = st.session_state.get("officer_name") or st.session_state.get("full_name")

        if officer_id and officer_name:
            log_officer_activity(
                officer_id=officer_id,
                officer_name=officer_name,
                action="LOGOUT",
                description=f"Officer {officer_name} ({officer_id}) logged out"
            )

        try:
            db.client.auth.sign_out()
        except Exception:
            pass

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.success("✅ Signed out successfully!")
        st.switch_page("pages/3_Login.py")

    except Exception as e:
        st.error(f"Logout error: {e}")


# =====================================================
# MAIN DASHBOARD
# =====================================================
def render_dashboard():
    inject_dashboard_css()
    set_dashboard_background()

    with st.sidebar:
        if "user_id" in st.session_state:
            officer_data = get_officer_data()

            if officer_data:
                st.session_state.officer_id = officer_data.get("officer_id")
                st.session_state.officer_name = officer_data.get("officer_name")

                st.markdown(
                    f"""
                    <div class="sidebar-officer-card">
                        <div class="sidebar-officer-name">
                            {officer_data.get('officer_name', st.session_state.get('full_name', 'Officer'))}
                        </div>
                        <div class="sidebar-officer-id">
                            {officer_data.get('officer_id', 'N/A')}
                        </div>
                        <div class="sidebar-officer-dept">
                            {DISPLAY_DEPARTMENT}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown('<div class="sidebar-nav-title">🌾 Officer Panel</div>', unsafe_allow_html=True)

        menu = st.radio(
            "Navigation",
            [
                "🏠 Home",
                "👤 Profile",
                "📄 Report",
                "💬 Forum",
                "🤖 AI Assistant",
                "🚪 Sign Out"
            ],
            label_visibility="collapsed"
        )

    if menu == "🚪 Sign Out":
        handle_logout()
        return None

    if menu == "🏠 Home":
        render_home_dashboard()

    return menu


# =====================================================
# GET OFFICER DATA
# =====================================================
def get_officer_data():
    if "user_id" not in st.session_state:
        return None

    try:
        officer_response = (
            db.service_client.table("officers")
            .select("*")
            .eq("id", st.session_state.user_id)
            .execute()
        )

        user_response = (
            db.service_client.table("users")
            .select("full_name, email, phone, region, profile_image_url")
            .eq("id", st.session_state.user_id)
            .execute()
        )

        officer = officer_response.data[0] if officer_response.data else {}
        user_data = user_response.data[0] if user_response.data else {}

        if not officer and not user_data:
            return None

        return {
            "id": st.session_state.user_id,
            "officer_id": officer.get("officer_id", f"OFF-{st.session_state.user_id[:8].upper()}"),
            "officer_name": officer.get("officer_name") or user_data.get("full_name", ""),
            "role": officer.get("role", "officer"),
            "email": officer.get("email") or user_data.get("email", ""),
            "phone": officer.get("phone") or user_data.get("phone", ""),
            "region": officer.get("region") or user_data.get("region", ""),
            "profile_img_link": officer.get("profile_img_link") or user_data.get("profile_image_url")
        }

    except Exception as e:
        st.error(f"Error loading officer data: {e}")
        return None


# =====================================================
# GEE HELPERS
# =====================================================
@st.cache_resource(show_spinner=False)
def init_gee():
    ee.Initialize(project=GEE_PROJECT_ID)
    return True


@st.cache_data(show_spinner=False)
def load_geojson_data():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_paddy_fields_data():
    if not os.path.exists(PADDY_FIELDS_PATH):
        return {"type": "FeatureCollection", "features": []}

    with open(PADDY_FIELDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_clicked_paddy_field(lat, lon):
    paddy_data = load_paddy_fields_data()
    clicked_point = Point(lon, lat)

    for feature in paddy_data.get("features", []):
        try:
            polygon = shape(feature.get("geometry"))
            if polygon.contains(clicked_point):
                return feature
        except Exception:
            continue

    return None


def get_paddy_fields_for_officer_area(officer_area_key):
    paddy_data = load_paddy_fields_data()
    district_name = DISTRICT_OPTIONS.get(officer_area_key)

    if not district_name:
        return []

    kedah_geojson = load_geojson_data()

    district_features = [
        f for f in kedah_geojson.get("features", [])
        if f.get("properties", {}).get(DISTRICT_FIELD) == district_name
    ]

    if not district_features:
        return []

    district_shape = shape(district_features[0]["geometry"])

    matched_fields = []

    for feature in paddy_data.get("features", []):
        try:
            props = feature.get("properties", {})

            # ONLY KEEP STRONG MATCH - Filter for rice-related polygons only
            if not (
                props.get("crop") == "rice"
                or props.get("rice") == "yes"
            ):
                continue

            field_shape = shape(feature.get("geometry"))

            if field_shape.intersects(district_shape):
                feature["_area_size"] = field_shape.area
                matched_fields.append(feature)

        except Exception:
            continue

    # Sort by area size (largest first)
    matched_fields = sorted(
        matched_fields,
        key=lambda f: f.get("_area_size", 0),
        reverse=True
    )
    
    # Show only largest paddy polygons to reduce map clutter
    matched_fields = matched_fields[:35]
    
    return matched_fields


@st.cache_resource(show_spinner=False)
def load_kedah_fc():
    init_gee()
    geojson_data = load_geojson_data()
    return ee.FeatureCollection(geojson_data)


def add_ee_image_layer(folium_map, ee_image, vis_params, layer_name, shown=True, opacity=1.0):
    map_id = ee.Image(ee_image).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id["tile_fetcher"].url_format,
        attr="Google Earth Engine",
        name=layer_name,
        overlay=True,
        control=True,
        show=shown,
        opacity=opacity,
    ).add_to(folium_map)


@st.cache_data(show_spinner=False)
def get_district_map_html(selected_area):
    init_gee()
    kedah_fc = load_kedah_fc()
    geojson_data = load_geojson_data()

    district_name = DISTRICT_OPTIONS[selected_area]
    district = kedah_fc.filter(ee.Filter.eq(DISTRICT_FIELD, district_name))
    district_geom = district.geometry()

    district_count = district.size().getInfo()
    if district_count == 0:
        return None, f"No district geometry found for {selected_area}."

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(district_geom)
        .filterDate("2023-01-01", "2025-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
        .sort("CLOUDY_PIXEL_PERCENTAGE")
    )

    image_count = collection.size().getInfo()
    if image_count == 0:
        return None, f"No Sentinel-2 imagery found for {selected_area}."

    image = collection.first()
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    fmap = folium.Map(location=[6.1, 100.5], zoom_start=10, tiles="OpenStreetMap")

    selected_features = [
        feature for feature in geojson_data.get("features", [])
        if feature.get("properties", {}).get(DISTRICT_FIELD) == district_name
    ]

    if selected_features:
        district_geojson = {
            "type": "FeatureCollection",
            "features": selected_features
        }

        folium.GeoJson(
            district_geojson,
            name="District Boundary",
            style_function=lambda _: {
                "color": "#1d4ed8",
                "weight": 2,
                "fillOpacity": 0.0,
            },
        ).add_to(fmap)

        temp_geojson = folium.GeoJson(district_geojson)
        bounds = temp_geojson.get_bounds()
        if bounds:
            fmap.fit_bounds(bounds)

    add_ee_image_layer(
        fmap,
        image.clip(district_geom),
        {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
        "Sentinel-2 RGB",
        shown=False,
        opacity=1.0,
    )

    add_ee_image_layer(
        fmap,
        ndvi.clip(district_geom),
        {"min": 0, "max": 1, "palette": ["red", "yellow", "green"]},
        "NDVI",
        shown=True,
        opacity=0.85,
    )

    # =========================================
    # ADD ASSIGNED FARMER FIELD AREAS + MARKERS
    # =========================================
    farmers = fetch_farmers_with_location()

    for f in farmers:
        lat = f.get("latitude")
        lon = f.get("longitude")

        # Only show farmers assigned inside currently selected map area
        if not row_matches_area(f, selected_area):
            continue

        if lat and lon:
            assigned_field = find_clicked_paddy_field(lat, lon)

            # Blue highlighted field area for assigned farmer location
            if assigned_field:
                folium.GeoJson(
                    assigned_field,
                    name="Assigned Farmer Paddy Field",
                    style_function=lambda _: {
                        "color": "#2563eb",
                        "weight": 3,
                        "fillColor": "#60a5fa",
                        "fillOpacity": 0.22,
                    },
                    tooltip=f"Assigned field: {f.get('full_name')} ({f.get('farmer_id')})"
                ).add_to(fmap)

            popup_html = f"""
            <b>Farmer:</b> {f.get('full_name')}<br>
            <b>ID:</b> {f.get('farmer_id')}<br>
            <b>Region:</b> {f.get('region')}<br>
            <b>Area:</b> {f.get('area')}<br>
            <b>Location:</b> Assigned
            """

            folium.Marker(
                location=[lat, lon],
                popup=popup_html,
                icon=folium.Icon(color="blue", icon="user")
            ).add_to(fmap)

    # =========================================
    # ADD DETECTION HISTORY PINPOINT MARKERS
    # =========================================
    detection_locations = fetch_detection_locations()

    for d in detection_locations:
        d_lat = d.get("detection_latitude")
        d_lon = d.get("detection_longitude")

        if not row_matches_area(d, selected_area):
            continue

        if d_lat and d_lon:
            popup_html = f"""
            <b>Report ID:</b> {d.get('report_id') or d.get('id')}<br>
            <b>Disease:</b> {d.get('disease', 'Unknown')}
            """

            folium.Marker(
                location=[d_lat, d_lon],
                popup=popup_html,
                tooltip="Detection Point",
                icon=folium.Icon(
                    color="red",
                    icon="exclamation-triangle",
                    prefix="fa"
                )
            ).add_to(fmap)

    folium.LayerControl(collapsed=False).add_to(fmap)

    return fmap._repr_html_(), None


def build_district_map(selected_area):
    try:
        map_html, map_error = get_district_map_html(selected_area)

        if map_error:
            st.warning(map_error)
            return

        components.html(map_html, height=600)

    except Exception as e:
        st.error(f"Failed to load GEE map: {e}")


# =====================================================
# DASHBOARD DATA HELPERS
# =====================================================
def normalize_text(value):
    return str(value).strip().lower() if value is not None else ""


def resolve_dashboard_area(region):
    if normalize_text(region) in ["kota setar", "alor setar"]:
        return "Alor Setar"
    return region


def row_matches_area(row, selected_area):
    aliases = [normalize_text(x) for x in AREA_ALIASES.get(selected_area, [selected_area])]
    area_value = normalize_text(row.get("area"))
    region_value = normalize_text(row.get("region"))
    return area_value in aliases or region_value in aliases


def load_area_data(selected_area):
    try:
        farmer_response = (
            db.service_client.table("farmers")
            .select("farmer_id, full_name, region, area, email")
            .execute()
        )

        report_response = (
            db.service_client.table("detection_history")
            .select("id, report_id, farmer_name, farmer_id, disease, status, area, region, created_at")
            .execute()
        )

        farmers_raw = farmer_response.data or []
        reports_raw = report_response.data or []

        farmer_rows = [row for row in farmers_raw if row_matches_area(row, selected_area)]
        report_rows = [row for row in reports_raw if row_matches_area(row, selected_area)]

        df_farmers = pd.DataFrame(farmer_rows)
        df_reports = pd.DataFrame(report_rows)

        if df_farmers.empty:
            df_farmers = pd.DataFrame(columns=["farmer_id", "full_name", "region", "area", "email"])

        if df_reports.empty:
            df_reports = pd.DataFrame(columns=["id", "report_id", "farmer_name", "farmer_id", "disease", "status", "area", "region", "created_at"])

        if not df_reports.empty:
            df_reports["status"] = df_reports["status"].fillna("PENDING").astype(str)
            df_reports["disease"] = df_reports["disease"].fillna("Unknown").astype(str)
            df_reports["created_at"] = pd.to_datetime(df_reports["created_at"], errors="coerce")
            df_reports = df_reports.sort_values(by="created_at", ascending=False, na_position="last").reset_index(drop=True)
            df_reports["created_at_display"] = df_reports["created_at"].dt.strftime("%d %b %Y, %I:%M %p").fillna("N/A")
            df_reports["report_id_display"] = df_reports["report_id"].fillna(df_reports["id"].astype(str))

        return df_farmers, df_reports

    except Exception as e:
        st.error(f"Failed to load area data: {e}")
        return pd.DataFrame(), pd.DataFrame()


# =====================================================
# UI STYLES
# =====================================================
def inject_dashboard_css():
    st.markdown("""
    <style>
    :root {
        --gov-text: #123524;
        --gov-text-soft: #5c6d62;
        --gov-green: #14532d;
        --gov-green-2: #1f7a45;
        --gov-green-3: #2f8a4f;
        --gov-chip: #e8f5e9;
        --gov-border: rgba(20, 83, 45, 0.12);
        --gov-radius-xl: 30px;
        --gov-radius-lg: 24px;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.55rem !important;
        padding-bottom: 2.2rem !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(67,160,71,0.06), transparent 28%),
            linear-gradient(180deg, #f7faf8 0%, #f1f6f3 100%);
    }

    .sidebar-officer-card {
        text-align: center;
        padding: 16px;
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(244,249,246,0.97) 100%);
        border: 1px solid rgba(16,59,45,0.08);
        border-radius: 20px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(16,59,45,0.06);
    }

    .sidebar-officer-name {
        font-size: 18px;
        font-weight: 800;
        color: #14532d;
        line-height: 1.3;
    }

    .sidebar-officer-id {
        font-size: 13px;
        color: #4d665b;
        margin-top: 5px;
        font-weight: 700;
    }

    .sidebar-officer-dept {
        font-size: 12px;
        color: #73887f;
        margin-top: 5px;
        font-weight: 600;
    }

    .sidebar-nav-title {
        font-size: 18px;
        font-weight: 800;
        color: #123524;
        margin: 6px 0 10px 0;
    }

    .paddy-hero {
        background:
            linear-gradient(135deg, rgba(10,56,32,0.98) 0%, rgba(20,83,45,0.96) 42%, rgba(39,119,63,0.94) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: var(--gov-radius-xl);
        padding: 28px 32px;
        color: white;
        box-shadow: 0 24px 56px rgba(15, 81, 50, 0.20);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }

    .paddy-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(120deg, rgba(255,255,255,0.06), transparent 40%),
            radial-gradient(circle at top right, rgba(255,255,255,0.12), transparent 34%);
        pointer-events: none;
    }

    .paddy-hero::after {
        content: "";
        position: absolute;
        top: -72px;
        right: -58px;
        width: 230px;
        height: 230px;
        background: rgba(255,255,255,0.07);
        border-radius: 50%;
    }

    .paddy-hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 14px;
        position: relative;
        z-index: 2;
        backdrop-filter: blur(8px);
    }

    .paddy-hero-title {
        font-size: 34px;
        font-weight: 800;
        line-height: 1.06;
        margin-bottom: 8px;
        position: relative;
        z-index: 2;
        letter-spacing: -0.02em;
        color: white;
    }

    .paddy-hero-subtitle {
        font-size: 15px;
        line-height: 1.7;
        color: rgba(255,255,255,0.92);
        position: relative;
        z-index: 2;
        max-width: 900px;
        margin-bottom: 14px;
    }

    .paddy-hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
        position: relative;
        z-index: 2;
    }

    .paddy-badge {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        background: rgba(255,255,255,0.16);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.20);
        backdrop-filter: blur(6px);
    }

    .dashboard-green-shell {
        background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 26px;
        box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34);
        padding: 22px 22px 18px 22px;
        backdrop-filter: blur(2px);
        margin-bottom: 16px;
    }

    .dashboard-green-title {
        font-size: 24px;
        font-weight: 800;
        color: #f4fff7;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }

    .dashboard-green-subtitle {
        font-size: 14px;
        color: rgba(240,255,244,0.88);
        margin-top: 0;
        margin-bottom: 18px;
        line-height: 1.65;
        font-weight: 600;
    }

    .dashboard-section-header {
        background: linear-gradient(180deg, #ffffff 0%, #f8fcfa 100%);
        border: 1px solid rgba(20, 83, 45, 0.10);
        border-radius: 22px;
        box-shadow: 0 12px 28px rgba(16,59,45,0.07);
        padding: 18px 20px 16px 20px;
        margin-bottom: 10px;
    }

    .dashboard-section-title {
        font-size: 22px;
        font-weight: 800;
        color: #103b2d;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }

    .dashboard-section-subtitle {
        font-size: 14px;
        color: #5f756a;
        margin-bottom: 0;
        line-height: 1.6;
        font-weight: 600;
    }

    .soft-banner {
        background: linear-gradient(180deg, #edf6ef 0%, #e5f1e8 100%);
        border: 1px solid rgba(20, 83, 45, 0.15);
        border-radius: 16px;
        padding: 13px 15px;
        color: #244634;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 14px;
        line-height: 1.65;
    }

    .dashboard-summary-shell {
        background: linear-gradient(180deg, #ffffff 0%, #f8fcfa 100%);
        border: 1px solid rgba(20, 83, 45, 0.10);
        border-radius: 24px;
        box-shadow: 0 12px 28px rgba(16,59,45,0.07);
        padding: 20px;
    }

    .dashboard-summary-title {
        font-size: 22px;
        font-weight: 800;
        color: #103b2d;
        margin-bottom: 14px;
        letter-spacing: -0.02em;
    }

    .summary-stat-card {
        background: linear-gradient(180deg, #fbfdfb 0%, #f5faf6 100%);
        border: 1px solid rgba(20, 83, 45, 0.08);
        border-radius: 18px;
        padding: 14px 15px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        margin-bottom: 12px;
    }

    .summary-stat-label {
        font-size: 11.5px;
        font-weight: 800;
        color: #728378;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }

    .summary-stat-value {
        font-size: 28px;
        font-weight: 800;
        color: #103b2d;
        line-height: 1;
        margin-bottom: 6px;
    }

    .summary-stat-note {
        font-size: 13px;
        color: #5c6d62;
        line-height: 1.5;
        font-weight: 600;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(16,59,45,0.08);
        box-shadow: 0 10px 28px rgba(16,59,45,0.06);
        background: rgba(255,255,255,0.99) !important;
    }

    div[data-testid="stForm"] {
        background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 26px !important;
        box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34) !important;
        padding: 22px 22px 18px 22px !important;
        backdrop-filter: blur(2px) !important;
    }

    div[data-testid="stForm"] label p {
        color: #f4fff7 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stSelectbox"] label p {
        color: #123524 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stForm"] div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.98) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 14px !important;
        color: #123524 !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border: 1px solid rgba(20, 83, 45, 0.14) !important;
        background: rgba(255,255,255,0.98) !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(20, 83, 45, 0.10) !important;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05) !important;
        height: 46px !important;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(135deg, #14532d 0%, #1f7a45 100%) !important;
        color: white !important;
        border: none !important;
    }

    .dashboard-map-wrap {
        border-radius: 18px;
        overflow: hidden;
    }

    /* Green container for Set Farmer Location section */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-green-marker),
    div[data-testid="stVerticalBlock"]:has(.dashboard-green-marker) {
        background: linear-gradient(135deg, rgba(12,58,34,0.95) 0%, rgba(18,78,42,0.94) 45%, rgba(28,110,61,0.92) 100%) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 26px !important;
        box-shadow: 0 24px 60px rgba(6, 30, 17, 0.34) !important;
        padding: 22px !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-green-marker) label p,
    div[data-testid="stVerticalBlock"]:has(.dashboard-green-marker) label p {
        color: #f4fff7 !important;
        font-weight: 800 !important;
    }

    @media (max-width: 1100px) {
        .paddy-hero-title {
            font-size: 30px;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# =====================================================
# HOME DASHBOARD
# =====================================================
def render_home_dashboard():
    officer_data = get_officer_data()
    region_name = officer_data.get("region", "Monitoring Area") if officer_data else "Monitoring Area"
    officer_name = officer_data.get("officer_name", st.session_state.get("full_name", "Officer")) if officer_data else st.session_state.get("full_name", "Officer")
    officer_id = officer_data.get("officer_id", "N/A") if officer_data else "N/A"

    hero_html = f"""
    <div class="paddy-hero">
        <div class="paddy-hero-kicker">Officer Identity Center</div>
        <div class="paddy-hero-title">Paddy Field Monitoring Dashboard</div>
        <div class="paddy-hero-subtitle">
            Live agricultural monitoring workspace for officer-level field oversight, area-based farmer visibility,
            detection reporting review, and satellite vegetation monitoring using Google Earth Engine.
        </div>
        <div class="paddy-hero-badges">
            <span class="paddy-badge">📍 {region_name}</span>
            <span class="paddy-badge">👤 {officer_name}</span>
            <span class="paddy-badge">🆔 {officer_id}</span>
            <span class="paddy-badge">🌾 Kedah Monitoring</span>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    if "selected_area_dashboard" not in st.session_state:
        st.session_state.selected_area_dashboard = list(DISTRICT_OPTIONS.keys())[0]

    st.markdown(
        """
        <div class="dashboard-green-shell">
            <div class="dashboard-green-title">Monitoring Area Selector</div>
            <div class="dashboard-green-subtitle">
                Choose a district coverage area, then load the latest monitoring workspace for that location.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("area_selector_form"):
        selected_area_input = st.selectbox(
            "🎯 Select Monitoring Area",
            list(DISTRICT_OPTIONS.keys()),
            index=list(DISTRICT_OPTIONS.keys()).index(st.session_state.selected_area_dashboard)
        )
        load_area_btn = st.form_submit_button("📍 Load Area Map", width="stretch")

    if load_area_btn:
        st.session_state.selected_area_dashboard = selected_area_input

    selected_area = st.session_state.selected_area_dashboard
    df_farmers, df_reports = load_area_data(selected_area)

    main_col, right_col = st.columns([3, 1], gap="large")

    with main_col:
        st.markdown(
            f"""
            <div class="soft-banner">
                <b>Coverage Region:</b> {region_name} &nbsp;|&nbsp; <b>Selected Area:</b> {selected_area}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="dashboard-section-header">
                <div class="dashboard-section-title">Satellite Monitoring Map</div>
                <div class="dashboard-section-subtitle">
                    Real Google Earth Engine district boundary with Sentinel-2 RGB and NDVI vegetation layer.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dashboard-map-wrap">', unsafe_allow_html=True)
        build_district_map(selected_area)
        st.markdown('</div>', unsafe_allow_html=True)

        # Reduced gap between top map and two cards
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

        farmer_col, report_col = st.columns(2, gap="large")

        with farmer_col:
            st.markdown(
                """
                <div class="dashboard-section-header">
                    <div class="dashboard-section-title">Farmers in Selected Area</div>
                    <div class="dashboard-section-subtitle">
                        Registered farmer profiles linked to the selected district coverage.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if df_farmers.empty:
                st.info("No farmers found for this area.")
            else:
                farmer_display = df_farmers[["farmer_id", "full_name", "region", "area"]].copy()
                farmer_display = farmer_display.rename(
                    columns={
                        "farmer_id": "Farmer ID",
                        "full_name": "Farmer Name",
                        "region": "Region",
                        "area": "Area"
                    }
                )
                st.dataframe(farmer_display, width="stretch", hide_index=True)

        with report_col:
            st.markdown(
                """
                <div class="dashboard-section-header">
                    <div class="dashboard-section-title">Reports in Selected Area</div>
                    <div class="dashboard-section-subtitle">
                        Detection history records linked to the selected district coverage.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if df_reports.empty:
                st.info("No reports found for this area.")
            else:
                report_display = df_reports[
                    ["report_id_display", "farmer_name", "farmer_id", "disease", "status", "created_at_display"]
                ].copy()
                report_display = report_display.rename(
                    columns={
                        "report_id_display": "Report ID",
                        "farmer_name": "Farmer Name",
                        "farmer_id": "Farmer ID",
                        "disease": "Disease",
                        "status": "Status",
                        "created_at_display": "Created At"
                    }
                )
                st.dataframe(report_display, width="stretch", hide_index=True)

    with right_col:
        total_farmers = len(df_farmers)
        total_reports = len(df_reports)

        if not df_reports.empty:
            healthy_count = len(df_reports[df_reports["status"].str.upper().str.contains("VALID|RESOLVED|CLOSED", na=False)])
            diseased_count = len(df_reports[df_reports["status"].str.upper().str.contains("HIGH|FLAG|UNDER|PENDING|REVIEW", na=False)])
            observation_count = len(df_reports[df_reports["status"].str.upper().str.contains("UNDER|REVIEW|PENDING", na=False)])
        else:
            healthy_count = 0
            diseased_count = 0
            observation_count = 0

        st.markdown(
            """
            <div class="dashboard-summary-shell">
                <div class="dashboard-summary-title">Area Summary</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="summary-stat-card">
                <div class="summary-stat-label">Farmers</div>
                <div class="summary-stat-value">{total_farmers}</div>
                <div class="summary-stat-note">Registered farmer records in this selected area.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="summary-stat-card">
                <div class="summary-stat-label">Reports</div>
                <div class="summary-stat-value">{total_reports}</div>
                <div class="summary-stat-note">Detection reports available for officer review.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="summary-stat-card">
                <div class="summary-stat-label">Stable Cases</div>
                <div class="summary-stat-value">{healthy_count}</div>
                <div class="summary-stat-note">Validated, resolved, or stable field cases.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="summary-stat-card">
                <div class="summary-stat-label">Active Cases</div>
                <div class="summary-stat-value">{diseased_count}</div>
                <div class="summary-stat-note">Cases requiring active officer attention or escalation.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="summary-stat-card" style="margin-bottom:0;">
                <div class="summary-stat-label">Under Observation</div>
                <div class="summary-stat-value">{observation_count}</div>
                <div class="summary-stat-note">Cases still pending, under review, or field monitoring.</div>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =====================================================
    # SET FARMER LOCATION - GREEN CARD CONTAINER
    # =====================================================
    with st.container(border=True):
        st.markdown('<div class="dashboard-green-marker"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="dashboard-green-shell">
                <div class="dashboard-green-title">Set Farmer Location</div>
                <div class="dashboard-green-subtitle">
                    Select a farmer and click map to assign location.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Filter farmer dropdown by officer region
        officer_region = region_name
        officer_area_key = resolve_dashboard_area(officer_region)
        
        farmers = [
            f for f in fetch_farmers_with_location()
            if normalize_text(f.get("region")) == normalize_text(officer_region)
        ]

        if farmers:
            farmer_dict = {
                f"{f['full_name']} ({f['farmer_id']})": f
                for f in farmers
            }

            selected_key = st.selectbox("👨‍🌾 Select Farmer", list(farmer_dict.keys()))
            selected_farmer = farmer_dict[selected_key]

            # REGION CENTERS
            region_centers = {
                "Alor Setar": [6.12, 100.37],
                "Pendang": [6.00, 100.47],
                "Kubang Pasu": [6.35, 100.43],
                "Padang Terap": [6.30, 100.65],
                "Yan": [5.80, 100.38],
            }

            # Force map to officer area key (resolved)
            center = region_centers.get(officer_area_key, [6.1, 100.5])

            m = folium.Map(location=center, zoom_start=11)

            # Add available paddy fields for officer area - FILTERED for rice only
            officer_paddy_fields = get_paddy_fields_for_officer_area(officer_area_key)

            for field in officer_paddy_fields:
                folium.GeoJson(
                    field,
                    name="Available Paddy Area",
                    style_function=lambda _: {
                        "color": "#16a34a",  # darker green
                        "weight": 1,
                        "fillColor": "#16a34a",
                        "fillOpacity": 0.08,  # reduced opacity for less dominance
                    },
                    tooltip=(
                        field.get("properties", {}).get("name")
                        or field.get("properties", {}).get("landuse")
                        or field.get("properties", {}).get("crop")
                        or "Paddy Field Area"
                    ),
                ).add_to(m)

            # DISPLAY ALL SAVED FARMER LOCATIONS UNDER OFFICER REGION
            for farmer in farmers:
                saved_lat = farmer.get("latitude")
                saved_lon = farmer.get("longitude")

                if saved_lat and saved_lon:
                    icon_color = "blue" if farmer["id"] == selected_farmer["id"] else "green"

                    folium.Marker(
                        location=[saved_lat, saved_lon],
                        popup=f"""
                        <b>{farmer.get('full_name')}</b><br>
                        Farmer ID: {farmer.get('farmer_id')}<br>
                        Region: {farmer.get('region')}<br>
                        Area: {farmer.get('area')}
                        """,
                        icon=folium.Icon(color=icon_color, icon="user")
                    ).add_to(m)

            # Force district to officer area key (resolved)
            district_name = DISTRICT_OPTIONS.get(officer_area_key)

            if district_name:
                geojson_data = load_geojson_data()
                selected_features = [
                    f for f in geojson_data.get("features", [])
                    if f.get("properties", {}).get(DISTRICT_FIELD) == district_name
                ]

                if selected_features:
                    folium.GeoJson(
                        {"type": "FeatureCollection", "features": selected_features},
                        style_function=lambda _: {
                            "color": "#16a34a",
                            "weight": 3,
                            "fillOpacity": 0.05,
                        },
                    ).add_to(m)
                    
                    # Zoom exactly to boundary
                    temp_geojson = folium.GeoJson(
                        {"type": "FeatureCollection", "features": selected_features}
                    )
                    bounds = temp_geojson.get_bounds()
                    if bounds:
                        m.fit_bounds(bounds)

            # Add highlight for matched paddy field - ORANGE HIGHLIGHT
            matched_field = st.session_state.get("matched_paddy_field")

            if matched_field:
                folium.GeoJson(
                    matched_field,
                    name="Selected Paddy Field",
                    style_function=lambda _: {
                        "color": "#f97316",
                        "weight": 5,
                        "fillColor": "#fb923c",
                        "fillOpacity": 0.55,
                    },
                    tooltip=matched_field.get("properties", {}).get("name", "Selected Paddy Field")
                ).add_to(m)

            # Enhanced map interaction with session state
            map_data = st_folium(
                m,
                height=500,
                width="100%",
                returned_objects=["last_clicked"],
                key="farmer_location_picker_map"
            )

            if map_data and map_data.get("last_clicked"):
                clicked_lat = map_data["last_clicked"]["lat"]
                clicked_lon = map_data["last_clicked"]["lng"]

                st.session_state["selected_farmer_lat"] = clicked_lat
                st.session_state["selected_farmer_lon"] = clicked_lon
                st.session_state["matched_paddy_field"] = find_clicked_paddy_field(clicked_lat, clicked_lon)

            lat = st.session_state.get("selected_farmer_lat")
            lon = st.session_state.get("selected_farmer_lon")

            if lat and lon:
                st.markdown(
    f"""
          <div style="
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.18);
                padding: 12px 16px;
                border-radius: 12px;
                color: white;
                font-weight: 700;
                font-size: 14px;
                margin-bottom: 14px;
             ">
               📍 Selected Location: {lat:.6f}, {lon:.6f}
          </div>
              """,
                 unsafe_allow_html=True
       )

            # Show detected field name under selected location - FINAL CLEAN VERSION
            matched_field = st.session_state.get("matched_paddy_field")

            if matched_field:
                props = matched_field.get("properties", {})

                if props.get("name"):
                    field_name = props["name"]
                elif props.get("crop") == "rice" or props.get("rice") == "yes":
                    field_name = "Paddy Field"
                else:
                    field_name = "Agricultural Area"

                st.markdown(
                    f"""
                    <div style="
                        background: rgba(0,255,136,0.14);
                        border: 1px solid rgba(0,255,136,0.35);
                        padding: 12px 16px;
                        border-radius: 12px;
                        color: white;
                        font-weight: 700;
                        font-size: 14px;
                        margin-bottom: 14px;
                    ">
                        🌾 Detected Paddy Field: {field_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if lat and lon:
                    st.markdown(
                        """
                        <div style="
                            background: rgba(255,193,7,0.14);
                            border: 1px solid rgba(255,193,7,0.35);
                            padding: 12px 16px;
                            border-radius: 12px;
                            color: white;
                            font-weight: 700;
                            font-size: 14px;
                            margin-bottom: 14px;
                        ">
                            ⚠️ No matching paddy polygon found at this clicked location.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Save and Delete buttons side by side
            save_col, delete_col = st.columns(2)

            with save_col:
                if st.button("💾 Save Location", type="primary", use_container_width=True):
                    if not lat or not lon:
                        st.warning("Click on the map first before saving.")
                    else:
                        if update_farmer_location(selected_farmer["id"], lat, lon):
                            st.success("✅ Farmer location saved.")
                            st.cache_data.clear()
                            st.session_state.pop("selected_farmer_lat", None)
                            st.session_state.pop("selected_farmer_lon", None)
                            st.session_state.pop("matched_paddy_field", None)
                            st.rerun()
                        else:
                            st.error("❌ Failed to save location.")

            with delete_col:
                if st.button("🗑️ Delete Location", use_container_width=True):
                    if delete_farmer_location(selected_farmer["id"]):
                        st.success("✅ Farmer location deleted.")
                        st.cache_data.clear()
                        st.session_state.pop("selected_farmer_lat", None)
                        st.session_state.pop("selected_farmer_lon", None)
                        st.session_state.pop("matched_paddy_field", None)
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete location.")

        else:
            st.warning(f"No farmers found in {officer_region} region")