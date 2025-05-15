import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import os
import json

# ====== AYARLAR ======
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'

SITELER = [
    {
        'ad': 'F.Ü - Ana Sayfa',
        'duyuru_url': 'https://www.firat.edu.tr/tr/page/announcement',
        'ana_sayfa': 'https://www.firat.edu.tr',
        'baslik_secici': 'h2.title',
        'tarih_secici': 'span.date'
    },
    {
        'ad': 'F.Ü - Mühendislik Fakültesi',
        'duyuru_url': 'https://muhendislikf.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://muhendislikf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - İİBF',
        'duyuru_url': 'https://iibf.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://iibf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Teknoloji Fakültesi',
        'duyuru_url': 'https://teknolojif.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://teknolojif.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Öğrenci DB',
        'duyuru_url': 'https://ogrencidb.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://ogrencidb.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Öğrenci Dekanlığı',
        'duyuru_url': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://ogrencidekanligi.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Yaz Okulu',
        'duyuru_url': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://yazokuluyeni.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Eğitim Fakültesi',
        'duyuru_url': 'https://egitimf.firat.edu.tr/tr/announcements-all',
        'ana_sayfa': 'https://egitimf.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
    },
    {
        'ad': 'F.Ü - Kütüphane',
        'duyuru_url': 'https://kutuphanedb.firat.edu.tr/announcements-all',
        'ana_sayfa': 'https://kutuphanedb.firat.edu.tr',
        'baslik_secici': 'div.new-section-detail-title h3',
        'tarih_secici': 'div.new-section-detail-date p'
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
        data['reply_markup'] = json.dumps({
            "inline_keyboard": [[{"text": "Duyuruya Git", "url": buton_linki}]]
        })
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram gönderim hatası:", e)

def kontrol_et(site):
    try:
        response = requests.get(site['duyuru_url'], timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        duyuru_linki = soup.select_one('a[href*="announcements-detail"], a[href*="/tr/news"]')
        if not duyuru_linki:
            print(f"⚠️ {site['ad']}: Duyuru bağlantısı bulunamadı.")
            return

        link = duyuru_linki['href']
        if not link.startswith('http'):
            link = site['ana_sayfa'].rstrip('/') + '/' + link.lstrip('/')

        detay = requests.get(link, verify=False)
        detay_soup = BeautifulSoup(detay.text, 'html.parser')

        baslik_tag = detay_soup.select_one(site['baslik_secici'])
        baslik = baslik_tag.get_text(strip=True) if baslik_tag else 'Başlık bulunamadı'

        tarih_tag = detay_soup.select_one(site['tarih_secici'])
        if tarih_tag:
            tarih = ''.join(tarih_tag.stripped_strings).replace('\n', '').replace(' ', '')
        else:
            tarih = 'Tarih bulunamadı'

        mesaj = f"<b>{site['ad']}</b>\n{baslik}\n📅 {tarih}"
        telegrama_gonder(mesaj, link)
        print(f"✅ {site['ad']}: Bildirim gönderildi.")

    except Exception as e:
        print(f"❌ {site['ad']} hatası:", e)

def hepsini_kontrol_et():
    for site in SITELER:
        kontrol_et(site)

# ====== BAŞLAT ======
print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

hepsini_kontrol_et()
