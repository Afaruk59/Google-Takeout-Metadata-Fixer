import os
import shutil
import datetime
import argparse

def organize_files_by_year(target_directory):
    """
    Belirtilen dizindeki tüm dosyaları (klasörler, .py scriptleri ve markdown vb. hariç)
    değiştirilme tarihlerinin (mtime) yıllarına göre ilgili klasörlere taşır.
    """
    if not os.path.isdir(target_directory):
        print(f"Hata: Belirtilen dizin bulunamadı - {target_directory}")
        return

    moved_count = 0
    error_count = 0

    print(f"Tarama başlatıldı: {target_directory}\n")

    for filename in os.listdir(target_directory):
        filepath = os.path.join(target_directory, filename)

        # Sadece dosyaları hedefle, klasörleri atla
        if not os.path.isfile(filepath):
            continue

        # Python scriptlerini, Git dosyalarını ve diğer sistemsel/kılavuz dosyaları atla
        if filename.endswith(".py") or filename in ["README.md", "walkthrough.md", ".gitignore", ".gitattributes"] or filename.startswith("."):
            continue

        try:
            # Dosyanın değiştirilme tarihini (mtime) al
            # fix_google_takeout_dates.py çalıştıktan sonra bu mtime doğru tarihe sahip olacaktır
            mtime = os.path.getmtime(filepath)
            date_mtime = datetime.datetime.fromtimestamp(mtime)
            year = str(date_mtime.year)

            # Yıla ait hedef klasör yolunu oluştur
            year_folder_path = os.path.join(target_directory, year)

            # Eğer o yıla ait klasör yoksa oluştur
            if not os.path.exists(year_folder_path):
                os.makedirs(year_folder_path)
                print(f"Yeni klasör oluşturuldu: {year}")

            # Dosyanın taşınacağı yeni yol
            destination_path = os.path.join(year_folder_path, filename)
            
            # Eğer hedefte aynı isimde dosya yoksa taşı
            if not os.path.exists(destination_path):
                shutil.move(filepath, destination_path)
                moved_count += 1
            else:
                print(f"Uyarı: {filename} zaten '{year}' klasöründe mevcut, taşınmadı.")
                error_count += 1
                
        except Exception as e:
            print(f"Hata ({filename}): {e}")
            error_count += 1

    print(f"\nİşlem tamamlandı. Toplam {moved_count} dosya başarıyla yıllara göre klasörlendi.")
    if error_count > 0:
        print(f"{error_count} dosya taşınırken sorun oluştu veya hedefte zaten mevcuttu.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dosyaları değiştirilme tarihlerine göre yıla ayırarak klasörler.")
    parser.add_argument("path", nargs="?", default=".", help="İşlem yapılacak dizin (Varsayılan: Mevcut dizin)")
    args = parser.parse_args()

    organize_files_by_year(args.path)
