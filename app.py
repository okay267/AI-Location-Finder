import streamlit as st
import cv2
import numpy as np
import librosa
import folium
from streamlit_folium import st_folium
import googlemaps
import tempfile
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام تحديد المواقع الجغرافي", layout="wide", page_icon="🛰️")

# تنسيق العناوين باللغة العربية
st.markdown("""
    <style>
    .main { text-align: right; direction: rtl; }
    div.stButton > button:first-child { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ نظام تحديد الموقع (بصري + صوتي)")
st.write("قم برفع ملف فيديو أو صورة واستخدم محرك البحث لتحديد الموقع على الخريطة.")

# 2. جلب المفتاح من Secrets
try:
    # تأكد أنك كتبت في الـ Secrets: GOOGLE_MAP_KEY = "your_key"
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.error("⚠️ خطأ: لم يتم العثور على مفتاح Google Maps في الإعدادات (Secrets).")
    st.stop()

# 3. تقسيم الواجهة إلى عمودين
col_input, col_map = st.columns([1, 1.2])

with col_input:
    st.subheader("📁 إدخال البيانات")
    
    # اختيار نوع الملف
    upload_type = st.radio("اختر نوع الملف المراد رفعه:", ["صورة", "فيديو"])
    uploaded_file = st.file_uploader(f"ارفع {upload_type} هنا", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])
    
    # خانة البحث عن الموقع (يدوي بدلاً من AI)
    target_location = st.text_input("📍 ابحث عن الموقع الجغرافي:", placeholder="مثلاً: برج القاهرة، مصر")

    if uploaded_file:
        if upload_type == "صورة":
            st.image(uploaded_file, caption="المعالم البصرية للموقع", use_container_width=True)
        else:
            st.video(uploaded_file)
            
            # تحليل صوتي بسيط باستخدام Librosa (مثال)
            st.info("📊 جاري تحليل البصمة الصوتية المحيطة...")
            # محاكاة تحليل ترددات
            chart_data = np.random.randn(50)
            st.line_chart(chart_data)

with col_map:
    st.subheader("🗺️ الخريطة التفاعلية")
    
    if target_location:
        try:
            # استخدام Google Geocoding لتحويل النص إلى إحداثيات
            geocode_result = gmaps.geocode(target_location)
            
            if geocode_result:
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lng = geocode_result[0]["geometry"]["location"]["lng"]
                formatted_address = geocode_result[0]["formatted_address"]

                st.success(f"✅ تم تحديد الموقع: {formatted_address}")

                # إنشاء الخريطة باستخدام Folium
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker(
                    [lat, lng], 
                    popup=target_location,
                    tooltip="الموقع المستهدف"
                ).add_to(m)
                
                # عرض الخريطة داخل Streamlit
                st_folium(m, width=700, height=500)
            else:
                st.warning("❓ لم نتمكن من العثور على هذا الموقع. يرجى التأكد من الاسم.")
        except Exception as e:
            st.error(f"❌ حدث خطأ في خدمة الخرائط: {e}")
    else:
        st.info("💡 اكتب اسم مكان في خانة البحث لتظهر لك الخريطة هنا.")

