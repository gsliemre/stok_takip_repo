import customtkinter as ctk
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import os

class StokUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Stok Takip Sistemi")
        self.geometry("600x700")

        # --- ÜST ORTA: BARKOD ALANI ---
        self.frame_barkod = ctk.CTkFrame(self)
        self.frame_barkod.pack(pady=20, padx=20, fill="x")

        self.lbl_barkod_baslik = ctk.CTkLabel(self.frame_barkod, text="Ürün Barkodu", font=("Arial", 16, "bold"))
        self.lbl_barkod_baslik.pack(pady=5)

        # Barkod Resminin Basılacağı Label
        self.lbl_barkod_resim = ctk.CTkLabel(self.frame_barkod, text="Henüz ürün seçilmedi")
        self.lbl_barkod_resim.pack(pady=10)

        # --- FORM ELEMANLARI (Giriş Alanları) ---
        self.entry_ad = ctk.CTkEntry(self, placeholder_text="Ürün Adı")
        self.entry_ad.pack(pady=10)

        self.entry_kod = ctk.CTkEntry(self, placeholder_text="Barkod / Ürün Kod (ör: 12345678)")
        self.entry_kod.pack(pady=10)

        self.btn_ekle = ctk.CTkButton(self, text="Ürün Ekle & Barkod Oluştur", command=self.barkod_olustur_ve_goster)
        self.btn_ekle.pack(pady=10)

    def barkod_olustur_ve_goster(self):
        urun_kodu = self.entry_kod.get().strip()
        
        if not urun_kodu:
            return

        # 1. Barkod Görselini Oluştur ve Kaydet (Code128 formatı)
        COD128 = barcode.get_barcode_class('code128')
        barkod_obj = COD128(urun_kodu, writer=ImageWriter())
        
        dosya_adi = f"barkod_{urun_kodu}"
        barkod_obj.save(dosya_adi) # "barkod_12345678.png" olarak kaydeder

        # 2. Kaydedilen Resmi Yükle ve Arayüzde Üst Ortada Göster
        img_path = f"{dosya_adi}.png"
        pil_img = Image.open(img_path)
        
        # Resim boyutunu ayarla
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(250, 100))

        # Üst ortadaki Label'a resmi aktar
        self.lbl_barkod_resim.configure(image=ctk_img, text="")

if __name__ == "__main__":
    app = StokUygulamasi()
    app.mainloop()