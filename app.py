import streamlit as st
import googlemaps
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from PIL import Image
import cv2
import tempfile
import os

# 1. إعدادات الصفحة والذكاء الاصطناعي
st.set_page_config(page_title="كاشف الموقع الذكي", layout="wide")

try:
    MAP_KEY = st.secrets["GOOGLE_MAP_KEY"]
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    
    gmaps = googlemaps.Client(key=MAP_KEY)
    genai.configure(api_key=GEMINI_KEY)
    # نستخدم فلاش 1.5 لأنه الأسرع والأفضل في تحليل الوسائط
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ تأكد من ضبط المفاتيح في Secrets (GOOGLE_MAP_KEY و GEMINI_API_KEY)")
    st.stop()

st.title("🛰️ نظام تحديد الموقع (صورة + فيديو)")

# 2. واجهة الإدخال
upload_type = st.radio("اختر نوع الملف المراد تحليله:", ["صورة", "فيديو"])
uploaded_file = st.file_uploader(f"ارفع {upload_type} للمكان المطلوب", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file:
    col1, col2 = st.columns(2)
    location_name = "Unknown"
    img_to_analyze = None

    with col1:
        if upload_type == "صورة":
            img_to_analyze = Image.open(uploaded_file)
            st.image(img_to_analyze, caption="الصورة المرفوعة")
        else:
            st.video(uploaded_file)
            # استخراج إطار من الفيديو للتحليل
            with st.spinner("🎞️ جاري معالجة الفيديو..."):
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                cap = cv2.VideoCapture(tfile.name)
                success, frame = cap.read()
                if success:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_to_analyze = Image.fromarray(frame_rgb)
                    st.image(img_to_analyze, caption="اللقطة التي تم تحليلها من الفيديو")
                cap.release()
                os.unlink(tfile.name)

    with col2:
        if img_to_analyze:
            with st.spinner("🔍 جاري التعرف على الموقع عبر الذكاء الاصطناعي..."):
                try:
                    prompt = "Identify the specific location or landmark in this image. Give me the name and city/country only. If you can't identify it, say 'Unknown'."
                    response = model.generate_content([prompt, img_to_analyze])
                    location_name = response.text.strip()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء تحليل الذكاء الاصطناعي: {e}")
            
            if location_name != "Unknown" and len(location_name) > 2:
                st.success(f"📍 الموقع المقترح: {location_name}")
                
                # جلب الإحداثيات من جوجل
                try:
                    geocode_result = gmaps.geocode(location_name)
                    if geocode_result:
                        lat = geocode_result[0]["geometry"]["location"]["lat"]
                        lng = geocode_result[0]["geometry"]["location"]["lng"]
                        
                        m = folium.Map(location=[lat, lng], zoom_start=15)
                        folium.Marker([lat, lng], popup=location_name).add_to(m)
                        st_folium(m, width=500, height=300)
                    else:
                        st.warning("تعذر العثور على إحداثيات دقيقة لهذا الموقع.")
                except Exception as e:
                    st.error(f"خطأ في الوصول لخريطة جوجل: {e}")
            else:
                st.info("الذكاء الاصطناعي لم يتعرف على معلم مشهور في هذه الصورة.")
