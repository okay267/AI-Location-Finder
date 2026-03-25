import streamlit as st
import googlemaps
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from PIL import Image
import cv2
import tempfile
import os

# إعدادات الصفحة
st.set_page_config(page_title="كاشف الموقع الذكي", layout="wide")

# جلب المفاتيح
try:
    MAP_KEY = st.secrets["GOOGLE_MAP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    gmaps = googlemaps.Client(key=MAP_KEY)
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ يرجى التأكد من صحة المفاتيح في الـ Secrets")
    st.stop()

st.title("🛰️ نظام تحديد الموقع الذكي (صورة + فيديو)")

upload_type = st.radio("اختر نوع الملف:", ["صورة", "فيديو"])
uploaded_file = st.file_uploader(f"ارفع {upload_type} للمكان المطلوب", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file:
    col1, col2 = st.columns(2)
    img_to_analyze = None

    with col1:
        if upload_type == "صورة":
            img_to_analyze = Image.open(uploaded_file)
            st.image(img_to_analyze, caption="الصورة المرفوعة")
        else:
            st.video(uploaded_file)
            with st.spinner("🎞️ جاري معالجة الفيديو..."):
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                cap = cv2.VideoCapture(tfile.name)
                success, frame = cap.read()
                if success:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_to_analyze = Image.fromarray(frame_rgb)
                    st.image(img_to_analyze, caption="لقطة من الفيديو")
                cap.release()
                os.unlink(tfile.name)

    with col2:
        if img_to_analyze:
            with st.spinner("🔍 جاري التحليل..."):
                try:
                    # الطريقة الأكثر أماناً لإرسال المحتوى لـ Gemini
                    prompt = "What is the name and city of this landmark? Answer only with name and city."
                    # إرسال الصورة كقائمة لضمان عدم حدوث InvalidArgument
                    response = model.generate_content([prompt, img_to_analyze])
                    location_name = response.text.strip()
                    
                    if "Unknown" not in location_name and len(location_name) > 3:
                        st.success(f"📍 الموقع المكتشف: {location_name}")
                        
                        # الخريطة
                        res = gmaps.geocode(location_name)
                        if res:
                            lat, lng = res[0]["geometry"]["location"].values()
                            m = folium.Map(location=[lat, lng], zoom_start=15)
                            folium.Marker([lat, lng], popup=location_name).add_to(m)
                            st_folium(m, width=500, height=300)
                    else:
                        st.warning("تعذر تحديد المعلم بدقة.")
                except Exception as e:
                    st.error(f"خطأ تقني: {e}")

                
