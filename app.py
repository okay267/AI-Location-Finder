import streamlit as st
import googlemaps
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from PIL import Image
import cv2
import tempfile
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="نظام تحديد الموقع الذكي", layout="wide")

# محاولة جلب المفاتيح من Secrets
try:
    MAP_KEY = st.secrets["GOOGLE_MAP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    gmaps = googlemaps.Client(key=MAP_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ خطأ في الإعدادات: تأكد من ضبط المفاتيح بشكل صحيح في Secrets.")
    st.stop()

st.title("🛰️ نظام تحديد الموقع بالذكاء الاصطناعي (بصري + فيديو)")

# 2. خيارات الإدخال
upload_type = st.radio("اختر نوع الملف:", ["صورة", "فيديو"])
uploaded_file = st.file_uploader(f"ارفع {upload_type} للمكان المطلوب تحليله", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file:
    col1, col2 = st.columns(2)
    location_name = "Unknown"

    with col1:
        if upload_type == "صورة":
            img = Image.open(uploaded_file)
            st.image(img, caption="الصورة المرفوعة")
            
            with st.spinner("🔍 جاري تحليل الصورة..."):
                prompt = "Identify this location. Return only the name and city. If unknown, say Unknown."
                response = model.generate_content([prompt, img])
                location_name = response.text.strip()
        
        else:  # معالجة الفيديو
            st.video(uploaded_file)
            with st.spinner("🎞️ جاري استخراج لقطة من الفيديو وتحليلها..."):
                # حفظ الفيديو مؤقتاً لاستخراج إطار (Frame) منه
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                vf = cv2.VideoCapture(tfile.name)
                success, frame = vf.read() # قراءة أول إطار
                if success:
                    cv2.imwrite("frame.jpg", frame)
                    img = Image.open("frame.jpg")
                    prompt = "Identify the location in this video frame. Return only name and city."
                    response = model.generate_content([prompt, img])
                    location_name = response.text.strip()
                vf.release()
                os.unlink(tfile.name)

    with col2:
        if location_name != "Unknown" and len(location_name) > 2:
            st.success(f"📍 الموقع المكتشف: {location_name}")
            
            try:
                # تحويل الاسم لإحداثيات
                geocode_result = gmaps.geocode(location_name)
                if geocode_result:
                    lat = geocode_result[0]["geometry"]["location"]["lat"]
                    lng = geocode_result[0]["geometry"]["location"]["lng"]
                    
                    m = folium.Map(location=[lat, lng], zoom_start=15)
                    folium.Marker([lat, lng], popup=location_name).add_to(m)
                    st_folium(m, width=500, height=300)
                else:
                    st.warning("الموقع مكتشف كاسم ولكن تعذر إيجاد إحداثياته على الخريطة.")
            except Exception as e:
                st.error(f"خطأ في Google Maps API: {e}")
        else:
            st.warning("لم يتمكن الذكاء الاصطناعي من تحديد الموقع. حاول رفع صورة أوضح لمعلم معروف.")

