import streamlit as st
import cv2
import numpy as np
import librosa
import folium
from streamlit_folium import st_folium
import googlemaps

st.set_page_config(page_title="نظام تحديد الموقع", layout="wide")
st.title("🛰️ نظام تحديد الموقع (بصري + صوتي)")

# جلب المفتاح بشكل صحيح من Secrets
try:
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ يرجى ضبط المفتاح في Secrets كما هو موضح في الخطوة 2")
    st.stop()

# واجهة رفع الملفات
upload_type = st.radio("اختر نوع الملف:", ["صورة", "فيديو"])
uploaded_file = st.file_uploader(f"ارفع {upload_type}", type=["jpg", "png", "mp4", "mov"])
location_name = st.text_input("📍 ابحث عن اسم المكان:", "Cairo Tower, Egypt")

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        if upload_type == "صورة":
            st.image(uploaded_file, caption="المعالجة البصرية")
        else:
            st.video(uploaded_file)
            st.line_chart(np.random.randn(100)) # تمثيل صوتي

    with col2:
        if location_name:
            res = gmaps.geocode(location_name)
            if res:
                lat, lng = res[0]["geometry"]["location"].values()
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], popup=location_name).add_to(m)
                st_folium(m, width="100%", height=400)
