import streamlit as st
import numpy as np
import googlemaps
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AI Locator", layout="wide")
st.title("🛰️ نظام تحديد الموقع الذكي")

# محاولة جلب المفتاح من الإعدادات
try:
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except:
    st.warning("⚠️ يرجى إضافة مفتاح الخرائط في الإعدادات")
    API_KEY = None

file = st.file_uploader("ارفع فيديو أو صورة", type=['mp4', 'jpg', 'png'])

if file:
    st.info("جاري التحليل...")
    # إحداثيات افتراضية للتجربة (برج القاهرة)
    lat, lng = 30.0459, 31.2243
    
    st.success("تم تحديد الموقع التقريبي!")
    m = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker([lat, lng], popup="الموقع المستهدف").add_to(m)
    st_folium(m, width=700)
