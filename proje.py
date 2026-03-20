import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Bütçe Kontrol Paneli", layout="wide")

# Veritabanı Kurulumu
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

# Özet Kartları
c1, c2 = st.columns(2)
c1.metric("Toplam Gelir", f"{gelir_toplam:.2f} TL")
c2.metric("Toplam Gider", f"{gider_toplam:.2f} TL")

st.divider()

# Ekleme Formu
with st.form("ekle"):
    tip = st.selectbox("Tip", ["GELİR", "GİDER"])
    aciklama = st.text_input("Açıklama")
    miktar = st.number_input("Miktar", min_value=0.0)
    if st.form_submit_button("Kaydet"):
        conn.execute("INSERT INTO islemler (tip, aciklama, miktar, tarih) VALUES (?,?,?,?)",
                     (tip, aciklama, miktar, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        st.rerun()

st.subheader("📜 Son İşlemler")
st.dataframe(df, use_container_width=True)
