import streamlit as st
import googlemaps
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from PIL import Image

# 1. إعدادات الصفحة والذكاء الاصطناعي
st.set_page_config(page_title="كاشف الموقع الذكي", layout="wide")

try:
    MAP_KEY = st.secrets["GOOGLE_MAP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    gmaps = googlemaps.Client(key=MAP_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ تأكد من ضبط GEMINI_API_KEY و GOOGLE_MAP_KEY في الـ Secrets")
    st.stop()

st.title("🛰️ نظام تحديد الموقع بالذكاء الاصطناعي")

uploaded_file = st.file_uploader("ارفع صورة للمكان المطلوب تحليله", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(img, caption="الصورة المرفوعة")
        
    with col2:
        with st.spinner("🔍 جاري تحليل المعالم البصرية..."):
            # سؤال Gemini عن الموقع بناءً على الصورة
            prompt = "Identify the location in this image. Return ONLY the name of the place and city/country. If unknown, say 'Unknown'."
            response = model.generate_content([prompt, img])
            location_name = response.text.strip()
            
        if location_name != "Unknown":
            st.success(f"📍 الموقع المكتشف: {location_name}")
            
            # تحويل الاسم إلى إحداثيات وعرض الخريطة
            geocode_result = gmaps.geocode(location_name)
            if geocode_result:
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lng = geocode_result[0]["geometry"]["location"]["lng"]
                
                m = folium.Map(location=[lat, lng], zoom_start=15)
                folium.Marker([lat, lng], popup=location_name).add_to(m)
                st_folium(m, width=500, height=300)
        else:
            st.warning("لم يستطع الذكاء الاصطناعي تحديد هذا الموقع بدقة.")
