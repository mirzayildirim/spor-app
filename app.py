import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- VERİTABANI (JSON) AYARLARI ---
DATA_FILE = "antrenman_verileri.json"

def veriyi_yukle():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def veriyi_kaydet(veri):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=4, ensure_ascii=False)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Antrenman Takibi", page_icon="🏋️‍♂️", layout="centered")

# --- KATALOG (Kendi makine görsellerini buraya ekleyebilirsin) ---
katalog = {
    "Shoulder Press": "https://dummyimage.com/300x200/5e35b1/fff&text=Shoulder+Press",
    "Bench Press": "https://dummyimage.com/300x200/1e88e5/fff&text=Bench+Press",
    "Squat": "https://dummyimage.com/300x200/d32f2f/fff&text=Squat",
    "Lat Pulldown": "https://dummyimage.com/300x200/2e7d32/fff&text=Lat+Pulldown"
}

# --- SEKMELER ---
tab1, tab2 = st.tabs(["📝 Antrenman Ekle", "📈 Geçmiş ve Analiz"])

# --- 1. SEKME: ANTRENMAN EKLE ---
with tab1:
    st.header("Bugünkü Antrenman")
    secilen_tarih = st.date_input("Tarih", datetime.today())
    secilen_hareket = st.selectbox("Hareket Seçin", list(katalog.keys()))
    
    # Seçilen hareketin görselini göster
    st.image(katalog[secilen_hareket], use_column_width=True)
    
    st.divider()
    st.subheader("Setler")
    
    # Set ekleme butonu için oturum (session) yönetimi
    if "set_sayisi" not in st.session_state:
        st.session_state.set_sayisi = 1

    def set_ekle():
        st.session_state.set_sayisi += 1

    # Set kutucuklarını dinamik olarak oluştur
    girilen_setler = []
    for i in range(st.session_state.set_sayisi):
        col1, col2 = st.columns(2)
        with col1:
            tekrar = st.number_input(f"{i+1}. Set - Tekrar", min_value=1, step=1, key=f"tekrar_{i}")
        with col2:
            agirlik = st.number_input(f"{i+1}. Set - Ağırlık (kg)", min_value=0.0, step=2.5, key=f"agirlik_{i}")
        girilen_setler.append({"set": i+1, "tekrar": tekrar, "agirlik": agirlik})

    st.button("➕ Set Ekle", on_click=set_ekle)
    
    st.divider()
    
    # Kaydetme İşlemi
    if st.button("💾 Antrenmanı Kaydet", type="primary"):
        yeni_kayit = {
            "tarih": str(secilen_tarih),
            "hareket": secilen_hareket,
            "setler": girilen_setler
        }
        mevcut_veri = veriyi_yukle()
        mevcut_veri.append(yeni_kayit)
        veriyi_kaydet(mevcut_veri)
        
        st.success(f"{secilen_hareket} başarıyla kaydedildi!")
        # İşlem bitince set sayısını sıfırla
        st.session_state.set_sayisi = 1

# --- 2. SEKME: GEÇMİŞ VE ANALİZ ---
with tab2:
    st.header("Veri Analizi (Mor Ok 🟣)")
    veri = veriyi_yukle()
    
    if len(veri) > 0:
        df = pd.json_normalize(veri)
        
        # Analiz edilecek hareketi seç
        analiz_hareket = st.selectbox("Analiz Etmek İstediğin Hareketi Seç", list(katalog.keys()), key="analiz")
        
        # Filtreleme
        hareket_verisi = [v for v in veri if v["hareket"] == analiz_hareket]
        
        if hareket_verisi:
            tarihler = []
            max_agirliklar = []
            
            # Her tarih için o hareketin maksimum ağırlığını bul
            for kayit in hareket_verisi:
                tarih = kayit["tarih"]
                setler_df = pd.DataFrame(kayit["setler"])
                if not setler_df.empty:
                    maksimum_agirlik = setler_df["agirlik"].max()
                    tarihler.append(tarih)
                    max_agirliklar.append(maksimum_agirlik)
            
            grafik_df = pd.DataFrame({
                "Tarih": pd.to_datetime(tarihler),
                "Maksimum Ağırlık (kg)": max_agirliklar
            }).sort_values("Tarih")
            
            st.subheader(f"📈 {analiz_hareket} Gelişimi")
            st.line_chart(grafik_df.set_index("Tarih"))
            
            st.divider()
            st.write("📋 **Geçmiş Kayıtlar**")
            for kayit in reversed(hareket_verisi):
                st.info(f"**Tarih:** {kayit['tarih']}")
                st.dataframe(pd.DataFrame(kayit["setler"]), use_container_width=True)
        else:
            st.warning("Bu hareket için henüz veri girilmemiş.")
    else:
        st.info("Henüz hiç antrenman kaydedilmedi.")

# --- TASARIM TEMİZLİĞİ (Logoları ve Menüleri Gizler) ---
gizleme_kodu = """
<style>
#MainMenu {visibility: hidden;} /* Sağ üstteki menüyü gizler */
footer {visibility: hidden;} /* En alttaki 'Made with Streamlit' yazısını gizler */
header {visibility: hidden;} /* Üstteki renkli şeridi ve GitHub logosunu gizler */
.block-container {padding-top: 1rem; padding-bottom: 0rem;} /* Üstteki devasa boşluğu kapatır */
</style>
"""
st.markdown(gizleme_kodu, unsafe_allow_html=True)
