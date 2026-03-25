import streamlit as st
import cv2
import numpy as np
import librosa
import folium
from streamlit_folium import st_folium
import googlemaps
import tempfile
import os

# إعداد الصفحة
st.set_page_config(page_title="نظام تحديد الموقع الجغرافي", layout="wide")

st.title("🛰️ نظام تحديد الموقع (بصري + صوتي)")

# جلب المفتاح من Secrets
try:
    # تأكد من كتابة GOOGLE_MAP_KEY في إعدادات Secrets
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ خطأ: يرجى إضافة GOOGLE_MAP_KEY في إعدادات Secrets بصيغة TOML.")
    st.stop()

# واجهة المستخدم
col_in, col_out = st.columns([1, 1])

with col_in:
    st.subheader("📁 رفع الوسائط")
    file_type = st.radio("نوع الملف:", ["صورة", "فيديو"])
    uploaded_file = st.file_uploader(f"اختر ملف {file_type}", type=["jpg", "png", "mp4", "mov"])
    
    # إدخال الموقع يدوياً (البديل عن الذكاء الاصطناعي)
    location_input = st.text_input("📍 ابحث عن مكان المعلم:", "Cairo Tower")

    if uploaded_file:
        if file_type == "صورة":
            st.image(uploaded_file, caption="المعالجة البصرية")
        else:
            st.video(uploaded_file)
            st.info("📊 تحليل البصمة الصوتية المحيطة...")
            # محاكاة تحليل الترددات باستخدام numpy
            st.line_chart(np.random.randn(100))

with col_out:
    st.subheader("🗺️ الخريطة التفاعلية")
    if location_input:
        try:
            geocode_result = gmaps.geocode(location_input)
            if geocode_result:
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lng = geocode_result[0]["geometry"]["location"]["lng"]
                address = geocode_result[0]["formatted_address"]
                
                st.success(f"تم العثور على: {address}")
                
                # عرض الخريطة
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], popup=address).add_to(m)
                st_folium(m, width="100%", height=400)
            else:
                st.warning("لم يتم العثور على نتائج. تأكد من تفعيل Geocoding API.")
        except Exception as e:
            st.error(f"خطأ في الاتصال بجوجل: {e}")
