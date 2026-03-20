import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# --- VERİTABANI AYARLARI ---
def tablo_olustur():
    with sqlite3.connect("final_butce_sistemi.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ayarlar (anahtar TEXT PRIMARY KEY, deger REAL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS gelirler (id INTEGER PRIMARY KEY, aciklama TEXT, miktar REAL, tarih TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS giderler (id INTEGER PRIMARY KEY, aciklama TEXT, miktar REAL, kategori TEXT, tarih TEXT)")
        cursor.execute("INSERT OR IGNORE INTO ayarlar VALUES ('limit', 2000.0)")
        conn.commit()

class PremiumButceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyFinance Dashboard v4.0")
        self.root.geometry("550x850")
        self.root.configure(bg="#F8F9FD")
        
        tablo_olustur()
        self.arayuz_hazirla()
        self.verileri_yukle()

    def arayuz_hazirla(self):
        # --- ÜST BAŞLIK ---
        header = tk.Frame(self.root, bg="#F8F9FD")
        header.pack(fill="x", padx=30, pady=(30, 10))
        tk.Label(header, text="Hoş Geldin,", fg="#ADB5BD", bg="#F8F9FD", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(header, text="Hesap Hareketleri", fg="#212529", bg="#F8F9FD", font=("Segoe UI", 18, "bold")).pack(anchor="w")

        # --- BAKİYE VE LİMİT KARTI ---
        self.card = tk.Frame(self.root, bg="#4E73DF", padx=20, pady=25, highlightthickness=0)
        self.card.pack(fill="x", padx=30, pady=10)
        
        tk.Label(self.card, text="GÜNCEL BAKİYE", fg="#D1D3E2", bg="#4E73DF", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lbl_bakiye = tk.Label(self.card, text="0.00 TL", fg="white", bg="#4E73DF", font=("Segoe UI", 26, "bold"))
        self.lbl_bakiye.pack(anchor="w", pady=5)
        
        self.lbl_limit_info = tk.Label(self.card, text="Bütçe Hedefi: 0 TL", fg="#FFFFFF", bg="#4E73DF", font=("Segoe UI", 9))
        self.lbl_limit_info.pack(anchor="w")

        # --- EN ÇOK HARCANAN KATEGORİ ---
        self.analysis_frame = tk.Frame(self.root, bg="#FFFFFF", highlightthickness=1, highlightbackground="#EDF0F5")
        self.analysis_frame.pack(fill="x", padx=30, pady=10)
        tk.Label(self.analysis_frame, text="EN ÇOK HARCAMA:", fg="#5A5C69", bg="#FFFFFF", font=("Segoe UI", 8, "bold")).pack(side="left", padx=15, pady=15)
        self.lbl_en_cok = tk.Label(self.analysis_frame, text="---", fg="#4E73DF", bg="#FFFFFF", font=("Segoe UI", 10, "bold"))
        self.lbl_en_cok.pack(side="left")

        # --- BÜTÇE AYARLAMA ---
        set_frame = tk.Frame(self.root, bg="#F8F9FD")
        set_frame.pack(fill="x", padx=35, pady=5)
        self.ent_limit_set = tk.Entry(set_frame, font=("Segoe UI", 9), width=10, bd=0, highlightthickness=1, highlightbackground="#D1D3E2")
        self.ent_limit_set.pack(side="left", padx=5, ipady=3)
        tk.Button(set_frame, text="Limit Güncelle", bg="#4E73DF", fg="white", font=("Segoe UI", 8, "bold"), bd=0, padx=10, command=self.limit_guncelle).pack(side="left")
        self.lbl_butce_mesaj = tk.Label(set_frame, text="", bg="#F8F9FD", font=("Segoe UI", 9, "bold"))
        self.lbl_butce_mesaj.pack(side="right")

        # --- GİRİŞ ALANLARI ---
        input_main = tk.Frame(self.root, bg="#FFFFFF", padx=20, pady=20, highlightthickness=1, highlightbackground="#EDF0F5")
        input_main.pack(fill="x", padx=30, pady=10)
        tabs = ttk.Notebook(input_main)
        tabs.pack(fill="x")

        # GELİR TAB
        self.tab_gelir = tk.Frame(tabs, bg="white", pady=10)
        tabs.add(self.tab_gelir, text="  + GELİR  ")
        self.create_modern_input(self.tab_gelir, "Gelir Kaynağı:", "gelir_ad")
        self.create_modern_input(self.tab_gelir, "Miktar (TL):", "gelir_tutar")
        tk.Button(self.tab_gelir, text="Geliri Kaydet", bg="#1CC88A", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=self.gelir_kaydet).pack(fill="x", pady=10)

        # GİDER TAB
        self.tab_gider = tk.Frame(tabs, bg="white", pady=10)
        tabs.add(self.tab_gider, text="  - GİDER  ")
        self.create_modern_input(self.tab_gider, "Harcama:", "gider_ad")
        self.create_modern_input(self.tab_gider, "Tutar:", "gider_tutar")
        tk.Label(self.tab_gider, text="Kategori:", bg="white", font=("Segoe UI", 8)).pack(anchor="w")
        self.combo_kat = ttk.Combobox(self.tab_gider, values=["Yemek", "Ulaşım", "Eğlence", "Fatura", "Diger"], state="readonly")
        self.combo_kat.current(0)
        self.combo_kat.pack(fill="x", pady=5)
        tk.Button(self.tab_gider, text="Harcamayı Kaydet", bg="#E74A3B", fg="white", font=("Segoe UI", 10, "bold"), bd=0, pady=8, command=self.gider_kaydet).pack(fill="x", pady=10)

        # --- LOG LİSTESİ (TÜM İŞLEMLER) ---
        tk.Label(self.root, text="Son İşlemler (Gelir & Gider)", fg="#4E73DF", bg="#F8F9FD", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=35, pady=(10, 5))
        
        self.tree = ttk.Treeview(self.root, columns=("T", "A", "M", "K"), show="headings", height=10)
        self.tree.heading("T", text="Tip"); self.tree.heading("A", text="Açıklama"); self.tree.heading("M", text="Tutar"); self.tree.heading("K", text="Kat.")
        self.tree.column("T", width=50); self.tree.column("A", width=180); self.tree.column("M", width=100); self.tree.column("K", width=80)
        self.tree.pack(fill="both", padx=30, pady=5)
        
        # Renkli satırlar için tag'ler
        self.tree.tag_configure('gelir', foreground='#1CC88A')
        self.tree.tag_configure('gider', foreground='#E74A3B')

    def create_modern_input(self, parent, label_text, attr):
        tk.Label(parent, text=label_text, bg="white", fg="#5A5C69", font=("Segoe UI", 8)).pack(anchor="w")
        e = tk.Entry(parent, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#D1D3E2")
        e.pack(fill="x", pady=(2, 10), ipady=5)
        setattr(self, f"ent_{attr}", e)

    def limit_guncelle(self):
        try:
            val = float(self.ent_limit_set.get())
            with sqlite3.connect("final_butce_sistemi.db") as conn:
                conn.execute("UPDATE ayarlar SET deger = ? WHERE anahtar = 'limit'", (val,))
            self.verileri_yukle()
            messagebox.showinfo("Başarılı", "Limit güncellendi.")
        except: messagebox.showerror("Hata", "Geçersiz sayı.")

    def verileri_yukle(self):
        with sqlite3.connect("final_butce_sistemi.db") as conn:
            limit = conn.execute("SELECT deger FROM ayarlar WHERE anahtar = 'limit'").fetchone()[0]
            gelir_toplam = conn.execute("SELECT SUM(miktar) FROM gelirler").fetchone()[0] or 0
            gider_toplam = conn.execute("SELECT SUM(miktar) FROM giderler").fetchone()[0] or 0
            en_cok = conn.execute("SELECT kategori, SUM(miktar) FROM giderler GROUP BY kategori ORDER BY SUM(miktar) DESC LIMIT 1").fetchone()
            
            # GELİR VE GİDERLERİ BİRLEŞTİR VE TARİHE GÖRE SIRALA
            gelirler = conn.execute("SELECT 'GELİR', aciklama, miktar, 'Gelir', tarih FROM gelirler").fetchall()
            giderler = conn.execute("SELECT 'GİDER', aciklama, miktar, kategori, tarih FROM giderler").fetchall()
            tum_islemeler = sorted(gelirler + giderler, key=lambda x: x[4], reverse=True)

        # Kart ve Analiz Güncelleme
        self.lbl_bakiye.config(text=f"{(gelir_toplam - gider_toplam):,.2f} TL")
        self.lbl_limit_info.config(text=f"Hedef: {limit:,.2f} TL | Harcanan: {gider_toplam:,.2f} TL")
        self.lbl_en_cok.config(text=f"{en_cok[0].upper()} ({en_cok[1]:,.2f} TL)" if en_cok else "Veri Yok")
        
        # Bütçe Uyarı Rengi
        if limit > 0 and gider_toplam > limit:
            self.lbl_butce_mesaj.config(text="LİMİT AŞILDI!", fg="#E74A3B")
            self.card.config(bg="#E74A3B")
        else:
            self.lbl_butce_mesaj.config(text="Bütçe Normal", fg="#1CC88A")
            self.card.config(bg="#4E73DF")

        # Tabloyu Güncelle (Gelir/Gider Ayrımıyla)
        for r in self.tree.get_children(): self.tree.delete(r)
        for tip, aciklama, miktar, kat, tarih in tum_islemeler:
            isaret = "+" if tip == "GELİR" else "-"
            tag = 'gelir' if tip == "GELİR" else 'gider'
            self.tree.insert("", "end", values=(tip, aciklama, f"{isaret}{miktar:,.2f} TL", kat), tags=(tag,))

    def gelir_kaydet(self):
        try:
            m = float(self.ent_gelir_tutar.get())
            with sqlite3.connect("final_butce_sistemi.db") as conn:
                conn.execute("INSERT INTO gelirler (aciklama, miktar, tarih) VALUES (?, ?, ?)", 
                             (self.ent_gelir_ad.get(), m, datetime.now().isoformat()))
            self.ent_gelir_ad.delete(0, tk.END); self.ent_gelir_tutar.delete(0, tk.END)
            self.verileri_yukle()
        except: messagebox.showerror("Hata", "Miktarı kontrol et.")

    def gider_kaydet(self):
        try:
            m = float(self.ent_gider_tutar.get())
            with sqlite3.connect("final_butce_sistemi.db") as conn:
                conn.execute("INSERT INTO giderler (aciklama, miktar, kategori, tarih) VALUES (?, ?, ?, ?)", 
                             (self.ent_gider_ad.get(), m, self.combo_kat.get(), datetime.now().isoformat()))
            self.ent_gider_ad.delete(0, tk.END); self.ent_gider_tutar.delete(0, tk.END)
            self.verileri_yukle()
        except: messagebox.showerror("Hata", "Miktarı kontrol et.")

if __name__ == "__main__":
    root = tk.Tk()
    try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = PremiumButceApp(root)
    root.mainloop()