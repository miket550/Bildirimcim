import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import re
import time
import os

# === AYARLAR ===
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'
CHECK_INTERVAL = 120  # saniye
FAKULTELER = [
    {
        'isim': 'F.Ü - Ana Sayfa',
        'duyuru_url': 'https://www.firat.edu.tr/tr/page/announcement',
        'detay_selector': 'div.card-title a',
        'ana_link': 'https://www.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - İİBF',
        'duyuru_url': 'https://iibf.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://iibf.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Mühendislik Fakültesi',
        'duyuru_url': 'https://muhendislikf.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://muhendislikf.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Teknoloji Fakültesi',
        'duyuru_url': 'https://teknolojif.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://teknolojif.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Öğrenci DB',
        'duyuru_url': 'https://ogrencidb.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://ogrencidb.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Öğrenci Dekanlığı',
        'duyuru_url': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://ogrencidekanligi.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Yaz Okulu',
        'duyuru_url': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://yazokuluyeni.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Eğitim Fakültesi',
        'duyuru_url': 'https://egitimf.firat.edu.tr/tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://egitimf.firat.edu.tr'
    },
    {
        'isim': 'F.Ü - Kütüphane DB',
        'duyuru_url': 'https://kutuphanedb.firat.edu.tr/announcements-all',
        'detay_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'ana_link': 'https://kutuphanedb.firat.edu.tr'
    },
]

app = Flask('')

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
        print("Mesaj gönderilemedi:", e)

@app.route('/')
def home():
    return "Bot aktif"

def webserveri_baslat():
    app.run(host='0.0.0.0', port=8080)

def duyuruyu_gonder(fakulte):
    try:
        response = requests.get(fakulte['duyuru_url'], timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        duyurular = soup.select(fakulte['detay_selector'])

        if not duyurular:
            print(f"⚠️ {fakulte['isim']} - Duyuru bulunamadı.")
            return

        duyuru = duyurular[0]
        link = duyuru['href']
        if not link.startswith('http'):
            link = fakulte['ana_link'] + link

        detay = requests.get(link, verify=False)
        detay_soup = BeautifulSoup(detay.text, 'html.parser')

        baslik_tag = detay_soup.select_one('h1')
        baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"

        tarih_tag = detay_soup.select_one('div.new-section-detail-date p')
        if tarih_tag:
            tarih = ''.join([s.strip() for s in tarih_tag.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '')
        else:
            tarih = "Tarih bulunamadı"

        mesaj = f"<b>{fakulte['isim']}</b>\n{baslik}\n📅 {tarih}"
        telegrama_gonder(mesaj, link)
        print(f"✅ {fakulte['isim']} duyuru gönderildi.")

    except Exception as e:
        print(f"❗ {fakulte['isim']} HATA: {e}")

# === TEST MODU: TÜMÜNÜ BİR KEZ GÖNDER ===
print("🚀 Test modu başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

for fakulte in FAKULTELER:
    duyuruyu_gonder(fakulte)

print("🧪 Test tamamlandı. Artık sadece yeni duyurular gönderilecek.")
