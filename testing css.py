# ---------- STYLING ----------
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0f0f0f; }

    /* Sidebar */

section[data-testid="stSidebar"] {

    background-color: #111111 !important;

    border-right: 1px solid #1f1f1f !important;

    min-width: 220px !important;

    max-width: 220px !important;

}

section[data-testid="stSidebar"][aria-expanded="false"] {

    min-width: 220px !important;

    max-width: 220px !important;

}
    }
    [data-testid="stSidebar"] * { color: #ffffff; }

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
    @media (max-width: 768px) {
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
    }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }
</style>