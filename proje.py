import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Finans Dashboard", layout="wide")

# Veritabanı
def init_db():
    conn = sqlite3.connect("butce_verisi.db")
    conn.execute("CREATE TABLE IF NOT EXISTS islemler (id INTEGER PRIMARY KEY, tip TEXT, aciklama TEXT, miktar REAL, kategori TEXT, tarih TEXT)")
    conn.commit()
    return conn

conn = init_db()

st.title("💰 Kişisel Bütçe Takip Sistemi")

# Verileri Çek
df = pd.read_sql_query("SELECT * FROM islemler ORDER BY id DESC", conn)
gelir_toplam = df[df['tip'] == 'GELİR']['miktar'].sum()
gider_toplam = df[df['tip'] == 'GİDER']['miktar'].sum()
bakiye = gelir_toplam - gider_toplam

# --- ÜST ÖZET PANELİ ---
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Bakiye", f"{bakiye:,.2f} TL")
col2.metric("Toplam Gider", f"{gider_toplam:,.2f} TL", delta_color="inverse")

# En Çok Harcanan Kategoriyi Bul
if not df[df['tip'] == 'GİDER'].empty:
    en_cok_kat = df[df['tip'] == 'GİDER'].groupby('kategori')['miktar'].sum().idxmax()
    en_cok_tutar = df[df['tip'] == 'GİDER'].groupby('kategori')['miktar'].sum().max()
    col3.metric("En Çok Harcanan", en_cok_kat, f"{en_cok_tutar:,.2f} TL")
else:
    col3.metric("En Çok Harcanan", "Veri Yok")

st.divider()

# --- İŞLEM EKLEME ---
with st.expander("➕ Yeni İşlem Ekle", expanded=True):
    with st.form("ekle_form"):
        c_tip, c_kat, c_tutar = st.columns(3)
        tip = c_tip.selectbox("İşlem Tipi", ["GELİR", "GİDER"])
        kat = c_kat.selectbox("Kategori", ["Maaş", "Yemek", "Ulaşım", "Eğlence", "Fatura", "Kira", "Diğer"])
        tutar = c_tutar.number_input("Miktar (TL)", min_value=0.0)
        aciklama = st.text_input("Açıklama")
        
        if st.form_submit_button("Sisteme Kaydet"):
            if tutar > 0:
                conn.execute("INSERT INTO islemler (tip, aciklama, miktar, kategori, tarih) VALUES (?,?,?,?,?)",
                             (tip, aciklama, tutar, kat, datetime.now().strftime("%Y-%m-%d %H:%M")))
                conn.commit()
                st.success("Kaydedildi!")
                st.rerun()

# --- TABLO ---
st.subheader("📜 İşlem Geçmişi")
st.dataframe(df[['tarih', 'tip', 'kategori', 'aciklama', 'miktar']], use_container_width=True, hide_index=True)

# Veri Sıfırlama (Kenar Çubuğunda)
if st.sidebar.button("🗑️ Tüm Verileri Temizle"):
    conn.execute("DELETE FROM islemler")
    conn.commit()
    st.rerun()
