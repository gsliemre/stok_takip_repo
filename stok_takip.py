import csv
import sqlite3
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import barcode
from barcode.writer import ImageWriter

# Tema Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GelismisStokUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gelişmiş Envanter & Stok Takip Sistemi")
        self.geometry("950x750")
        self.resizable(False, False)

        self.db_kurulum()
        self.setup_ui()
        self.verileri_yukle()

    def db_kurulum(self):
        """Veritabanını ve tabloyu oluşturur."""
        self.conn = sqlite3.connect("stok_veritabani.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_kodu TEXT UNIQUE,
                urun_adi TEXT,
                kategori TEXT,
                adetcik INTEGER,
                fiyat REAL
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        """Arayüz bileşenlerini oluşturur."""
        
        # ==========================================
        # 1. ÜST ORTA BARKOD ALANI
        # ==========================================
        self.frame_barkod = ctk.CTkFrame(self)
        self.frame_barkod.pack(pady=10, padx=20, fill="x")

        self.lbl_barkod_baslik = ctk.CTkLabel(
            self.frame_barkod, 
            text="📌 Ürün Barkod Alanı", 
            font=("Arial", 14, "bold")
        )
        self.lbl_barkod_baslik.pack(pady=(5, 2))

        self.lbl_barkod_resim = ctk.CTkLabel(
            self.frame_barkod, 
            text="Barkodu görüntülemek için tablodan ürün seçin veya yeni ürün ekleyin."
        )
        self.lbl_barkod_resim.pack(pady=(2, 10))

        # ==========================================
        # 2. FORM / GİRİŞ ALANLARI FRAME
        # ==========================================
        self.frame_form = ctk.CTkFrame(self)
        self.frame_form.pack(pady=10, padx=20, fill="x")

        # Form Elemanları
        self.entry_kod = ctk.CTkEntry(self.frame_form, placeholder_text="Ürün Kodu (Barkod No)")
        self.entry_kod.grid(row=0, column=0, padx=10, pady=10)

        self.entry_ad = ctk.CTkEntry(self.frame_form, placeholder_text="Ürün Adı")
        self.entry_ad.grid(row=0, column=1, padx=10, pady=10)

        self.entry_kategori = ctk.CTkEntry(self.frame_form, placeholder_text="Kategori")
        self.entry_kategori.grid(row=0, column=2, padx=10, pady=10)

        self.entry_adet = ctk.CTkEntry(self.frame_form, placeholder_text="Adet")
        self.entry_adet.grid(row=1, column=0, padx=10, pady=10)

        self.entry_fiyat = ctk.CTkEntry(self.frame_form, placeholder_text="Birim Fiyat (TL)")
        self.entry_fiyat.grid(row=1, column=1, padx=10, pady=10)

        # Butonlar
        self.btn_ekle = ctk.CTkButton(self.frame_form, text="Ürün Ekle & Barkod Üret", command=self.urun_ekle)
        self.btn_ekle.grid(row=1, column=2, padx=10, pady=10)

        self.btn_temizle = ctk.CTkButton(self.frame_form, text="Formu Temizle", fg_color="gray", command=self.form_temizle)
        self.btn_temizle.grid(row=2, column=1, padx=10, pady=(0, 10))

        # ==========================================
        # 3. TABLO (TREEVIEW) ALANI
        # ==========================================
        self.frame_tablo = ctk.CTkFrame(self)
        self.frame_tablo.pack(pady=10, padx=20, fill="both", expand=True)

        columns = ("id", "urun_kodu", "urun_adi", "kategori", "adetcik", "fiyat")
        self.tree = ttk.Treeview(self.frame_tablo, columns=columns, show="headings", height=10)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("urun_kodu", text="Ürün Kodu")
        self.tree.heading("urun_adi", text="Ürün Adı")
        self.tree.heading("kategori", text="Kategori")
        self.tree.heading("adetcik", text="Adet")
        self.tree.heading("fiyat", text="Fiyat (TL)")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("urun_kodu", width=120, anchor="center")
        self.tree.column("urun_adi", width=180)
        self.tree.column("kategori", width=120)
        self.tree.column("adetcik", width=80, anchor="center")
        self.tree.column("fiyat", width=100, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Tablodan Satır Seçildiğinde Çalışacak Olay
        self.tree.bind("<<TreeviewSelect>>", self.tablodan_sec)

    # ==========================================
    # DÜZELTİLMİŞ BARKOD METODU
    # ==========================================
    def barkod_olustur_ve_goster(self, urun_kodu):
        """Barkodu sadece çizgi ve altında numara olacak şekilde üretir."""
        if not urun_kodu:
            return

        try:
            dosya_adi = f"barkod_{urun_kodu}"
            img_path = f"{dosya_adi}.png"

            # Code128 Barkod Yapılandırması
            COD128 = barcode.get_barcode_class('code128')
            
            # Sadece geçerli python-barcode opsiyonları
            options = {
                'write_text': True,     # Sadece ürün kodunun numarasını çizer
                'module_width': 0.25,   # Çizgi kalınlığı
                'module_height': 10.0,  # Çizgi yüksekliği
                'font_size': 10,        # Numara yazı boyutu
                'text_distance': 3.5,   # Numarayla çizgi arası mesafe
                'quiet_zone': 2.0       # Kenar boşlukları
            }

            barkod_obj = COD128(str(urun_kodu), writer=ImageWriter())
            barkod_obj.save(dosya_adi, options=options)

            # Görseli kilitlenme (file locking) olmadan yükleyip göster
            with Image.open(img_path) as pil_img:
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(230, 95))
                self.lbl_barkod_resim.configure(image=ctk_img, text="")

        except Exception as e:
            messagebox.showerror("Barkod Hatası", f"Barkod oluşturulamadı: {e}")

    # ==========================================
    # VERİTABANI VE FORM İŞLEMLERİ
    # ==========================================
    def urun_ekle(self):
        kod = self.entry_kod.get().strip()
        ad = self.entry_ad.get().strip()
        kategori = self.entry_kategori.get().strip()
        adet = self.entry_adet.get().strip()
        fiyat = self.entry_fiyat.get().strip()

        if not (kod and ad and adet and fiyat):
            messagebox.showwarning("Eksik Bilgi", "Lütfen tüm zorunlu alanları doldurun!")
            return

        try:
            self.cursor.execute(
                "INSERT INTO urunler (urun_kodu, urun_adi, kategori, adetcik, fiyat) VALUES (?, ?, ?, ?, ?)",
                (kod, ad, kategori, int(adet), float(fiyat))
            )
            self.conn.commit()
            
            # Ürün eklenince barkodunu üstte göster
            self.barkod_olustur_ve_goster(kod)
            
            self.verileri_yukle()
            self.form_temizle()
            messagebox.showinfo("Başarılı", "Ürün başarıyla eklendi ve barkodu oluşturuldu.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu Ürün Kodu zaten kayıtlı!")
        except ValueError:
            messagebox.showerror("Hata", "Adet tam sayı, fiyat sayısal bir değer olmalıdır!")

    def verileri_yukle(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT * FROM urunler")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def tablodan_sec(self, event):
        """Tablodan tıklandığında bilgileri forma doldurur ve barkodunu gösterir."""
        secili_item = self.tree.selection()
        if not secili_item:
            return

        item_values = self.tree.item(secili_item[0], "values")
        urun_kodu = item_values[1]

        # Formu seçili veriyle doldur
        self.entry_kod.delete(0, "end")
        self.entry_kod.insert(0, item_values[1])
        
        self.entry_ad.delete(0, "end")
        self.entry_ad.insert(0, item_values[2])
        
        self.entry_kategori.delete(0, "end")
        self.entry_kategori.insert(0, item_values[3])

        self.entry_adet.delete(0, "end")
        self.entry_adet.insert(0, item_values[4])

        self.entry_fiyat.delete(0, "end")
        self.entry_fiyat.insert(0, item_values[5])

        # Üst ortadaki barkod alanını güncelle
        self.barkod_olustur_ve_goster(urun_kodu)

    def form_temizle(self):
        self.entry_kod.delete(0, "end")
        self.entry_ad.delete(0, "end")
        self.entry_kategori.delete(0, "end")
        self.entry_adet.delete(0, "end")
        self.entry_fiyat.delete(0, "end")


if __name__ == "__main__":
    app = GelismisStokUygulamasi()
    app.mainloop()