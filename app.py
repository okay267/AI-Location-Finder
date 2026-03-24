import streamlit as st
import google.generativeai as genai
import PIL.Image
import folium
from streamlit_folium import st_folium

# إعداد واجهة التطبيق
st.set_page_config(page_title="AI Finder Pro", layout="centered")
st.title("🛰️ نظام تحديد الموقع الذكي")

# جلب مفتاح الأمان من الإعدادات
try:
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.warning("⚠️ يرجى إضافة مفتاح الخرائط في الإعدادات")
    st.stop()

# رفع الملف
file = st.file_uploader("📸 ارفع صورة للمكان لتحليلها", type=['jpg', 'jpeg', 'png'])

if file:
    img = PIL.Image.open(file)
    st.image(img, caption="الصورة المرفوعة", use_container_width=True)
    
    if st.button("🚀 ابدأ التحليل بالذكاء الاصطناعي"):
        with st.spinner("⏳ جارٍ تحليل معالم الصورة وتحديد الإحداثيات..."):
            try:
                # محرك الذكاء الاصطناعي
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = "Give me ONLY the GPS coordinates (latitude and longitude) of the location in this image. Response format: lat, lon"
                response = model.generate_content([prompt, img])
                
                # استخراج الإحداثيات
                coords = response.text.strip().split(',')
                lat = float(coords[0])
                lon = float(coords[1])
                
                st.success(f"📍 تم تحديد الموقع: {lat}, {lon}")
                
                # عرض الخريطة
                m = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker([lat, lon], popup="الموقع المكتشف").add_to(m)
                st_folium(m, width=700)
                
            except:
                st.error("❌ عذراً، لم يستطع الذكاء الاصطناعي تحديد إحداثيات دقيقة لهذه الصورة.")
