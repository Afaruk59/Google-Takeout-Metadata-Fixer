import os
import argparse
from pathlib import Path

def delete_json_files(directory_path):
    target_dir = Path(directory_path)
    if not target_dir.is_dir():
        print(f"HATA: '{directory_path}' geçerli bir dizin değil.")
        return

    print(f"\nTaranıyor ve .json dosyaları SİLİNİYOR: {target_dir.resolve()} (Tüm alt klasörler dâhil)\n")
    
    deleted_count = 0
    error_count = 0

    for root, _, files in os.walk(target_dir):
        for filename in files:
            if filename.lower().endswith('.json'):
                filepath = Path(root) / filename
                try:
                    # Dosyayı sil
                    filepath.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Silinemedi: {filepath} - Hata: {e}")
                    error_count += 1

    print("-" * 30)
    print("🗑️ SİLME İŞLEMİ RAPORU")
    print(f"✅ Başarıyla Silinen .json Dosyası: {deleted_count}")
    print(f"❌ Silinemeyen/Hata Alınan: {error_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Belirtilen dizin ve alt dizinlerindeki tüm .json dosyalarını kalıcı olarak siler.")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="Taranacak ana dizin (Varsayılan: Bulunduğunuz dizin)"
    )
    args = parser.parse_args()

    # Silme işlemi geri döndürülemez olduğu için ekstra güvenlik onayı istiyoruz.
    print(f"⚠️ DİKKAT: '{Path(args.directory).resolve()}' dizinindeki ve tüm alt klasörlerindeki TÜM .json dosyaları KALICI OLARAK silinecektir.")
    confirm = input("Bu işlemi onaylıyor musunuz? (E/H): ")
    
    if confirm.lower() == 'e':
        delete_json_files(args.directory)
    else:
        print("İşlem kullanıcı tarafından İPTAL EDİLDİ. Hiçbir dosya silinmedi.")
