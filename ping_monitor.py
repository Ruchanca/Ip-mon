#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ping Monitor - Cihaz IP'lerine düzenli aralıklarla ping atan uygulama
"""

import subprocess
import threading
import time
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import queue

# Modern renk paleti
class Colors:
    PRIMARY = "#2E3440"      # Koyu gri
    SECONDARY = "#3B4252"    # Orta gri
    ACCENT = "#5E81AC"       # Mavi
    SUCCESS = "#A3BE8C"      # Yeşil
    WARNING = "#EBCB8B"       # Sarı
    ERROR = "#BF616A"        # Kırmızı
    TEXT = "#ECEFF4"         # Açık gri
    BACKGROUND = "#1E1E1E"   # Çok koyu gri
    CARD = "#2D3748"         # Kart rengi
    BORDER = "#4A5568"       # Kenarlık rengi

class PingMonitor:
    def __init__(self, gui_callback=None):
        self.devices = []
        self.monitoring = False
        self.ping_interval = 30  # saniye
        self.ping_timeout = 5    # saniye
        self.log_queue = queue.Queue()
        self.gui_callback = gui_callback  # GUI güncelleme callback'i
        self.load_devices()
        
    def load_devices(self):
        """Cihaz listesini JSON dosyasından yükle"""
        try:
            if os.path.exists('devices.json'):
                with open('devices.json', 'r', encoding='utf-8') as f:
                    self.devices = json.load(f)
            else:
                self.devices = []
        except Exception as e:
            print(f"Cihaz listesi yüklenirken hata: {e}")
            self.devices = []
    
    def save_devices(self):
        """Cihaz listesini JSON dosyasına kaydet"""
        try:
            with open('devices.json', 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cihaz listesi kaydedilirken hata: {e}")
    
    def ping_device(self, ip):
        """Belirtilen IP'ye ping at"""
        try:
            # Windows için ping komutu
            if os.name == 'nt':
                cmd = ['ping', '-n', '1', '-w', str(self.ping_timeout * 1000), ip]
            else:
                cmd = ['ping', '-c', '1', '-W', str(self.ping_timeout), ip]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.ping_timeout + 2)
            return result.returncode == 0
        except Exception as e:
            self.log_message(f"Ping hatası ({ip}): {e}")
            return False
    
    def log_message(self, message):
        """Log mesajını kuyruğa ekle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_queue.put(log_entry)
        print(log_entry)
    
    def monitor_devices(self):
        """Cihazları izleme döngüsü"""
        while self.monitoring:
            for device in self.devices:
                if not self.monitoring:
                    break
                
                ip = device['ip']
                name = device.get('name', ip)
                previous_status = device.get('status', 'unknown')
                
                self.log_message(f"{name} ({ip}) ping atılıyor...")
                is_online = self.ping_device(ip)
                
                device['last_check'] = datetime.now().isoformat()
                new_status = 'online' if is_online else 'offline'
                
                # Durum değişikliği kontrolü
                if previous_status != new_status:
                    device['last_status_change'] = datetime.now().isoformat()
                    status_change_text = "ÇEVRİMİÇİ" if is_online else "ÇEVRİMDIŞI"
                    self.log_message(f"🔄 {name} ({ip}) DURUM DEĞİŞTİ: {status_change_text}")
                else:
                    status_text = "ÇEVRİMİÇİ" if is_online else "ÇEVRİMDIŞI"
                    self.log_message(f"✅ {name} ({ip}): {status_text}")
                
                device['status'] = new_status
                
                # GUI'yi güncelle (her ping sonrasında) - thread-safe
                if self.gui_callback:
                    self.gui_callback()
            
            # Cihaz listesini kaydet
            self.save_devices()
            
            # Bekleme süresi
            for _ in range(self.ping_interval):
                if not self.monitoring:
                    break
                time.sleep(1)
    
    def start_monitoring(self):
        """İzlemeyi başlat"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_devices, daemon=True)
            self.monitor_thread.start()
            self.log_message("İzleme başlatıldı")
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.monitoring = False
        self.log_message("İzleme durduruldu")
    
    def add_device(self, name, ip):
        """Yeni cihaz ekle"""
        device = {
            'name': name,
            'ip': ip,
            'status': 'unknown',
            'last_check': None,
            'last_status_change': None
        }
        self.devices.append(device)
        self.save_devices()
        self.log_message(f"Yeni cihaz eklendi: {name} ({ip})")
    
    def remove_device(self, index):
        """Cihaz sil"""
        if 0 <= index < len(self.devices):
            device = self.devices.pop(index)
            self.save_devices()
            self.log_message(f"Cihaz silindi: {device['name']} ({device['ip']})")

class PingMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔍 Ping Monitor - Cihaz İzleme Uygulaması")
        self.root.geometry("1000x700")
        self.root.configure(bg=Colors.BACKGROUND)
        
        # Modern tema ayarları
        self.setup_theme()
        
        # Monitor'u GUI callback ile başlat
        self.monitor = PingMonitor(gui_callback=self.update_display)
        
        self.setup_gui()
        self.update_display()
        self.process_log_queue()
    
    def setup_theme(self):
        """Modern tema ayarlarını yapılandır"""
        style = ttk.Style()
        
        # Modern tema stilleri
        style.theme_use('clam')
        
        # Ana frame stili
        style.configure('Main.TFrame', 
                       background=Colors.BACKGROUND,
                       relief='flat')
        
        # Kart stili
        style.configure('Card.TFrame',
                       background=Colors.CARD,
                       relief='flat',
                       borderwidth=1)
        
        # Başlık stili
        style.configure('Title.TLabel',
                       background=Colors.CARD,
                       foreground=Colors.TEXT,
                       font=('Segoe UI', 14, 'bold'))
        
        # Buton stilleri
        style.configure('Primary.TButton',
                       background=Colors.ACCENT,
                       foreground=Colors.TEXT,
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', Colors.SUCCESS),
                           ('pressed', Colors.WARNING)])
        
        style.configure('Success.TButton',
                       background=Colors.SUCCESS,
                       foreground=Colors.PRIMARY,
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Error.TButton',
                       background=Colors.ERROR,
                       foreground=Colors.TEXT,
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat',
                       borderwidth=0)
        
        # Treeview stili
        style.configure('Modern.Treeview',
                       background=Colors.CARD,
                       foreground=Colors.TEXT,
                       fieldbackground=Colors.CARD,
                       font=('Segoe UI', 9),
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Modern.Treeview.Heading',
                       background=Colors.PRIMARY,
                       foreground=Colors.TEXT,
                       font=('Segoe UI', 10, 'bold'),
                       relief='flat')
        
        # Entry stili
        style.configure('Modern.TEntry',
                       background=Colors.SECONDARY,
                       foreground='#000000',  # Siyah yazı rengi
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=1,
                       insertcolor='#000000')
        
        # Label stili
        style.configure('Modern.TLabel',
                       background=Colors.CARD,
                       foreground=Colors.TEXT,
                       font=('Segoe UI', 9))
        
        # Spinbox stili
        style.configure('Modern.TSpinbox',
                       background=Colors.SECONDARY,
                       foreground='#000000',  # Siyah yazı rengi
                       font=('Segoe UI', 10),
                       relief='flat',
                       borderwidth=1)
    
    def setup_gui(self):
        """GUI arayüzünü oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root, style='Main.TFrame', padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        title_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="15")
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="🔍 Ping Monitor", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Cihaz İzleme ve Durum Takip Sistemi", style='Modern.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Kontrol paneli
        control_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="15")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Kontrol butonları
        button_frame = ttk.Frame(control_frame, style='Card.TFrame')
        button_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="▶️ İzlemeyi Başlat", 
                                   style='Success.TButton', command=self.start_monitoring)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ İzlemeyi Durdur", 
                                 style='Error.TButton', command=self.stop_monitoring, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=10)
        
        # Ping aralığı ayarları
        settings_frame = ttk.Frame(control_frame, style='Card.TFrame')
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Label(settings_frame, text="⏱️ Ping Aralığı (saniye):", style='Modern.TLabel').grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.interval_var = tk.StringVar(value=str(self.monitor.ping_interval))
        interval_spin = ttk.Spinbox(settings_frame, from_=10, to=300, width=10, 
                                  textvariable=self.interval_var, style='Modern.TSpinbox')
        interval_spin.grid(row=0, column=1, padx=(0, 10))
        
        update_btn = ttk.Button(settings_frame, text="🔄 Güncelle", 
                               style='Primary.TButton', command=self.update_interval)
        update_btn.grid(row=0, column=2, padx=10)
        
        # Cihaz yönetimi
        device_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="15")
        device_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Cihaz yönetimi başlığı
        device_title = ttk.Label(device_frame, text="📱 Cihaz Yönetimi", style='Title.TLabel')
        device_title.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 15))
        
        # Cihaz listesi
        columns = ('Name', 'IP', 'Status', 'Last Check')
        self.device_tree = ttk.Treeview(device_frame, columns=columns, show='headings', 
                                       height=8, style='Modern.Treeview')
        
        # Sütun başlıkları
        self.device_tree.heading('Name', text='📛 Cihaz Adı')
        self.device_tree.heading('IP', text='🌐 IP Adresi')
        self.device_tree.heading('Status', text='📊 Durum')
        self.device_tree.heading('Last Check', text='⏰ Son Kontrol')
        
        # Sütun genişlikleri
        self.device_tree.column('Name', width=150, anchor='w')
        self.device_tree.column('IP', width=120, anchor='w')
        self.device_tree.column('Status', width=120, anchor='center')
        self.device_tree.column('Last Check', width=100, anchor='center')
        
        self.device_tree.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(device_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        scrollbar.grid(row=1, column=4, sticky=(tk.N, tk.S))
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        # Cihaz ekleme formu
        form_frame = ttk.Frame(device_frame, style='Card.TFrame')
        form_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(form_frame, text="📝 Cihaz Adı:", style='Modern.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.name_entry = ttk.Entry(form_frame, width=20, style='Modern.TEntry')
        self.name_entry.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(form_frame, text="🌐 IP Adresi:", style='Modern.TLabel').grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.ip_entry = ttk.Entry(form_frame, width=20, style='Modern.TEntry')
        self.ip_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Butonlar
        button_frame = ttk.Frame(device_frame, style='Card.TFrame')
        button_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E))
        
        add_btn = ttk.Button(button_frame, text="➕ Cihaz Ekle", 
                           style='Success.TButton', command=self.add_device)
        add_btn.grid(row=0, column=0, padx=(0, 10))
        
        remove_btn = ttk.Button(button_frame, text="🗑️ Seçili Cihazı Sil", 
                               style='Error.TButton', command=self.remove_device)
        remove_btn.grid(row=0, column=1, padx=10)
        
        # Log paneli
        log_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="15")
        log_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Log başlığı
        log_title = ttk.Label(log_frame, text="📋 Log Kayıtları", style='Title.TLabel')
        log_title.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Log text alanı
        self.log_text = tk.Text(log_frame, height=15, width=50, wrap=tk.WORD,
                               bg=Colors.SECONDARY, fg=Colors.TEXT, 
                               font=('Consolas', 9), relief='flat', borderwidth=0,
                               insertbackground=Colors.TEXT, selectbackground=Colors.ACCENT)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Log kontrol butonları
        log_control_frame = ttk.Frame(log_frame, style='Card.TFrame')
        log_control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        clear_btn = ttk.Button(log_control_frame, text="🗑️ Logları Temizle", 
                               style='Error.TButton', command=self.clear_logs)
        clear_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Status göstergeleri
        status_frame = ttk.Frame(log_control_frame, style='Card.TFrame')
        status_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.status_online = ttk.Label(status_frame, text="🟢 Çevrimiçi: 0", style='Modern.TLabel')
        self.status_online.grid(row=0, column=0, padx=(0, 10))
        
        self.status_offline = ttk.Label(status_frame, text="🔴 Çevrimdışı: 0", style='Modern.TLabel')
        self.status_offline.grid(row=0, column=1)
        
        # Alt bilgi (Footer)
        footer_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="10")
        footer_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        footer_label = ttk.Label(footer_frame, text="© 2025 Süleyman Rüçhan Çakıllı Tarafından Geliştirilmektedir", 
                                style='Modern.TLabel', font=('Segoe UI', 8))
        footer_label.grid(row=0, column=0, sticky=tk.W)
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        device_frame.columnconfigure(0, weight=1)
        device_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
    
    def start_monitoring(self):
        """İzlemeyi başlat"""
        try:
            self.monitor.ping_interval = int(self.interval_var.get())
            self.monitor.start_monitoring()
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Başarı animasyonu
            self.animate_button(self.start_btn, Colors.SUCCESS)
            self.log_message("🚀 İzleme başlatıldı!")
            
        except ValueError:
            messagebox.showerror("❌ Hata", "Geçerli bir ping aralığı girin!")
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        self.monitor.stop_monitoring()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # Durdurma animasyonu
        self.animate_button(self.stop_btn, Colors.ERROR)
        self.log_message("⏹️ İzleme durduruldu!")
    
    def update_interval(self):
        """Ping aralığını güncelle"""
        try:
            new_interval = int(self.interval_var.get())
            if 10 <= new_interval <= 300:
                self.monitor.ping_interval = new_interval
                messagebox.showinfo("✅ Başarılı", f"Ping aralığı {new_interval} saniye olarak güncellendi")
                self.log_message(f"⚙️ Ping aralığı güncellendi: {new_interval} saniye")
            else:
                messagebox.showerror("❌ Hata", "Ping aralığı 10-300 saniye arasında olmalı!")
        except ValueError:
            messagebox.showerror("❌ Hata", "Geçerli bir sayı girin!")
    
    def add_device(self):
        """Yeni cihaz ekle"""
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        
        if not name or not ip:
            messagebox.showerror("❌ Hata", "Cihaz adı ve IP adresi gerekli!")
            return
        
        # Basit IP format kontrolü
        if not self.is_valid_ip(ip):
            messagebox.showerror("❌ Hata", "Geçerli bir IP adresi girin!")
            return
        
        self.monitor.add_device(name, ip)
        self.name_entry.delete(0, tk.END)
        self.ip_entry.delete(0, tk.END)
        self.update_display()
        
        # Başarı mesajı
        self.log_message(f"✅ Yeni cihaz eklendi: {name} ({ip})")
    
    def remove_device(self):
        """Seçili cihazı sil"""
        selection = self.device_tree.selection()
        if not selection:
            messagebox.showwarning("⚠️ Uyarı", "Silinecek cihazı seçin!")
            return
        
        item = self.device_tree.item(selection[0])
        index = self.device_tree.index(selection[0])
        device_name = item['values'][0]
        
        if messagebox.askyesno("🗑️ Onay", f"'{device_name}' cihazını silmek istediğinizden emin misiniz?"):
            self.monitor.remove_device(index)
            self.update_display()
            self.log_message(f"🗑️ Cihaz silindi: {device_name}")
    
    def is_valid_ip(self, ip):
        """IP adresi formatını kontrol et"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False
    
    def update_display(self):
        """Cihaz listesini güncelle"""
        try:
            # Mevcut öğeleri temizle
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            online_count = 0
            offline_count = 0
            
            # Cihazları ekle
            for device in self.monitor.devices:
                status = device.get('status', 'unknown')
                last_check = device.get('last_check', '')
                
                if last_check:
                    try:
                        dt = datetime.fromisoformat(last_check)
                        last_check = dt.strftime("%H:%M:%S")
                    except:
                        pass
                
                # Status sayacı
                if status == 'online':
                    online_count += 1
                    status_text = "🟢 ÇEVRİMİÇİ"
                elif status == 'offline':
                    offline_count += 1
                    status_text = "🔴 ÇEVRİMDIŞI"
                else:
                    status_text = "⚪ BİLİNMİYOR"
                
                self.device_tree.insert('', 'end', values=(
                    device.get('name', ''),
                    device.get('ip', ''),
                    status_text,
                    last_check
                ))
            
            # Status göstergelerini güncelle
            self.status_online.config(text=f"🟢 Çevrimiçi: {online_count}")
            self.status_offline.config(text=f"🔴 Çevrimdışı: {offline_count}")
            
        except Exception as e:
            # GUI güncelleme hatası
            pass
    
    def process_log_queue(self):
        """Log kuyruğunu işle"""
        try:
            while True:
                log_entry = self.monitor.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_entry + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Her 100ms'de bir kontrol et
        self.root.after(100, self.process_log_queue)
    
    def clear_logs(self):
        """Log kayıtlarını temizle"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ Log kayıtları temizlendi!")
    
    def animate_button(self, button, color):
        """Buton animasyonu"""
        original_color = button.cget('background')
        button.configure(background=color)
        self.root.after(200, lambda: button.configure(background=original_color))
    
    def log_message(self, message):
        """Log mesajını ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Uygulama kapatılırken"""
        if self.monitor.monitoring:
            self.monitor.stop_monitoring()
        self.root.destroy()

def main():
    """Ana fonksiyon"""
    print("Ping Monitor uygulaması başlatılıyor...")
    app = PingMonitorGUI()
    app.run()

if __name__ == "__main__":
    main()
