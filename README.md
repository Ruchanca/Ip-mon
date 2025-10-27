# Ping Monitor - Cihaz İzleme Uygulaması

Bu uygulama, belirtilen IP adreslerine düzenli aralıklarla ping atarak cihazların çevrimiçi/çevrimdışı durumlarını izler.

## Özellikler

- **Grafik Arayüz**: Kullanıcı dostu tkinter tabanlı GUI
- **Çoklu Cihaz İzleme**: Birden fazla IP adresini aynı anda izleme
- **Gerçek Zamanlı Durum**: Cihazların anlık durumunu görüntüleme
- **Özelleştirilebilir Aralık**: Ping aralığını 10-300 saniye arasında ayarlama
- **Log Kayıtları**: Tüm ping işlemlerini ve durum değişikliklerini kaydetme
- **Veri Kalıcılığı**: Cihaz listesi JSON dosyasında saklanır
- **Kolay Yönetim**: Cihaz ekleme/silme işlemleri

## Kurulum

1. Python 3.6 veya üzeri sürümün yüklü olduğundan emin olun
2. Bu projeyi indirin
3. Gerekli dosyaların mevcut olduğunu kontrol edin:
   - `ping_monitor.py` (ana uygulama)
   - `devices.json` (cihaz listesi)
   - `requirements.txt` (gereksinimler)

## Kullanım

### Uygulamayı Başlatma
```bash
python ping_monitor.py
```

### Cihaz Ekleme
1. "Cihaz Adı" alanına cihaz için bir isim girin
2. "IP Adresi" alanına hedef IP adresini girin
3. "Cihaz Ekle" butonuna tıklayın

### İzleme Başlatma
1. "Ping Aralığı" değerini ayarlayın (varsayılan: 30 saniye)
2. "İzlemeyi Başlat" butonuna tıklayın
3. Log panelinde ping sonuçlarını takip edin

### Cihaz Silme
1. Cihaz listesinden silmek istediğiniz cihazı seçin
2. "Seçili Cihazı Sil" butonuna tıklayın
3. Onay penceresinde "Evet" seçeneğini seçin

## Dosya Yapısı

- `ping_monitor.py`: Ana uygulama dosyası
- `devices.json`: Cihaz listesi (otomatik oluşturulur)
- `requirements.txt`: Python gereksinimleri
- `README.md`: Bu dosya

## Özellik Detayları

### Ping İşlemi
- Windows ve Linux sistemlerde çalışır
- Timeout süresi: 5 saniye
- Ping aralığı: 10-300 saniye (ayarlanabilir)

### Durum Takibi
- **ÇEVRİMİÇİ**: Ping başarılı
- **ÇEVRİMDIŞI**: Ping başarısız
- **BİLİNMİYOR**: Henüz ping atılmamış

### Log Sistemi
- Tüm ping işlemleri kaydedilir
- Zaman damgası ile birlikte
- Gerçek zamanlı görüntüleme
- Log temizleme özelliği

## Sistem Gereksinimleri

- Python 3.6+
- Windows, Linux veya macOS
- İnternet bağlantısı (hedef IP'lere erişim için)
- Ping komutuna erişim (genellikle varsayılan olarak mevcuttur)

## Sorun Giderme

### Ping Çalışmıyor
- Hedef IP adresinin doğru olduğundan emin olun
- Firewall ayarlarını kontrol edin
- Ağ bağlantınızı kontrol edin

### Uygulama Açılmıyor
- Python sürümünüzü kontrol edin (3.6+ gerekli)
- Gerekli dosyaların mevcut olduğundan emin olun
- Hata mesajlarını kontrol edin

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir. Özgürce kullanabilir ve değiştirebilirsiniz.


