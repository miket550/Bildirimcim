import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import re

TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'

DUYURU_SITELERI = [
    {
        'fakulte': 'F.Ü - Ana Sayfa',
        'duyuru_url': 'https://www.firat.edu.tr/tr/page/announcement',
        'link_selector': '.news-list a',
        'baslik_selector': 'h2.title',
        'tarih_selector': '.news-date'
    },
    {
        'fakulte': 'F.Ü - Mühendislik Fakültesi',
        'duyuru_url': 'https://muhendislikf.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - İktisadi ve İdari Bilimler Fakültesi',
        'duyuru_url': 'https://iibf.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Teknoloji Fakültesi',
        'duyuru_url': 'https://teknolojif.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Öğrenci İşleri Daire Başkanlığı',
        'duyuru_url': 'https://ogrencidb.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Öğrenci Dekanlığı',
        'duyuru_url': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Yaz Okulu Birimi',
        'duyuru_url': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Eğitim Fakültesi',
        'duyuru_url': 'https://egitimf.firat.edu.tr/tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
    {
        'fakulte': 'F.Ü - Kütüphane ve Dokümantasyon Daire Başkanlığı',
        'duyuru_url': 'https://kutuphanedb.firat.edu.tr/announcements-all',
        'link_selector': 'div.other-news-card.mb-3 a[href*="announcements-detail"]',
        'baslik_selector': 'div.new-section-detail-title h3',
        'tarih_selector': 'div.new-section-detail-date p'
    },
]

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
        print("Telegram gönderim hatası:", e)

def duyuru_bilgilerini_getir(site):
    try:
        response = requests.get(site['duyuru_url'], timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        duyurular = soup.select(site['link_selector'])

        if not duyurular:
            print(f"⚠️ {site['fakulte']}: Duyuru bulunamadı.")
            return

        duyuru = duyurular[0]
        link = duyuru['href'] if duyuru.has_attr('href') else ''
        if not link.startswith('http'):
            base = site['duyuru_url'].split('/announcements-all')[0].split('/tr')[0]
            link = base + link

        detay = requests.get(link, verify=False)
        detay_soup = BeautifulSoup(detay.text, 'html.parser')

        baslik_tag = detay_soup.select_one(site['baslik_selector'])
        baslik = baslik_tag.get_text(strip=True) if baslik_tag else 'Başlık bulunamadı'

        tarih_tag = detay_soup.select_one(site['tarih_selector'])
        if tarih_tag:
            tarih = ''.join([t.strip() for t in tarih_tag.stripped_strings])
        else:
            tarih = 'Tarih bulunamadı'

        mesaj = f"<b>{site['fakulte']}</b>\n{baslik}\n📅 {tarih}"
        telegrama_gonder(mesaj, link)
        print(f"✅ Gönderildi: {site['fakulte']}")

    except Exception as e:
        print(f"❗ {site['fakulte']} hata: {e}")

print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

for site in DUYURU_SITELERI:
    duyuru_bilgilerini_getir(site)
    time.sleep(1)
