import streamlit as st
import googlemaps
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from PIL import Image
import cv2
import tempfile
import os
import io

st.set_page_config(page_title="كاشف الموقع الذكي", layout="wide")

# جلب المفاتيح
try:
    MAP_KEY = st.secrets["GOOGLE_MAP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    gmaps = googlemaps.Client(key=MAP_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ تأكد من ضبط المفاتيح في Secrets")
    st.stop()

st.title("🛰️ نظام تحديد الموقع (صورة + فيديو)")

upload_type = st.radio("اختر نوع الملف:", ["صورة", "فيديو"])
uploaded_file = st.file_uploader(f"ارفع {upload_type}", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file:
    col1, col2 = st.columns(2)
    img_byte_arr = None

    with col1:
        if upload_type == "صورة":
            img = Image.open(uploaded_file)
            st.image(img, caption="الصورة المرفوعة")
            # تحويل الصورة لبايتات لضمان قبولها في Gemini
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            img_byte_arr = buf.getvalue()
        else:
            st.video(uploaded_file)
            with st.spinner("🎞️ جاري معالجة الفيديو..."):
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                cap = cv2.VideoCapture(tfile.name)
                success, frame = cap.read()
                if success:
                    _, buffer = cv2.imencode('.jpg', frame)
                    img_byte_arr = buffer.tobytes()
                    st.image(img_byte_arr, caption="اللقطة المأخوذة للتحليل")
                cap.release()
                os.unlink(tfile.name)

    with col2:
        if img_byte_arr:
            with st.spinner("🔍 جاري التحليل..."):
                try:
                    # إرسال الصورة كبايتات (هذا يحل مشكلة InvalidArgument)
                    contents = [
                        "What is the name and city of this landmark? Answer ONLY with 'Name, City'.",
                        {'mime_type': 'image/jpeg', 'data': img_byte_arr}
                    ]
                    response = model.generate_content(contents)
                    location_name = response.text.strip()
                    
                    if "Unknown" not in location_name:
                        st.success(f"📍 الموقع: {location_name}")
                        res = gmaps.geocode(location_name)
                        if res:
                            lat, lng = res[0]["geometry"]["location"].values()
                            m = folium.Map(location=[lat, lng], zoom_start=15)
                            folium.Marker([lat, lng], popup=location_name).add_to(m)
                            st_folium(m, width=500, height=300)
                except Exception as e:
                    st.error(f"خطأ تقني: {e}")
