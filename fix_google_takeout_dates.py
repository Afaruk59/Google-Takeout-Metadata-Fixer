import os
import sys
import json
import argparse
import re
import datetime
from pathlib import Path
import ctypes
import ctypes.wintypes

# Konsol çıktılarında emojilerin (utf-8) hata vermemesi için
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def set_ctime_windows(filepath, timestamp):
    """
    Windows üzerinde dosya oluşturulma tarihini ctypes kullanarak değiştirir.
    Ek bir kütüphane kurulumu gerektirmez.
    """
    if os.name != 'nt':
        return

    # 1 Ocak 1601'den (Windows epoch) 1 Ocak 1970'e (Unix epoch) kadar geçen saniye (11644473600)
    # 100-nanosaniyelik adımlara çeviriyoruz
    EPOCH_AS_FILETIME = 116444736000000000
    HUNDREDS_OF_NANOSECONDS = 10000000

    filetime = int(timestamp * HUNDREDS_OF_NANOSECONDS + EPOCH_AS_FILETIME)

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.wintypes.DWORD),
                    ("dwHighDateTime", ctypes.wintypes.DWORD)]

    ctime = FILETIME(filetime & 0xFFFFFFFF, filetime >> 32)

    # Parametreler (Windows API)
    GENERIC_WRITE = 0x40000000
    FILE_SHARE_WRITE = 0x00000002
    OPEN_EXISTING = 3
    FILE_ATTRIBUTE_NORMAL = 0x80

    handle = ctypes.windll.kernel32.CreateFileW(
        str(filepath),
        GENERIC_WRITE,
        FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None
    )

    if handle == -1 or handle == ctypes.wintypes.HANDLE(-1).value:
        raise OSError(f"Dosya açılamadı (Handle Error): {filepath}")

    try:
        # Sadece Creation Time (Oluşturma Tarihi) değiştirilir
        # SetFileTime(handle, lpCreationTime, lpLastAccessTime, lpLastWriteTime)
        success = ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(ctime), None, None)
        if not success:
            raise OSError(f"Oluşturulma tarihi ayarlanamadı: {filepath}")
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)

def parse_date_from_filename(filename):
    """
    Dosya isminden tarih ve saat bilgisini (YYYYMMDD_HHMMSS vb.) ayıklayıp
    UNIX timestamp (int) olarak döndürür. Bulamazsa None döner.
    """
    # Genel 8 rakamlı tarih (19XX veya 20XX) ve opsiyonel 6 rakamlı zaman
    pattern = r'(20\d{2}|19\d{2})[-_]?([0-1]\d)[-_]?([0-3]\d)[-_ ]?(?:WA\d+|([0-2]\d)[-_]?([0-5]\d)[-_]?([0-5]\d))?'
    match = re.search(pattern, filename)
    
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 1 <= month <= 12 and 1 <= day <= 31:
            hour = int(match.group(4)) if match.group(4) else 12
            minute = int(match.group(5)) if match.group(5) else 0
            second = int(match.group(6)) if match.group(6) else 0
            try:
                dt = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
                return int(dt.timestamp())
            except ValueError:
                pass
    return None

def process_directory(directory_path):
    target_dir = Path(directory_path)
    if not target_dir.is_dir():
        print(f"HATA: '{directory_path}' geçerli bir dizin değil.")
        return

    # Desteklenen bazı medya formatları
    media_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.heic', '.gif', '.mov', '.webp'}
    
    stats = {
        "total": 0,
        "success": 0,
        "success_filename": 0,
        "skipped_files": [],
        "error": 0
    }

    print(f"Taranıyor: {target_dir.resolve()} (Tüm alt klasörler dâhil)\n")

    # Tüm klasör ağacını dolaş
    for root, _, files in os.walk(target_dir):
        # O klasördeki tüm JSON dosyalarını bir kerede alalım
        json_files = [f for f in files if f.lower().endswith('.json')]
        
        for filename in files:
            filepath = Path(root) / filename
            
            # Sadece hedef medya dosyalarını filtrele
            if filepath.suffix.lower() not in media_extensions:
                continue
                
            stats["total"] += 1
            
            # Olası JSON dosya isimleri
            # Google Takeout bazen isimleri (özellikle supplemental-metadata uzantısını) kırpar (truncate eder).
            # Örn: "resim.png" için "resim.png.supplemental-metada.json" veya "resim.png.su.json" olabilir.
            json_filepath = None
            
            # 1. Birebir eşleşenler
            exact_candidates = [
                filepath.name + '.json',
                filepath.stem + '.json',
                filepath.name + '.supplemental-metadata.json',
                filepath.stem + '.supplemental-metadata.json'
            ]
            
            # Google Takeout "(1)" gibi ekleri bazen uzantının dışına atar.
            # Örn: image(1).png -> image.png.supplemental-metadata(1).json
            match_n = re.search(r'^(.*)\((\d+)\)$', filepath.stem)
            if match_n:
                base_stem = match_n.group(1)
                n = match_n.group(2)
                exact_candidates.extend([
                    f"{base_stem}{filepath.suffix}.supplemental-metadata({n}).json",
                    f"{base_stem}{filepath.suffix}({n}).json",
                    f"{base_stem.strip()}{filepath.suffix}.supplemental-metadata({n}).json",
                    f"{base_stem.strip()}{filepath.suffix}({n}).json"
                ])
            
            for candidate in exact_candidates:
                if candidate in json_files:
                    json_filepath = Path(root) / candidate
                    break
            
            # 2. Kırpılmış (Truncated) eşleşmeler
            # JSON dosyasının adı, medya dosyasının tam adıyla başlıyorsa (örn: resim.png.su.json)
            if not json_filepath:
                for jf in json_files:
                    if jf.startswith(filepath.name):
                        json_filepath = Path(root) / jf
                        break

            # 3. Kırpılmış (Truncated) ve uzantısız eşleşmeler
            # JSON dosyasının adı, medya dosyasının uzantısız adıyla (stem) başlıyorsa
            if not json_filepath:
                for jf in json_files:
                    # Başka dosyalarla (örn: resim(1).jpg vs resim.jpg) karışmasını önlemek için 
                    # daha sıkı bir uzunluk kontrolü yapabiliriz, ancak take out genelde stem'i korur.
                    if jf.startswith(filepath.stem + '.') and jf != filepath.name:
                        json_filepath = Path(root) / jf
                        break
            
            if not json_filepath:
                # JSON yoksa dosya adından tarih çıkarmayı dene
                fallback_timestamp = parse_date_from_filename(filepath.name)
                if fallback_timestamp:
                    try:
                        os.utime(filepath, (fallback_timestamp, fallback_timestamp))
                        set_ctime_windows(filepath, fallback_timestamp)
                        stats["success_filename"] += 1
                    except Exception:
                        stats["error"] += 1
                else:
                    stats["skipped_files"].append(filepath.name)
                continue

            try:
                # JSON dosyasını oku
                with open(json_filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # timestamp değerini al
                timestamp_str = data.get('photoTakenTime', {}).get('timestamp')
                
                if not timestamp_str:
                    stats["error"] += 1
                    continue
                
                timestamp = int(timestamp_str)
                
                # 1. Modification ve Access Time'ı güncelle (os.utime)
                os.utime(filepath, (timestamp, timestamp))
                
                # 2. Creation Time'ı güncelle (Windows API üzerinden)
                set_ctime_windows(filepath, timestamp)
                
                stats["success"] += 1

            except PermissionError:
                stats["error"] += 1
                continue # İzin sorunlarını atla
            except Exception as e:
                # Beklenmeyen diğer hatalar (Örn: Bozuk JSON)
                stats["error"] += 1
                continue

    # Raporlama
    print("📊 İŞLEM RAPORU")
    print("-" * 30)
    print(f"📁 Taranan Toplam Dosya: {stats['total']}")
    print(f"✅ JSON ile Tarihi Güncellenen: {stats['success']}")
    print(f"✅ İsimden Tarihi Güncellenen: {stats['success_filename']}")
    print(f"⚠️ Hiçbir Tarih Bulunamayan/Es Geçilen: {len(stats['skipped_files'])}")
    print(f"❌ Hata Alınan (İzin Sorunu vb.): {stats['error']}")
    
    if stats['skipped_files']:
        print("\n⚠️ EKSİK DOSYALAR LİSTESİ (Tarihi Bulunamayanlar):")
        print("-" * 30)
        for skipped in stats['skipped_files']:
            print(f"  - {skipped}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Takeout dosyalarının tarihlerini JSON verisinden okuyup düzeltir.")
    parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="Taranacak ana dizin (Varsayılan: Bulunduğunuz dizin)"
    )
    args = parser.parse_args()

    process_directory(args.directory)
