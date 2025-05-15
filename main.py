import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
import time
import os
import re

TELEGRAM_BOT_TOKEN = '8075438517:AAH2V8mWVH9OY1qcj3QJ6CcwmERviQpGjuA'
CHAT_ID = '944442637'

DUYURU_SITELERI = [
    {
        "isim": "F.Ü - Ana Sayfa",
        "url": "https://www.firat.edu.tr/tr/page/announcement",
        "duyuru_link_selector": "div.card-body a",
        "baslik_selector": "h2.title",
        "tarih_selector": "div.date span"
    },
    {
        "isim": "F.Ü - İİBF",
        "url": "https://iibf.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Mühendislik Fakültesi",
        "url": "https://muhendislikf.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Teknoloji Fakültesi",
        "url": "https://teknolojif.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Öğrenci İşleri",
        "url": "https://ogrencidb.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Öğrenci Dekanlığı",
        "url": "https://ogrencidekanligi.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Yaz Okulu",
        "url": "https://yazokuluyeni.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Eğitim Fakültesi",
        "url": "https://egitimf.firat.edu.tr/tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
    {
        "isim": "F.Ü - Kütüphane",
        "url": "https://kutuphanedb.firat.edu.tr/announcements-all",
        "duyuru_link_selector": "div.other-news-card.mb-3 a",
        "baslik_selector": "div.new-section-detail-title h3",
        "tarih_selector": "div.new-section-detail-date p"
    },
]

app = Flask('')

@app.route('/')
def home():
    return "Bot çalışıyor."

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

def duyuru_takip():
    if not os.path.exists("kayitlar.txt"):
        with open("kayitlar.txt", "w") as f:
            f.write("")
    with open("kayitlar.txt", "r") as f:
        onceki_linkler = f.read().splitlines()

    yeni_linkler = []

    for site in DUYURU_SITELERI:
        try:
            response = requests.get(site['url'], timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            duyuru = soup.select_one(site['duyuru_link_selector'])
            if not duyuru:
                print(f"❌ Duyuru bulunamadı: {site['isim']}")
                continue

            link = duyuru.get('href')
            if not link.startswith('http'):
                base = site['url'].split('/announcements-all')[0]
                link = base + link if link.startswith('/') else base + '/' + link

            if link in onceki_linkler:
                continue  # zaten gönderilmiş

            detay = requests.get(link, verify=False)
            detay_soup = BeautifulSoup(detay.text, 'html.parser')

            baslik_tag = detay_soup.select_one(site['baslik_selector'])
            baslik = baslik_tag.get_text(strip=True) if baslik_tag else "Başlık bulunamadı"

            tarih_tag = detay_soup.select_one(site['tarih_selector'])
            if tarih_tag:
                tarih = ''.join([s.strip() for s in tarih_tag.contents if isinstance(s, str)]).replace('\n', '').replace(' ', '')
                tarih = re.sub(r'(\d{1,2})(\.)(\d{1,2})(\.)(\d{4})', r'\1.\3.\5', tarih)
            else:
                tarih = "Tarih bulunamadı"

            mesaj = f"<b>{site['isim']}</b>\n{baslik}\n📅 {tarih}"
            telegrama_gonder(mesaj, link)
            yeni_linkler.append(link)
            print(f"✅ Gönderildi: {site['isim']}")

        except Exception as e:
            print(f"⚠️ Hata ({site['isim']}):", e)

    if yeni_linkler:
        with open("kayitlar.txt", "a") as f:
            for link in yeni_linkler:
                f.write(link + "\n")

def donguyu_baslat():
    while True:
        duyuru_takip()
        time.sleep(120)

print("🚀 Bot başlatıldı.")
t = Thread(target=webserveri_baslat)
t.start()
d = Thread(target=donguyu_baslat)
d.start()
