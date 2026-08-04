import sqlite3
import csv
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

# Tema Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GelismisStokUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gelişmiş Envanter & Stok Takip Sistemi")
        self.geometry("950x670")
        self.resizable(False, False)

        self.db_kurulum()
        self.setup_ui()
        self.verileri_yukle()

    def db_kurulum(self):
        self.conn = sqlite3.connect("gelismis_stok.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_adi TEXT NOT NULL,
                kategori TEXT NOT NULL,
                stok_miktari INTEGER NOT NULL,
                fiyat REAL NOT NULL,
                kritik_esik INTEGER DEFAULT 5
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        # Üst Panel - Özet Rapor Kartları
        self.rapor_frame = ctk.CTkFrame(self)
        self.rapor_frame.pack(pady=10, padx=20, fill="x")

        self.lbl_toplam_cesit = ctk.CTkLabel(
            self.rapor_frame, 
            text="Toplam Çeşit: 0", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_toplam_cesit.pack(side="left", expand=True, pady=10)

        self.lbl_toplam_stok = ctk.CTkLabel(
            self.rapor_frame, 
            text="Toplam Adet: 0", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_toplam_stok.pack(side="left", expand=True, pady=10)

        self.lbl_toplam_deger = ctk.CTkLabel(
            self.rapor_frame, 
            text="Envanter Değeri: 0.00 TL", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_toplam_deger.pack(side="left", expand=True, pady=10)

        # Form ve Arama Alanı
        self.orta_frame = ctk.CTkFrame(self)
        self.orta_frame.pack(pady=5, padx=20, fill="x")

        # Sol: Ürün Ekle/Güncelle Formu
        self.form_frame = ctk.CTkFrame(self.orta_frame)
        self.form_frame.pack(side="left", padx=10, pady=10, fill="both")

        self.entry_ad = ctk.CTkEntry(self.form_frame, placeholder_text="Ürün Adı", width=150)
        self.entry_ad.grid(row=0, column=0, padx=5, pady=5)

        self.entry_kategori = ctk.CTkEntry(self.form_frame, placeholder_text="Kategori", width=120)
        self.entry_kategori.grid(row=0, column=1, padx=5, pady=5)

        self.entry_stok = ctk.CTkEntry(self.form_frame, placeholder_text="Stok", width=80)
        self.entry_stok.grid(row=1, column=0, padx=5, pady=5)

        self.entry_fiyat = ctk.CTkEntry(self.form_frame, placeholder_text="Fiyat (TL)", width=80)
        self.entry_fiyat.grid(row=1, column=1, padx=5, pady=5)

        self.btn_ekle = ctk.CTkButton(
            self.form_frame, 
            text="Ürün Kaydet", 
            fg_color="green", 
            hover_color="darkgreen",
            command=self.urun_kaydet
        )
        self.btn_ekle.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # Formu Temizle Butonu
        self.btn_temizle = ctk.CTkButton(
            self.form_frame, 
            text="🧹 Formu Temizle", 
            fg_color="gray", 
            hover_color="darkgray",
            command=self.form_temizle
        )
        self.btn_temizle.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        # Sağ: Arama ve Dışa Aktarma
        self.islem_frame = ctk.CTkFrame(self.orta_frame)
        self.islem_frame.pack(side="right", padx=10, pady=10, fill="both")

        self.entry_arama = ctk.CTkEntry(self.islem_frame, placeholder_text="🔍 Ürün Ara...", width=180)
        self.entry_arama.pack(pady=5, padx=5)
        self.entry_arama.bind("<KeyRelease>", self.urun_ara)

        self.btn_export = ctk.CTkButton(
            self.islem_frame, 
            text="📊 CSV/Excel Dışa Aktar", 
            fg_color="#1f538d",
            command=self.disa_aktar
        )
        self.btn_export.pack(pady=5, padx=5)

        # Tablo Alanı
        self.tablo_frame = ctk.CTkFrame(self)
        self.tablo_frame.pack(pady=10, padx=20, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2a2d2e")
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tablo = ttk.Treeview(
            self.tablo_frame, 
            columns=("ID", "Ürün Adı", "Kategori", "Stok", "Fiyat", "Durum"), 
            show="headings"
        )
        self.tablo.heading("ID", text="ID")
        self.tablo.heading("Ürün Adı", text="Ürün Adı")
        self.tablo.heading("Kategori", text="Kategori")
        self.tablo.heading("Stok", text="Stok Adedi")
        self.tablo.heading("Fiyat", text="Fiyat (TL)")
        self.tablo.heading("Durum", text="Stok Durumu")

        self.tablo.column("ID", width=40, anchor="center")
        self.tablo.column("Ürün Adı", width=200)
        self.tablo.column("Kategori", width=120)
        self.tablo.column("Stok", width=80, anchor="center")
        self.tablo.column("Fiyat", width=100, anchor="center")
        self.tablo.column("Durum", width=120, anchor="center")

        # Kritik Stok Renklendirmesi (Kırmızı Etiket)
        self.tablo.tag_configure('kritik', background='#7A1C1C', foreground='white')

        self.tablo.pack(fill="both", expand=True, padx=5, pady=5)
        self.tablo.bind("<Double-1>", self.satir_sec)

        # Alt Butonlar
        self.alt_frame = ctk.CTkFrame(self)
        self.alt_frame.pack(pady=5, padx=20, fill="x")

        self.btn_sil = ctk.CTkButton(
            self.alt_frame, 
            text="Seçili Ürünü Sil", 
            fg_color="red", 
            hover_color="darkred",
            command=self.urun_sil
        )
        self.btn_sil.pack(side="right", padx=10, pady=5)

        self.selected_id = None

    def urun_kaydet(self):
        ad = self.entry_ad.get()
        kat = self.entry_kategori.get()
        stok = self.entry_stok.get()
        fiyat = self.entry_fiyat.get()

        if not ad or not stok or not fiyat:
            messagebox.showwarning("Hata", "Lütfen gerekli alanları doldurun!")
            return

        try:
            stok_num = int(stok)
            fiyat_num = float(fiyat)

            if self.selected_id:
                # Güncelleme
                self.cursor.execute("""
                    UPDATE urunler 
                    SET urun_adi=?, kategori=?, stok_miktari=?, fiyat=? 
                    WHERE id=?
                """, (ad, kat, stok_num, fiyat_num, self.selected_id))
                self.selected_id = None
                self.btn_ekle.configure(text="Ürün Kaydet", fg_color="green")
            else:
                # Yeni Ekleme
                self.cursor.execute("""
                    INSERT INTO urunler (urun_adi, kategori, stok_miktari, fiyat) 
                    VALUES (?, ?, ?, ?)
                """, (ad, kat, stok_num, fiyat_num))

            self.conn.commit()
            self.form_temizle()
            self.verileri_yukle()
        except ValueError:
            messagebox.showerror("Hata", "Stok ve Fiyat sayısal bir değer olmalıdır!")

    def verileri_yukle(self, sorgu_sonucu=None):
        for item in self.tablo.get_children():
            self.tablo.delete(item)

        if sorgu_sonucu is None:
            self.cursor.execute("SELECT * FROM urunler")
            veriler = self.cursor.fetchall()
        else:
            veriler = sorgu_sonucu

        toplam_stok = 0
        toplam_deger = 0.0

        for row in veriler:
            u_id, ad, kat, stok, fiyat, kritik = row
            durum = "Kritik!" if stok <= kritik else "Normal"
            tag = "kritik" if stok <= kritik else ""

            self.tablo.insert("", "end", values=(u_id, ad, kat, stok, f"{fiyat:.2f}", durum), tags=(tag,))

            toplam_stok += stok
            toplam_deger += (stok * fiyat)

        # Rapor Kartlarını Güncelle
        self.lbl_toplam_cesit.configure(text=f"Toplam Çeşit: {len(veriler)}")
        self.lbl_toplam_stok.configure(text=f"Toplam Adet: {toplam_stok}")
        self.lbl_toplam_deger.configure(text=f"Envanter Değeri: {toplam_deger:,.2f} TL")

    def urun_ara(self, event):
        kelime = self.entry_arama.get()
        self.cursor.execute("SELECT * FROM urunler WHERE urun_adi LIKE ? OR kategori LIKE ?", (f"%{kelime}%", f"%{kelime}%"))
        sonuclar = self.cursor.fetchall()
        self.verileri_yukle(sonuclar)

    def satir_sec(self, event):
        secili = self.tablo.selection()
        if secili:
            item = self.tablo.item(secili[0])["values"]
            self.selected_id = item[0]

            self.entry_ad.delete(0, 'end')
            self.entry_ad.insert(0, item[1])

            self.entry_kategori.delete(0, 'end')
            self.entry_kategori.insert(0, item[2])

            self.entry_stok.delete(0, 'end')
            self.entry_stok.insert(0, item[3])

            self.entry_fiyat.delete(0, 'end')
            self.entry_fiyat.insert(0, item[4])

            self.btn_ekle.configure(text="Ürünü Güncelle", fg_color="orange")

    def urun_sil(self):
        secili = self.tablo.selection()
        if not secili:
            messagebox.showwarning("Hata", "Silinecek ürünü seçin!")
            return

        item_id = self.tablo.item(secili[0])["values"][0]
        self.cursor.execute("DELETE FROM urunler WHERE id = ?", (item_id,))
        self.conn.commit()
        self.verileri_yukle()
        self.form_temizle()

    def disa_aktar(self):
        dosya_yolu = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dosyası", "*.csv")])
        if dosya_yolu:
            self.cursor.execute("SELECT * FROM urunler")
            veriler = self.cursor.fetchall()

            with open(dosya_yolu, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Ürün Adı", "Kategori", "Stok", "Fiyat", "Kritik Eşik"])
                writer.writerows(veriler)

            messagebox.showinfo("Başarılı", "Stok verileri başarıyla aktarıldı!")

    def form_temizle(self):
        self.entry_ad.delete(0, 'end')
        self.entry_kategori.delete(0, 'end')
        self.entry_stok.delete(0, 'end')
        self.entry_fiyat.delete(0, 'end')
        self.selected_id = None
        self.btn_ekle.configure(text="Ürün Kaydet", fg_color="green")

if __name__ == "__main__":
    app = GelismisStokUygulamasi()
    app.mainloop()