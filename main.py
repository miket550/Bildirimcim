import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import json
import time
import os

# ====== AYARLAR ======
TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'
CHECK_INTERVAL = 120  # saniye cinsinden

SITELER = [
    {
        "fakulte": "F.Ü - Ana Sayfa",
        "duyuru_url": "https://www.firat.edu.tr/tr/page/announcement",
        "ana_url": "https://www.firat.edu.tr",
        "link_selector": ".card-title a",
        "baslik_selector": "h2.title",
        "tarih_selector": "div.col-12.col-sm-6.col-md-4.col-lg-3 small"
    },
    {
        "fakulte": "F.Ü - İİBF",
        "duyuru_url": "https://iibf.firat.edu.tr/announcements-all",
        "ana_url": "https://iibf.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Mühendislik Fakültesi",
        "duyuru_url": "https://muhendislikf.firat.edu.tr/announcements-all",
        "ana_url": "https://muhendislikf.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Teknoloji Fakültesi",
        "duyuru_url": "https://teknolojif.firat.edu.tr/announcements-all",
        "ana_url": "https://teknolojif.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Öğrenci DB",
        "duyuru_url": "https://ogrencidb.firat.edu.tr/announcements-all",
        "ana_url": "https://ogrencidb.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Öğrenci Dekanlığı",
        "duyuru_url": "https://ogrencidekanligi.firat.edu.tr/announcements-all",
        "ana_url": "https://ogrencidekanligi.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Yaz Okulu",
        "duyuru_url": "https://yazokuluyeni.firat.edu.tr/announcements-all",
        "ana_url": "https://yazokuluyeni.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Eğitim Fakültesi",
        "duyuru_url": "https://egitimf.firat.edu.tr/tr/announcements-all",
        "ana_url": "https://egitimf.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "fakulte": "F.Ü - Kütüphane DB",
        "duyuru_url": "https://kutuphanedb.firat.edu.tr/announcements-all",
        "ana_url": "https://kutuphanedb.firat.edu.tr",
        "link_selector": "div.other-news-card.mb-3 a[href*='announcements-detail']",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    }
]

KAYIT_DOSYASI = "seen_announcements.json"

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

def yuklenmis_duyurulari_al():
    if os.path.exists(KAYIT_DOSYASI):
        with open(KAYIT_DOSYASI, 'r') as f:
            return json.load(f)
    return {}

def kaydet(gorulenler):
    with open(KAYIT_DOSYASI, 'w') as f:
        json.dump(gorulenler, f)

def duyuru_kontrol():
    gorulenler = yuklenmis_duyurulari_al()
    for site in SITELER:
        try:
            response = requests.get(site['duyuru_url'], timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            duyurular = soup.select(site['link_selector'])
            if not duyurular:
                print(f"⚠️ {site['fakulte']} - Duyuru bulunamadı.")
                continue

            ilk_duyuru = duyurular[0]
            link = ilk_duyuru.get('href', '')
            if not link.startswith('http'):
                link = site['ana_url'].rstrip('/') + '/' + link.lstrip('/')

            if site['duyuru_url'] in gorulenler and gorulenler[site['duyuru_url']] == link:
                continue  # zaten gönderilmiş

            detay = requests.get(link, verify=False)
            detay_soup = BeautifulSoup(detay.text, 'html.parser')

            baslik_tag = detay_soup.select_one(site['baslik_selector'])
            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"

            tarih_tag = detay_soup.select_one(site['tarih_selector'])
            tarih = ''.join([s.strip() for s in tarih_tag.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '') if tarih_tag else "Tarih bulunamadı"

            mesaj = f"<b>{site['fakulte']}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            gorulenler[site['duyuru_url']] = link
            print(f"✅ Yeni duyuru gönderildi: {site['fakulte']}")
        except Exception as e:
            print(f"❌ HATA - {site['fakulte']}:", e)

    kaydet(gorulenler)

def donguyu_baslat():
    while True:
        duyuru_kontrol()
        time.sleep(CHECK_INTERVAL)

print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()

donguyu_baslat()
