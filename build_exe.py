#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ping Monitor uygulamasını exe dosyasına dönüştürme scripti
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """PyInstaller'ı yükle"""
    try:
        import PyInstaller
        print("PyInstaller zaten yuklu")
        return True
    except ImportError:
        print("PyInstaller yukleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller basariyla yuklendi")
            return True
        except subprocess.CalledProcessError:
            print("HATA: PyInstaller yuklenemedi")
            return False

def create_spec_file():
    """PyInstaller spec dosyası oluştur"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ping_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('devices.json', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PingMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('ping_monitor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Spec dosyasi olusturuldu: ping_monitor.spec")

def build_exe():
    """Exe dosyasını oluştur"""
    print("Exe dosyasi olusturuluyor...")
    try:
        # PyInstaller ile exe oluştur
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--onefile",  # Tek dosya olarak
            "--windowed",  # Konsol penceresi gösterme
            "--name=PingMonitor",  # Exe dosya adı
            "--add-data=devices.json;.",  # JSON dosyasını dahil et
            "--distpath=dist",  # Çıktı klasörü
            "--workpath=build",  # Geçici dosyalar klasörü
            "--specpath=.",  # Spec dosyası konumu
            "ping_monitor.py"
        ])
        
        print("Exe dosyasi basariyla olusturuldu!")
        print("Konum: dist/PingMonitor.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"HATA: Exe olusturma hatasi: {e}")
        return False
    
    return True

def create_icon():
    """Basit bir icon dosyası oluştur (opsiyonel)"""
    try:
        from PIL import Image, ImageDraw
        
        # 64x64 icon oluştur
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Basit ping icon'u çiz
        draw.ellipse([8, 8, 56, 56], fill=(94, 129, 172, 255))  # Mavi daire
        draw.text((20, 20), "P", fill=(255, 255, 255, 255))  # P harfi
        
        img.save('icon.ico', format='ICO')
        print("Icon dosyasi olusturuldu: icon.ico")
        return True
        
    except ImportError:
        print("UYARI: PIL kutuphanesi yok, icon olusturulamadi")
        return False
    except Exception as e:
        print(f"UYARI: Icon olusturma hatasi: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("Ping Monitor Exe Donusturucu")
    print("=" * 40)
    
    # Gerekli dosyaları kontrol et
    if not os.path.exists('ping_monitor.py'):
        print("HATA: ping_monitor.py dosyasi bulunamadi!")
        return
    
    if not os.path.exists('devices.json'):
        print("UYARI: devices.json dosyasi bulunamadi, olusturuluyor...")
        with open('devices.json', 'w', encoding='utf-8') as f:
            f.write('[]')
    
    # PyInstaller'ı yükle
    if not install_pyinstaller():
        return
    
    # Icon oluştur (opsiyonel)
    create_icon()
    
    # Exe oluştur
    if build_exe():
        print("\nISLEM TAMAMLANDI!")
        print("Exe dosyasi: dist/PingMonitor.exe")
        print("Exe dosyasini calistirmak icin dist klasorune gidin")
    else:
        print("\nHATA: Exe olusturma basarisiz!")

if __name__ == "__main__":
    main()
