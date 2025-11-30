import streamlit as st
import google.generativeai as genai
from pytubefix import YouTube # <-- ARTIK BUNU KULLANIYORUZ
import re

# --- AYARLAR ---
my_api_key = st.secrets["API_KEY"]

genai.configure(api_key=my_api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- YARDIMCI FONKSİYON: SRT TEMİZLEME ---
# Pytube altyazıları saatli (SRT) formatında verir, bunu düz yazıya çevirelim.
def clean_srt(srt_text):
    lines = srt_text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Zaman kodlarını ve sayıları at, sadece metni al
        if '-->' not in line and not line.strip().isdigit() and line.strip() != '':
            cleaned_lines.append(line.strip())
    return " ".join(cleaned_lines)

# --- SAYFA TASARIMI ---
st.set_page_config(page_title="YouTube Özetleyici v2", page_icon="🔥")
st.title("🔥 YouTube Asistanı")
st.write("Video izlemeye zamanınız mı yok? Sizin için özetleyelim!")

video_link = st.text_input("YouTube Video Linki:")

if st.button("🚀 Analiz Et"):
    if not video_link:
        st.warning("Link girmeyi unuttun.")
    else:
        try:
            with st.spinner('Video bilgileri alınıyor...'):
                # 1. Pytubefix ile videoya bağlan
                yt = YouTube(video_link)
                
                # 2. Altyazıları bulmaya çalış (Önce Türkçe, yoksa İngilizce)
                # 'a.tr' -> Otomatik Türkçe, 'tr' -> Manuel Türkçe
                caption = None
                
                # Mevcut dilleri kontrol et
                mevcut_diller = yt.captions
                
                # Öncelik sırası: Manuel Türkçe > Otomatik Türkçe > Manuel İngilizce > Otomatik İngilizce
                if 'tr' in mevcut_diller: caption = mevcut_diller['tr']
                elif 'a.tr' in mevcut_diller: caption = mevcut_diller['a.tr']
                elif 'en' in mevcut_diller: caption = mevcut_diller['en']
                elif 'a.en' in mevcut_diller: caption = mevcut_diller['a.en']
                
                if caption:
                    # 3. Altyazıyı indir ve temizle
                    srt_format = caption.generate_srt_captions()
                    full_text = clean_srt(srt_format)
                    
                    # 4. Gemini'ye Gönder
                    with st.spinner('Yapay zeka düşünüyor...'):
                        prompt = f"""
                        Bu videoyu benim için analiz et.
                        Ana fikri ve 3 önemli maddeyi Türkçe olarak yaz.
                        
                        Metin: {full_text[:8000]}
                        """
                        response = model.generate_content(prompt)
                        
                    st.success("Başarılı!")
                    st.write(response.text)
                else:
                    st.error("Bu videoda uygun bir altyazı bulunamadı (TR veya EN).")
                    st.info("Mevcut Altyazılar: " + str(mevcut_diller))
                    
        except Exception as e:

            st.error(f"Bir hata oluştu: {e}")



