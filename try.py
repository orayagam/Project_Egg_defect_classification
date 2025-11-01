import streamlit as st
import os
from pipeline import load_model, full_pipeline
from PIL import Image
import base64
import tempfile

# --- Page Config ---
st.set_page_config(page_title="Egg Defect Detection and Classification", layout="wide")

# --- Functions ---
def get_base64_of_image(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def stop_process():
    st.session_state.stop_processing = True

# --- Background Image ---
image_path = "eggs-on-conveyor-1.jpg"
img_base64 = get_base64_of_image(image_path)

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
                          url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo ---
logo_base64 = get_base64_of_image("it-logo.png")
st.markdown(
    f"""
    <style>
    .top-right-logo {{
        position: fixed;
        top: 15px;
        right: 25px;
        width: 60px;
        z-index: 1000;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.);
    }}
    </style>
    <img src="data:image/png;base64,{logo_base64}" class="top-right-logo">
    """,
    unsafe_allow_html=True
)

# --- Fonts ---
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stFileUploader"] * {
        font-family: 'Roboto Condensed', sans-serif !important;
    }
    .center-title, .sidebar-title {
        font-family: 'Roboto Condensed', sans-serif !important;
    }
    code, pre {
        font-family: 'Courier New', monospace !important;
    }
    .css-1v3fvcr { font-family: 'Roboto Condensed', sans-serif !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #3a577b;
        min-width: 350px;
        max-width: 350px;
        padding: 20px;
    }
    .sidebar-title {
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 15px;
    }
    [data-testid="stFileUploader"] label {
        color: #ffffff !important;
        font-weight: bold;
        font-size: 18px;
        text-align: center;
        display: block;
    }
    [data-testid="stFileUploader"] section div {
        background-color: #ffffff;
        border: 2px dashed #b3d1ff;
        border-radius: 10px;
        padding: 15px;
    }
    [data-testid="stFileUploader"] section:hover div {
        border-color: #003366;
        background-color: #d9e7ff;
    }
    header, footer { visibility: hidden; }
    .css-18e3th9 { padding-top: 0px !important; }
    .center-title {
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: 1.5px;
        margin-top: -50px;
        margin-bottom: 20px;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* หัวข้อของ expander */
    details > summary {
        background-color: #2e4260 !important;
        color: #ffffff !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        font-weight: 600;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        list-style: none;
    }

    /* เนื้อหาด้านใน expander */
    details > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Roboto Condensed', sans-serif !important;
        padding: 10px;
        border-radius: 5px;
    }

    /* ลบลูกศร default ของ summary */
    details > summary::-webkit-details-marker {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown('<div class="sidebar-title">Upload File</div>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Upload Video for Egg Defect Detection:", type=["mp4", "avi", "mov"])

with st.sidebar.expander("Guidelines"):
    st.markdown(
        """
        <div style="font-family: 'Roboto Condensed', sans-serif; color: #000000; font-weight: 400; line-height: 1.5;">
        1. Upload the video file<br>
        2. Click Start Processing Video to detect defective eggs<br>
        3. Click Stop Processing Video if you want to halt processing<br>
        4. View and download the processed video
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Center Title ---
st.markdown('<div class="center-title">EGG DEFECT DETECTION AND CLASSIFICATION</div>', unsafe_allow_html=True)

# --- Status Placeholder ---
status_placeholder = st.empty()

# --- Load Model ---
MODEL_PATH = "model/best.pt"
if "model" not in st.session_state:
    st.session_state.model = load_model(MODEL_PATH)
model = st.session_state.model

# --- Session Flags ---
if "processing_started" not in st.session_state:
    st.session_state.processing_started = False
if "stop_processing" not in st.session_state:
    st.session_state.stop_processing = False
if "process_done" not in st.session_state:
    st.session_state.process_done = False

# --- Video Processing ---
if uploaded_file is not None:
    input_folder = "temp_inputs"
    os.makedirs(input_folder, exist_ok=True)
    input_path = os.path.join(input_folder, uploaded_file.name)

    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    output_folder = tempfile.mkdtemp()
    # os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{uploaded_file.name}_detected.mp4")

    st.markdown(
    '<h3 style="color: #FFFFFF; font-family: Roboto Condensed; font-weight:bold;">Original Video</h3>',
    unsafe_allow_html=True)
    st.video(input_path)

    col_start, col_space, col_stop = st.columns([1, 3, 1])

    # --- Start Processing Button ---
    with col_start:
        if st.button("Start Processing Video"):
            st.session_state.processing_started = True
            st.session_state.stop_processing = False
            status_placeholder.warning("Processing has been started.")
            # ข้อความพื้นหลังเหลือง ตัวอักษรขาว
            status_placeholder.markdown(
                '<div style="background-color: #f1c40f; color: white; padding: 10px; border-radius: 5px;">Processing has been started.</div>',
                unsafe_allow_html=True
            )

    # --- Stop Processing Button ---
    with col_stop:
        if st.session_state.processing_started:
            if st.button("Stop Processing Video", on_click=stop_process):
                st.session_state.stop_processing = True
                status_placeholder.warning("Processing has been stopped.")
                # ข้อความพื้นหลังเหลือง ตัวอักษรขาว
                status_placeholder.markdown(
                    '<div style="background-color: #f1c40f; color: white; padding: 10px; border-radius: 5px;">Processing has been stopped.</div>',
                    unsafe_allow_html=True
                )

    # --- Run Full Pipeline ---
    if st.session_state.processing_started and not st.session_state.stop_processing:
        with st.spinner("Detecting Defective Eggs..."):
            full_pipeline(input_path, output_path, model)
            st.session_state.output_path = output_path
            st.session_state.last_video = uploaded_file.name
            st.session_state.process_done = True
            st.session_state.processing_started = False
            # ข้อความพื้นหลังเขียว ตัวอักษรขาว
            status_placeholder.markdown(
                '<div style="background-color: #28a745; color: white; padding: 10px; border-radius: 5px;">Processing Complete</div>',
                unsafe_allow_html=True
            )

    # --- Show Result Video ---
    if st.session_state.get("process_done", False):
        st.markdown(
            '<h3 style="color: #FFFFFF; font-family: Roboto Condensed; font-weight:bold;">Result Video</h3>',
            unsafe_allow_html=True
        )
        with open(st.session_state.output_path, "rb") as f:
            video_bytes = f.read()
        st.video(video_bytes)

        with open(st.session_state.output_path, "rb") as f:
            st.download_button(
                label="Download Processed Video",
                data=f,
                file_name="output_detected.mp4",
                mime="video/mp4"
            )




