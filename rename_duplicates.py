import os
import sys
import argparse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def rename_duplicates(directory_path):
    target_dir = Path(directory_path)
    if not target_dir.is_dir():
        print(f"HATA: '{directory_path}' geçerli bir dizin değil.")
        return

    print(f"\nTaranıyor ve Çakışan İsimler Yeniden Adlandırılıyor: {target_dir.resolve()}\n")
    
    seen_names = set()
    renamed_count = 0

    # Dosyaları dolaşıyoruz
    for root, _, files in os.walk(target_dir):
        for filename in files:
            filepath = Path(root) / filename
            
            # Windows'ta dosya isimleri büyük/küçük harf duyarlı olmadığı için
            # isim çakışmalarını küçük harfe çevirerek kontrol ediyoruz.
            lower_filename = filename.lower()
            
            if lower_filename in seen_names:
                stem = filepath.stem
                suffix = filepath.suffix
                
                counter = 1
                new_filename = f"{stem}_{counter}{suffix}"
                
                # Yeni oluşturduğumuz ismin de daha önceden var olup olmadığını kontrol et
                while new_filename.lower() in seen_names:
                    counter += 1
                    new_filename = f"{stem}_{counter}{suffix}"
                
                new_filepath = Path(root) / new_filename
                
                try:
                    # Dosyanın adını bulunduğu klasör içerisinde değiştir
                    filepath.rename(new_filepath)
                    
                    # Yeni ismimizi listeye ekle
                    seen_names.add(new_filename.lower())
                    renamed_count += 1
                    
                    # Çok kalabalık yapmaması için çıktı formatını kısa tutuyoruz
                    # print(f"Değiştirildi: {filename} -> {new_filename}") 
                except Exception as e:
                    print(f"HATA: {filename} yeniden adlandırılamadı. Detay: {e}")
            else:
                # İsmi ilk defa görüyorsak, gördüklerimiz listesine ekle
                seen_names.add(lower_filename)

    print("-" * 30)
    print("📝 YENİDEN ADLANDIRMA RAPORU")
    print(f"✅ Çakıştığı İçin Yeniden Adlandırılan Toplam Dosya: {renamed_count}")
    print("💡 Artık tüm alt klasörlerdeki dosyaları, 'Bu hedefte aynı isimde dosya var' uyarısı almadan tek bir ana klasöre taşıyabilirsiniz.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tüm alt klasörlerdeki aynı isimli dosyaları bulur ve sonlarına numara ekleyerek çakışmayı önler.")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="Taranacak ana dizin (Varsayılan: Bulunduğunuz dizin)"
    )
    args = parser.parse_args()

    rename_duplicates(args.directory)
