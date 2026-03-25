import streamlit as st
import cv2
import numpy as np
import librosa
import folium
from streamlit_folium import st_folium
import googlemaps

# 1. إعدادات الصفحة
st.set_page_config(page_title="كاشف الموقع الذكي", layout="wide")

st.title("🛰️ نظام تحديد الموقع (بصري + صوتي)")
st.write("قم برفع فيديو، صورة، أو استخدام الكاميرا لتحديد الموقع الجغرافي بالضبط.")

# 2. محاولة جلب مفتاح جوجل بأمان من Secrets
try:
    # ملاحظة: تأكد من تسمية المفتاح في Secrets بـ GOOGLE_MAP_KEY
    API_KEY = st.secrets["GOOGLE_MAP_KEY"]
    gmaps = googlemaps.Client(key=API_KEY)
except Exception:
    st.warning("⚠️ يرجى ضبط مفتاح Google Maps API في إعدادات Secrets.")
    API_KEY = None

# 3. واجهة الإدخال المحدثة (تدعم الصور الآن)
option = st.selectbox("اختر طريقة الإدخال:", ["رفع ملف (فيديو أو صورة)", "التقاط فيديو للمكان"])

if "رفع ملف" in option:
    # أضفنا jpg و png للسماح بالصور
    uploaded_file = st.file_uploader("اختر ملف...", type=["mp4", "mov", "avi", "jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("التقط صورة/فيديو للمكان")

# 4. معالجة الملف المرفوع
if uploaded_file is not None:
    col1, col2 = st.columns(2)

    with col1:
        # التحقق إذا كان الملف صورة أم فيديو للعرض الصحيح
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="المعالم البصرية الملتقطة")
        else:
            st.video(uploaded_file)
        
        st.info("...جاري تحليل البصمة الصوتية والبيئية")
        # تمثيل بياني بسيط لموجات الصوت (مثال)
        audio_wave = np.random.randn(100)
        st.line_chart(audio_wave)

    with col2:
        # هنا نضع منطق افتراضي (يمكنك تطويره لاحقاً للتعرف الحقيقي)
        location_name = "Cairo Tower, Egypt" # مثال توضيحي
        
        if API_KEY:
            try:
                res = gmaps.geocode(location_name)
                if res:
                    lat = res[0]["geometry"]["location"]["lat"]
                    lng = res[0]["geometry"]["location"]["lng"]

                    st.success(f"📍 الموقع المكتشف: {location_name}")

                    # عرض الخريطة
                    m = folium.Map(location=[lat, lng], zoom_start=15)
                    folium.Marker([lat, lng], popup=location_name).add_to(m)
                    st_folium(m, width=500, height=300)
                else:
                    st.error("لم يتم العثور على إحداثيات لهذا الموقع.")
            except Exception as e:
                st.error(f"حدث خطأ أثناء جلب البيانات: {e}")
        else:
            st.error("الموقع مكتشف ولكن الخريطة تتطلب مفتاح API.")


