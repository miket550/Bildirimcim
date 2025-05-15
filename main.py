import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import re

# AYARLAR
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'

# DUYURU KAYIT
eski_duyurular = {}

# SİTELER
DUYURU_SITELERI = {
    'F.Ü - Ana Sayfa': 'https://www.firat.edu.tr/tr/page/announcement',
    'F.Ü - İİBF': 'https://iibf.firat.edu.tr/announcements-all',
    'F.Ü - Mühendislik Fakültesi': 'https://muhendislikf.firat.edu.tr/announcements-all',
    'F.Ü - Teknoloji Fakültesi': 'https://teknolojif.firat.edu.tr/announcements-all',
    'F.Ü - Öğrenci İşleri': 'https://ogrencidb.firat.edu.tr/announcements-all',
    'F.Ü - Öğrenci Dekanlığı': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
    'F.Ü - Yaz Okulu': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
    'F.Ü - Eğitim Fakültesi': 'https://egitimf.firat.edu.tr/tr/announcements-all',
    'F.Ü - Kütüphane': 'https://kutuphanedb.firat.edu.tr/announcements-all',
}

# Web sunucu (Render için)
app = Flask('')
@app.route('/')
def home():
    return "Bot aktif"

def webserveri_baslat():
    app.run(host='0.0.0.0', port=8080)

def telegrama_gonder(mesaj, buton_linki=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': mesaj,
        'parse_mode': 'HTML'
    }
    if buton_linki:
        data['reply_markup'] = '{"inline_keyboard":[[{"text":"Duyuruya Git", "url":"' + buton_linki + '"}]]}'
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram mesajı gönderilemedi:", e)

def duyurulari_kontrol_et():
    for fakulte, url in DUYURU_SITELERI.items():
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            duyurular = soup.select('div.other-news-card.mb-3 a[href*="announcements-detail"]')
            if not duyurular:
                print(f"⚠️ {fakulte} için duyuru bulunamadı.")
                continue

            ilk_duyuru = duyurular[0]
            link = ilk_duyuru['href']
            if not link.startswith('http'):
                link = url.split('/announcements-all')[0] + link

            # Eski duyuruyla karşılaştır
            onceki_link = eski_duyurular.get(fakulte)
            if onceki_link == link:
                continue  # Zaten bildirildi

            # Detay sayfasına git
            detay = requests.get(link, verify=False)
            detay_soup = BeautifulSoup(detay.text, 'html.parser')

            # Başlık ve tarih al
            baslik_tag = detay_soup.select_one('h1')
            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"

            tarih_tag = detay_soup.select_one('div.new-section-detail-date p')
            if tarih_tag:
                tarih = ''.join([s.strip() for s in tarih_tag.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '')
            else:
                tarih = "Tarih bulunamadı"

            mesaj = f"<b>{fakulte}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            eski_duyurular[fakulte] = link
            print(f"✅ {fakulte} duyurusu gönderildi.")

        except Exception as e:
            print(f"❗ {fakulte} kontrolünde hata:", e)

print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

# İlk çalıştırma ve sonra döngü
duyurulari_kontrol_et()

import time
while True:
    time.sleep(120)
    duyurulari_kontrol_et()
